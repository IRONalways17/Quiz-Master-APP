from flask import Blueprint, request, jsonify
from backend.app.database import db
from backend.app.models import Subject, Chapter, Quiz, Question, User
from backend.app.utils.auth import jwt_required_custom, get_jwt
from sqlalchemy import or_
from flask import jsonify
from backend.app.database import db
from celery_app import celery
from sqlalchemy import text

common_bp = Blueprint('common', __name__)

@common_bp.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check for all services"""
    health_status = {
        'status': 'healthy',
        'services': {},
        'timestamp': None
    }
    
    from datetime import datetime
    health_status['timestamp'] = datetime.utcnow().isoformat()
    
    # Test database connection
    try:
        db.session.execute(text('SELECT 1'))
        health_status['services']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['services']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Redis removed from health check
    
    # Test Celery connection
    try:
        # Test Celery broker connection
        celery.control.inspect().active()
        health_status['services']['celery'] = {
            'status': 'healthy',
            'message': 'Celery connection successful'
        }
    except Exception as e:
        health_status['services']['celery'] = {
            'status': 'warning',
            'message': f'Celery connection failed (normal in WSL2): {str(e)}'
        }
        # Don't mark overall status as unhealthy for Celery issues in WSL2
    
    return jsonify(health_status), 200 if health_status['status'] == 'healthy' else 503

@common_bp.route('/api/health', methods=['GET'])
def api_health():
    """Simple API health check"""
    from datetime import datetime
    return jsonify({
        'status': 'healthy',
        'message': 'Quiz Master V2 API is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@common_bp.route('/search', methods=['GET'])
@jwt_required_custom
def search():
    """Search across quizzes, subjects, and questions based on user role"""
    try:
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')  # all, quiz, subject, user
        
        if not query:
            return jsonify({
                'query': '',
                'results': {
                    'subjects': [],
                    'quizzes': [],
                    'users': []
                },
                'total_results': 0
            }), 200
        
        if len(query) < 2:
            return jsonify({'error': 'Search query must be at least 2 characters'}), 400
        
        claims = get_jwt()
        is_admin = claims.get('role') == 'admin'
        
        results = {
            'subjects': [],
            'quizzes': [],
            'users': []
        }
        
        # Search subjects
        if search_type in ['all', 'subject']:
            subjects = Subject.query.filter(
                Subject.is_active == True,
                or_(
                    Subject.name.ilike(f'%{query}%'),
                    Subject.code.ilike(f'%{query}%'),
                    Subject.description.ilike(f'%{query}%')
                )
            ).limit(10).all()
            results['subjects'] = [s.to_dict() for s in subjects]
        
        # Search quizzes
        if search_type in ['all', 'quiz']:
            quiz_query = Quiz.query.join(Chapter).join(Subject).filter(
                Quiz.is_active == True,
                or_(
                    Quiz.title.ilike(f'%{query}%'),
                    Quiz.description.ilike(f'%{query}%'),
                    Chapter.name.ilike(f'%{query}%'),
                    Subject.name.ilike(f'%{query}%')
                )
            )
            
            # For regular users, only show available quizzes
            if not is_admin:
                from datetime import datetime
                now = datetime.utcnow()
                quiz_query = quiz_query.filter(
                    Quiz.start_date <= now,
                    Quiz.end_date >= now
                )
            
            quizzes = quiz_query.limit(10).all()
            results['quizzes'] = [q.to_dict() for q in quizzes]
        
        # Search users (admin only)
        if is_admin and search_type in ['all', 'user']:
            users = User.query.filter(
                or_(
                    User.username.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%'),
                    User.full_name.ilike(f'%{query}%')
                )
            ).limit(10).all()
            results['users'] = [u.to_dict() for u in users]
        
        # Add questions count for admin
        if is_admin and search_type in ['all', 'question']:
            question_count = Question.query.filter(
                Question.is_active == True,
                Question.question_text.ilike(f'%{query}%')
            ).count()
            results['question_count'] = question_count
        
        return jsonify({
            'query': query,
            'results': results,
            'total_results': sum(len(v) if isinstance(v, list) else 0 for v in results.values())
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@common_bp.route('/leaderboard', methods=['GET'])
@jwt_required_custom
def global_leaderboard():
    """Get global leaderboard across all quizzes"""
    try:
        from backend.app.models import Score
        import json
        
        # Cache removed - fetch data directly
        
        # Get top performers based on average score
        top_performers = db.session.query(
            User.id,
            User.username,
            User.full_name,
            db.func.count(Score.id).label('total_quizzes'),
            db.func.avg(Score.percentage).label('avg_score'),
            db.func.sum(Score.passed).label('passed_count')
        ).join(
            Score, User.id == Score.user_id
        ).group_by(
            User.id, User.username, User.full_name
        ).having(
            db.func.count(Score.id) >= 3  # Minimum 3 quizzes attempted
        ).order_by(
            db.desc('avg_score')
        ).limit(20).all()
        
        leaderboard = []
        for idx, performer in enumerate(top_performers, 1):
            leaderboard.append({
                'rank': idx,
                'user_id': performer.id,
                'username': performer.username,
                'full_name': performer.full_name,
                'total_quizzes': performer.total_quizzes,
                'average_score': round(performer.avg_score, 2),
                'passed_count': performer.passed_count,
                'success_rate': round((performer.passed_count / performer.total_quizzes * 100), 2)
            })
        
        data = {'leaderboard': leaderboard}
        
        # Cache removed - return data directly
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@common_bp.route('/subjects/<int:subject_id>', methods=['GET'])
@jwt_required_custom
def get_subject_details(subject_id):
    """Get detailed subject information with chapters and quiz counts"""
    try:
        subject = Subject.query.get(subject_id)
        if not subject or not subject.is_active:
            return jsonify({'error': 'Subject not found'}), 404
        
        subject_data = subject.to_dict(include_chapters=True)
        
        # Add quiz counts for each chapter
        for chapter in subject_data['chapters']:
            quiz_count = Quiz.query.filter_by(
                chapter_id=chapter['id'],
                is_active=True
            ).count()
            chapter['quiz_count'] = quiz_count
        
        return jsonify(subject_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
