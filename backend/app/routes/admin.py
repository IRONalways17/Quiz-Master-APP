from flask import Blueprint, request, jsonify
from backend.app.database import db
from backend.app.models import User, Subject, Chapter, Quiz, Question, Score
from backend.app.utils.auth import admin_required
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__)

# Cache helper functions
def clear_cache_pattern(pattern):
    """Clear Redis cache by pattern with improved error handling"""
    try:
        # Redis temporarily disabled
        print(f"Cache clearing disabled for pattern: {pattern}")
        return 0
    except Exception as e:
        print(f"Cache clear error for pattern {pattern}: {e}")
        return 0

# User Management
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users with pagination and search"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.username.contains(search),
                    User.email.contains(search),
                    User.full_name.contains(search)
                )
            )
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Add quiz statistics to each user
        users_with_stats = []
        for user in pagination.items:
            user_dict = user.to_dict()
            # Add quiz count for this user
            quiz_count = Score.query.filter_by(user_id=user.id).count()
            user_dict['quizzes_taken'] = quiz_count
            users_with_stats.append(user_dict)
        
        return jsonify({
            'users': users_with_stats,
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_details(user_id):
    """Get individual user details"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's quiz statistics
        total_quizzes = Score.query.filter_by(user_id=user_id).count()
        
        # Get average score
        scores = Score.query.filter_by(user_id=user_id).all()
        avg_score = 0
        if scores:
            total_score = sum(score.score for score in scores)
            total_possible = sum(score.max_score for score in scores)
            avg_score = round((total_score / total_possible * 100), 2) if total_possible > 0 else 0
        
        # Get recent activity (last 5 quizzes)
        recent_scores = Score.query.filter_by(user_id=user_id).order_by(Score.completed_at.desc()).limit(5).all()
        recent_activity = []
        for score in recent_scores:
            quiz = Quiz.query.get(score.quiz_id)
            if quiz:
                recent_activity.append({
                    'quiz_title': quiz.title,
                    'score': score.score,
                    'total_questions': score.max_score,
                    'completed_at': score.completed_at.isoformat() if score.completed_at else None
                })
        
        user_data = user.to_dict()
        user_data.update({
            'statistics': {
                'total_quizzes_taken': total_quizzes,
                'average_score_percentage': avg_score,
                'recent_activity': recent_activity
            }
        })
        
        return jsonify({'user': user_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/history', methods=['GET'])
@admin_required
def get_user_history(user_id):
    """Get user's quiz history"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's quiz scores with related data
        scores = Score.query.filter_by(user_id=user_id).order_by(Score.completed_at.desc()).all()
        
        history = []
        for score in scores:
            quiz = Quiz.query.get(score.quiz_id)
            if quiz:
                chapter = Chapter.query.get(quiz.chapter_id)
                subject = Subject.query.get(chapter.subject_id) if chapter else None
                
                history.append({
                    'id': score.id,
                    'quiz_title': quiz.title,
                    'quiz_id': quiz.id,
                    'chapter_name': chapter.name if chapter else 'Unknown',
                    'subject_name': subject.name if subject else 'Unknown',
                    'score': score.score,
                    'total_questions': score.max_score,
                    'percentage': score.percentage,
                    'completed_at': score.completed_at.isoformat() if score.completed_at else None,
                    'time_taken': score.time_taken_seconds,
                    'passed': score.passed
                })
        
        return jsonify({
            'history': history,
            'total_quizzes': len(history),
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user account"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deleting admin users (optional safety check)
        if user.role == 'admin':
            return jsonify({'error': 'Cannot delete admin users'}), 403
        
        # Get user stats before deletion
        user_scores_count = Score.query.filter_by(user_id=user_id).count()
        user_info = user.to_dict()
        
        # Delete user (cascade will handle related records)
        db.session.delete(user)
        db.session.commit()
        
        # Clear related cache
        clear_cache_pattern(f'user:{user_id}:*')
        clear_cache_pattern('users:*')
        
        return jsonify({
            'message': f'User "{user_info["full_name"]}" deleted successfully',
            'deleted_user': user_info,
            'deleted_quiz_records': user_scores_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST', 'PUT'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/export', methods=['POST'])
@admin_required  
def export_users():
    """Export users to CSV"""
    try:
        users = User.query.all()
        
        # Create CSV data
        csv_data = []
        csv_data.append(['ID', 'Username', 'Email', 'Full Name', 'Qualification', 'Role', 'Status', 'Created At', 'Last Login'])
        
        for user in users:
            csv_data.append([
                user.id,
                user.username,
                user.email,
                user.full_name,
                user.qualification or '',
                user.role,
                'Active' if user.is_active else 'Inactive',
                user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ''
            ])
        
        return jsonify({
            'message': 'Users exported successfully',
            'csv_data': csv_data,
            'filename': f'users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            'total_users': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to export users: {str(e)}'}), 500

# Subject Management
@admin_bp.route('/subjects', methods=['GET'])
@admin_required
def get_subjects():
    """Get all subjects"""
    try:
        subjects = Subject.query.filter_by(is_active=True).all()
        return jsonify({
            'subjects': [subject.to_dict(include_chapters=True) for subject in subjects]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subjects', methods=['POST'])
@admin_required
def create_subject():
    """Create a new subject"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('code'):
            return jsonify({'error': 'Name and code are required'}), 400
        
        # Check if code already exists
        if Subject.query.filter_by(code=data['code']).first():
            return jsonify({'error': 'Subject code already exists'}), 409
        
        subject = Subject(
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
            color=data.get('color', '#3498db'),
            icon=data.get('icon', 'book')
        )
        
        db.session.add(subject)
        db.session.commit()
        
        # Clear cache
        clear_cache_pattern('subjects:*')
        
        return jsonify({
            'message': 'Subject created successfully',
            'subject': subject.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subjects/<int:subject_id>', methods=['GET'])
@admin_required
def get_subject(subject_id):
    """Get a specific subject"""
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        return jsonify({
            'subject': subject.to_dict(include_chapters=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@admin_required
def update_subject(subject_id):
    """Update a subject"""
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            subject.name = data['name']
        if 'code' in data:
            # Check if code already exists for another subject
            existing_subject = Subject.query.filter_by(code=data['code']).first()
            if existing_subject and existing_subject.id != subject_id:
                return jsonify({'error': 'Subject code already exists'}), 400
            subject.code = data['code']
        if 'description' in data:
            subject.description = data['description']
        if 'color' in data:
            subject.color = data['color']
        if 'icon' in data:
            subject.icon = data['icon']
        
        subject.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Clear cache
        clear_cache_pattern('subjects:*')
        
        return jsonify({
            'message': 'Subject updated successfully',
            'subject': subject.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id):
    """Delete a subject (soft delete)"""
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        subject.is_active = False
        db.session.commit()
        
        # Clear cache
        clear_cache_pattern('subjects:*')
        
        return jsonify({'message': 'Subject deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Chapter Management
@admin_bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
@admin_required
def get_subject_chapters(subject_id):
    """Get all chapters for a subject"""
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        chapters = Chapter.query.filter_by(
            subject_id=subject_id,
            is_active=True
        ).order_by(Chapter.chapter_number).all()
        
        # Add debug information
        print(f"Found {len(chapters)} chapters for subject {subject_id}")
        for chapter in chapters:
            print(f"Chapter: {chapter.name}, ID: {chapter.id}, Number: {chapter.chapter_number}")
        
        return jsonify({
            'subject': subject.to_dict(),
            'chapters': [chapter.to_dict() for chapter in chapters]
        }), 200
        
    except Exception as e:
        print(f"Error getting chapters: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/chapters/check-duplicates', methods=['GET'])
@admin_required
def check_duplicate_chapters():
    """Check for duplicate chapter names across subjects"""
    duplicates = Chapter.get_duplicate_names()
    
    duplicate_details = []
    for duplicate in duplicates:
        chapters = Chapter.query.filter_by(name=duplicate['name'], is_active=True).all()
        subjects_info = [{
            'chapter_id': chapter.id,
            'chapter_slug': chapter.slug,
            'subject_name': chapter.subject.name if chapter.subject else None,
            'subject_slug': chapter.subject.slug if chapter.subject else None,
            'subject_id': chapter.subject_id
        } for chapter in chapters]
        
        duplicate_details.append({
            'chapter_name': duplicate['name'],
            'subject_count': duplicate['subject_count'],
            'subjects': subjects_info
        })
    
    return jsonify({
        'duplicates': duplicate_details,
        'total_duplicates': len(duplicate_details),
        'message': 'Duplicate chapters can cause navigation issues'
    })

@admin_bp.route('/chapters', methods=['GET'])
@admin_required
def get_all_chapters():
    """Get all chapters grouped by subject"""
    chapters = Chapter.query.filter_by(is_active=True).order_by(
        Chapter.subject_id, Chapter.chapter_number
    ).all()
    
    chapters_by_subject = {}
    for chapter in chapters:
        subject_id = chapter.subject_id
        if subject_id not in chapters_by_subject:
            chapters_by_subject[subject_id] = []
        chapters_by_subject[subject_id].append(chapter.to_dict())
    
    duplicates = Chapter.get_duplicate_names()
    
    return jsonify({
        'chapters_by_subject': chapters_by_subject,
        'total_chapters': len(chapters),
        'duplicate_names': len(duplicates),
        'duplicates_summary': duplicates
    })

@admin_bp.route('/chapters', methods=['POST'])
@admin_required
def create_chapter():
    """Create a new chapter"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'subject_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if subject exists
        subject = Subject.query.get(data['subject_id'])
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Auto-generate chapter number if not provided
        if 'chapter_number' not in data or data['chapter_number'] is None:
            # Get the highest chapter number for this subject and add 1
            max_chapter = Chapter.query.filter_by(subject_id=data['subject_id']).order_by(Chapter.chapter_number.desc()).first()
            data['chapter_number'] = (max_chapter.chapter_number + 1) if max_chapter else 1
            print(f"Auto-generated chapter number: {data['chapter_number']} for subject {data['subject_id']}")
        
        # Check if chapter number already exists for this subject
        existing_chapter = Chapter.query.filter_by(
            subject_id=data['subject_id'], 
            chapter_number=data['chapter_number']
        ).first()
        
        if existing_chapter:
            return jsonify({'error': f'Chapter number {data["chapter_number"]} already exists for this subject'}), 400
        
        chapter = Chapter(
            name=data['name'],
            chapter_number=data['chapter_number'],
            description=data.get('description', ''),
            subject_id=data['subject_id']
        )
        
        db.session.add(chapter)
        db.session.commit()
        
        print(f"Chapter created successfully: {chapter.name}, ID: {chapter.id}, Number: {chapter.chapter_number}")
        
        # Clear cache
        clear_cache_pattern(f'subject:{data["subject_id"]}:*')
        
        return jsonify({
            'message': 'Chapter created successfully',
            'chapter': chapter.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
@admin_required
def update_chapter(chapter_id):
    """Update a chapter"""
    try:
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({'error': 'Chapter not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            chapter.name = data['name']
        if 'chapter_number' in data:
            chapter.chapter_number = data['chapter_number']
        if 'description' in data:
            chapter.description = data['description']
        
        chapter.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Clear cache
        clear_cache_pattern(f'subject:{chapter.subject_id}:*')
        
        return jsonify({
            'message': 'Chapter updated successfully',
            'chapter': chapter.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@admin_required
def delete_chapter(chapter_id):
    """Delete a chapter (soft delete)"""
    try:
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({'error': 'Chapter not found'}), 404
        
        chapter.is_active = False
        db.session.commit()
        
        # Clear cache
        clear_cache_pattern(f'subject:{chapter.subject_id}:*')
        
        return jsonify({'message': 'Chapter deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Quiz Management
@admin_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@admin_required
def get_chapter_quizzes(chapter_id):
    """Get all quizzes for a chapter"""
    try:
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({'error': 'Chapter not found'}), 404
        
        quizzes = Quiz.query.filter_by(
            chapter_id=chapter_id,
            is_active=True
        ).order_by(Quiz.created_at.desc()).all()
        
        return jsonify({
            'chapter': chapter.to_dict(),
            'subject': chapter.subject.to_dict(),
            'quizzes': [quiz.to_dict() for quiz in quizzes]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/quizzes', methods=['GET'])
@admin_required
def get_quizzes():
    """Get all quizzes with filters"""
    try:
        subject_id = request.args.get('subject_id', type=int)
        chapter_id = request.args.get('chapter_id', type=int)
        status = request.args.get('status')
        
        query = Quiz.query
        
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)
        elif subject_id:
            query = query.join(Chapter).filter(Chapter.subject_id == subject_id)
        
        quizzes = query.filter_by(is_active=True).all()
        
        # Filter by status if provided
        if status:
            quizzes = [q for q in quizzes if q.status == status]
        
        return jsonify({
            'quizzes': [quiz.to_dict() for quiz in quizzes]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/quizzes', methods=['POST'])
@admin_required
def create_quiz():
    """Create a new quiz"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'chapter_id', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if chapter exists
        chapter = Chapter.query.get(data['chapter_id'])
        if not chapter:
            return jsonify({'error': 'Chapter not found'}), 404
        
        # Parse dates
        start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        
        if start_date >= end_date:
            return jsonify({'error': 'End date must be after start date'}), 400
        
        quiz = Quiz(
            title=data['title'],
            description=data.get('description', ''),
            chapter_id=data['chapter_id'],
            duration_minutes=data.get('duration_minutes', 30),
            passing_score=data.get('passing_score', 60),
            max_attempts=data.get('max_attempts', 3),
            start_date=start_date,
            end_date=end_date
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        # Clear cache
        clear_cache_pattern(f'chapter:{data["chapter_id"]}:*')
        clear_cache_pattern('quizzes:*')
        
        return jsonify({
            'message': 'Quiz created successfully',
            'quiz': quiz.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@admin_required
def get_quiz(quiz_id):
    """Get a single quiz by ID"""
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        return jsonify({
            'quiz': quiz.to_dict(),
            'chapter': quiz.chapter.to_dict(),
            'subject': quiz.chapter.subject.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@admin_required
def update_quiz(quiz_id):
    """Update a quiz"""
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            quiz.title = data['title']
        if 'description' in data:
            quiz.description = data['description']
        if 'duration_minutes' in data:
            quiz.duration_minutes = data['duration_minutes']
        if 'passing_score' in data:
            quiz.passing_score = data['passing_score']
        if 'max_attempts' in data:
            quiz.max_attempts = data['max_attempts']
        if 'start_date' in data:
            quiz.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        if 'end_date' in data:
            quiz.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        
        quiz.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Clear cache
        clear_cache_pattern(f'quiz:{quiz_id}:*')
        clear_cache_pattern(f'chapter:{quiz.chapter_id}:*')
        
        return jsonify({
            'message': 'Quiz updated successfully',
            'quiz': quiz.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@admin_required
def delete_quiz(quiz_id):
    """Delete a quiz (soft delete)"""
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        quiz.is_active = False
        db.session.commit()
        
        # Clear cache
        clear_cache_pattern(f'quiz:{quiz_id}:*')
        clear_cache_pattern(f'chapter:{quiz.chapter_id}:*')
        
        return jsonify({'message': 'Quiz deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Question Management
@admin_bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET'])
@admin_required
def get_quiz_questions(quiz_id):
    """Get all questions for a quiz"""
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        questions = Question.query.filter_by(
            quiz_id=quiz_id,
            is_active=True
        ).order_by(Question.order).all()
        
        return jsonify({
            'quiz': quiz.to_dict(),
            'chapter': quiz.chapter.to_dict(),
            'subject': quiz.chapter.subject.to_dict(),
            'questions': [q.to_dict() for q in questions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/questions/<int:quiz_id>', methods=['GET'])
@admin_required
def get_questions(quiz_id):
    """Get all questions for a quiz"""
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        questions = Question.query.filter_by(
            quiz_id=quiz_id,
            is_active=True
        ).order_by(Question.order).all()
        
        return jsonify({
            'questions': [q.to_dict() for q in questions],
            'quiz': quiz.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/questions', methods=['POST'])
@admin_required
def create_question():
    """Create a new question"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['quiz_id', 'question_text', 'options', 'correct_answer']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if quiz exists
        quiz = Quiz.query.get(data['quiz_id'])
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Get the next order number
        max_order = db.session.query(db.func.max(Question.order)).filter_by(
            quiz_id=data['quiz_id']
        ).scalar() or 0
        
        question = Question(
            quiz_id=data['quiz_id'],
            question_text=data['question_text'],
            question_type=data.get('question_type', 'multiple_choice'),
            points=data.get('points', 1),
            correct_answer=str(data['correct_answer']),
            explanation=data.get('explanation', ''),
            order=max_order + 1
        )
        
        # Set options
        question.set_options(data['options'])
        
        db.session.add(question)
        db.session.commit()
        
        # Clear cache
        clear_cache_pattern(f'quiz:{data["quiz_id"]}:*')
        
        return jsonify({
            'message': 'Question created successfully',
            'question': question.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/questions/<int:question_id>', methods=['PUT'])
@admin_required
def update_question(question_id):
    """Update a question"""
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'question_text' in data:
            question.question_text = data['question_text']
        if 'question_type' in data:
            question.question_type = data['question_type']
        if 'points' in data:
            question.points = data['points']
        if 'options' in data:
            question.set_options(data['options'])
        if 'correct_answer' in data:
            question.correct_answer = str(data['correct_answer'])
        if 'explanation' in data:
            question.explanation = data['explanation']
        if 'order' in data:
            question.order = data['order']
        
        question.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Clear cache
        clear_cache_pattern(f'quiz:{question.quiz_id}:*')
        
        return jsonify({
            'message': 'Question updated successfully',
            'question': question.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@admin_required
def delete_question(question_id):
    """Delete a question (soft delete)"""
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        question.is_active = False
        db.session.commit()
        
        # Clear cache
        clear_cache_pattern(f'quiz:{question.quiz_id}:*')
        
        return jsonify({'message': 'Question deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Dashboard Statistics
@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Check cache first
        cache_key = 'admin:dashboard:stats'
        cached = #redis_client.get(cache_key)
        if cached:
            return jsonify(json.loads(cached)), 200
        
        # Basic stats
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_subjects': Subject.query.filter_by(is_active=True).count(),
            'total_quizzes': Quiz.query.filter_by(is_active=True).count(),
            'active_quizzes': Quiz.query.filter_by(is_active=True).filter(
                Quiz.start_date <= datetime.utcnow(),
                Quiz.end_date >= datetime.utcnow()
            ).count(),
            'total_questions': Question.query.filter_by(is_active=True).count()
        }
        
        # Quiz distribution by subject
        quiz_distribution = db.session.query(
            Subject.name,
            db.func.count(Quiz.id).label('quiz_count')
        ).select_from(Subject).outerjoin(Chapter).outerjoin(Quiz).filter(
            Subject.is_active == True,
            Quiz.is_active == True
        ).group_by(Subject.id, Subject.name).all()
        
        # Convert to chart format
        distribution_data = {
            'labels': [item.name for item in quiz_distribution],
            'data': [item.quiz_count for item in quiz_distribution],
            'colors': [
                '#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#6b7280',
                '#8b5cf6', '#06b6d4', '#84cc16', '#f97316', '#ec4899'
            ]
        }
        
        # If no subjects have quizzes, show a default message
        if not distribution_data['labels']:
            distribution_data = {
                'labels': ['No Quizzes Yet'],
                'data': [1],
                'colors': ['#6b7280']
            }
        
        stats['quiz_distribution'] = distribution_data
        
        # Quiz activity trend (last 7 days)
        today = datetime.now().date()
        activity_data = []
        activity_labels = []
        
        for i in range(6, -1, -1):  # Last 7 days
            day_date = today - timedelta(days=i)
            day_start = datetime.combine(day_date, datetime.min.time())
            day_end = datetime.combine(day_date, datetime.max.time())
            
            # Count quiz attempts (scores) for this day
            attempts = Score.query.filter(
                Score.completed_at >= day_start,
                Score.completed_at <= day_end
            ).count()
            
            activity_data.append(attempts)
            activity_labels.append(day_date.strftime('%a'))  # Mon, Tue, etc.
        
        stats['activity_trend'] = {
            'labels': activity_labels,
            'data': activity_data
        }
        
        # Cache for 5 minutes
        #redis_client.setex(cache_key, 300, json.dumps(stats))
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/search', methods=['GET'])
@admin_required
def search():
    """Search across subjects, quizzes, and users"""
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')
        
        if not query:
            return jsonify({
                'subjects': [],
                'quizzes': [],
                'users': []
            }), 200
        
        results = {
            'subjects': [],
            'quizzes': [],
            'users': []
        }
        
        # Search subjects
        if search_type in ['all', 'subjects']:
            subjects = Subject.query.filter(
                db.or_(
                    Subject.name.contains(query),
                    Subject.code.contains(query),
                    Subject.description.contains(query)
                ),
                Subject.is_active == True
            ).all()
            results['subjects'] = [subject.to_dict() for subject in subjects]
        
        # Search quizzes
        if search_type in ['all', 'quizzes']:
            quizzes = Quiz.query.join(Chapter).join(Subject).filter(
                db.or_(
                    Quiz.title.contains(query),
                    Quiz.description.contains(query),
                    Chapter.name.contains(query),
                    Subject.name.contains(query)
                ),
                Quiz.is_active == True
            ).all()
            results['quizzes'] = [quiz.to_dict() for quiz in quizzes]
        
        # Search users
        if search_type in ['all', 'users']:
            users = User.query.filter(
                db.or_(
                    User.username.contains(query),
                    User.email.contains(query),
                    User.full_name.contains(query)
                )
            ).all()
            results['users'] = [user.to_dict() for user in users]
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/cache/stats', methods=['GET'])
@admin_required
def get_cache_stats():
    """Get Redis cache statistics"""
    try:
        # Redis temporarily disabled
        return jsonify({'error': 'Redis cache is temporarily disabled'}), 503
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Temporarily disable cache routes
"""
@admin_bp.route('/cache/clear', methods=['POST'])
@admin_required  
def clear_cache():
    """Clear cache by pattern or all cache"""
    try:
        data = request.get_json() or {}
        pattern = data.get('pattern', '*')
        
        if not #redis_client:
            return jsonify({'error': 'Redis not configured'}), 500
        
        # Safety check for clearing all cache
        if pattern == '*':
            if not data.get('confirm_clear_all'):
                return jsonify({
                    'error': 'Clearing all cache requires confirmation',
                    'required_field': 'confirm_clear_all: true'
                }), 400
        
        # Clear cache by pattern
        keys = list(#redis_client.scan_iter(match=pattern))
        deleted_count = 0
        
        for key in keys:
            #redis_client.delete(key)
            deleted_count += 1
        
        return jsonify({
            'message': f'Cleared {deleted_count} cache keys',
            'pattern': pattern,
            'deleted_keys': deleted_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
""" 
