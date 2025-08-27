from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Subject, Chapter, Quiz, Score, Reminder, User
from app.utils.auth import user_required, get_current_user_id
from app import redis_client
import json
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/recent-activity', methods=['GET'])
@user_required
def get_recent_activity():
    """Get user's recent quiz activity with detailed information"""
    try:
        user_id = get_current_user_id()
        
        # Get recent scores with quiz and subject information
        recent_scores = db.session.query(Score).join(Quiz).join(Chapter).join(Subject).filter(
            Score.user_id == user_id
        ).order_by(Score.created_at.desc()).limit(10).all()
        
        activities = []
        for score in recent_scores:
            # Determine activity type based on score
            if score.percentage >= 90:
                activity_type = 'excellent_score'
                type_label = 'Excellent Performance'
            elif score.percentage >= 80:
                activity_type = 'good_score'
                type_label = 'Good Performance'
            elif score.percentage >= 70:
                activity_type = 'average_score'
                type_label = 'Average Performance'
            else:
                activity_type = 'needs_improvement'
                type_label = 'Needs Improvement'
            
            activities.append({
                'id': score.id,
                'type': activity_type,
                'title': f"{score.quiz.title}",
                'description': f"Completed {score.quiz.title} in {score.quiz.chapter.subject.name} - {score.quiz.chapter.name}",
                'score': score.percentage,
                'score_text': f"{score.score}/{score.max_score}",
                'type_label': type_label,
                'subject_name': score.quiz.chapter.subject.name,
                'chapter_name': score.quiz.chapter.name,
                'quiz_title': score.quiz.title,
                'created_at': score.created_at.isoformat(),
                'quiz_id': score.quiz_id,
                'passed': score.passed,
                'time_taken': score.time_taken_seconds
            })
        
        return jsonify({'activities': activities}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/subjects', methods=['GET'])
@user_required
def get_subjects():
    """Get all active subjects"""
    subjects = Subject.query.filter_by(is_active=True).all()
    data = {'subjects': [subject.to_dict(include_chapters=True) for subject in subjects]}
    return jsonify(data)

@user_bp.route('/subjects/<string:subject_slug>/chapters', methods=['GET'])
@user_required
def get_subject_chapters_by_slug(subject_slug):
    """Get chapters for a subject"""
    subject = Subject.query.filter_by(slug=subject_slug, is_active=True).first()
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404
    
    chapters = Chapter.query.filter_by(
        subject_id=subject.id, 
        is_active=True
    ).order_by(Chapter.chapter_number).all()
    
    return jsonify({
        'subject': subject.to_dict(),
        'chapters': [chapter.to_dict() for chapter in chapters]
    })

@user_bp.route('/subjects/<string:subject_slug>/chapters/<string:chapter_slug>/quizzes', methods=['GET'])
@user_required
def get_chapter_quizzes_by_subject_and_chapter_slug(subject_slug, chapter_slug):
    """Get quizzes for a specific chapter"""
    user_id = get_current_user_id()
    
    subject = Subject.query.filter_by(slug=subject_slug, is_active=True).first()
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404
    
    chapter = Chapter.query.filter_by(
        slug=chapter_slug, 
        subject_id=subject.id,
        is_active=True
    ).first()
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    quizzes = Quiz.query.filter_by(chapter_id=chapter.id, is_active=True).all()
    quiz_data = []
    
    for quiz in quizzes:
        attempts = Score.query.filter_by(user_id=user_id, quiz_id=quiz.id).all()
        quiz_dict = quiz.to_dict()
        quiz_dict.update({
            'user_attempts': len(attempts),
            'best_score': max([s.percentage for s in attempts]) if attempts else None,
            'can_attempt': quiz.is_available and len(attempts) < quiz.max_attempts
        })
        quiz_data.append(quiz_dict)
    
    return jsonify({
        'subject': subject.to_dict(),
        'chapter': chapter.to_dict(),
        'quizzes': quiz_data
    })

@user_bp.route('/chapters/<string:chapter_slug>/quizzes', methods=['GET'])
@user_required
def get_chapter_quizzes_by_slug(chapter_slug):
    """Get quizzes for a chapter by slug - handles duplicate names"""
    user_id = get_current_user_id()
    
    chapters = Chapter.query.filter_by(slug=chapter_slug, is_active=True).all()
    if len(chapters) > 1:
        return jsonify({
            'error': 'Multiple chapters found with same name',
            'suggestion': 'Use /subjects/{subject_slug}/chapters/{chapter_slug}/quizzes',
            'options': [{
                'chapter_name': ch.name,
                'subject_name': ch.subject.name,
                'full_path': f'/subjects/{ch.subject.slug}/chapters/{ch.slug}/quizzes'
            } for ch in chapters]
        }), 400
    
    if not chapters:
        return jsonify({'error': 'Chapter not found'}), 404
    
    chapter = chapters[0]
    quizzes = Quiz.query.filter_by(chapter_id=chapter.id, is_active=True).all()
    quiz_data = []
    
    for quiz in quizzes:
        attempts = Score.query.filter_by(user_id=user_id, quiz_id=quiz.id).all()
        quiz_dict = quiz.to_dict()
        quiz_dict.update({
            'user_attempts': len(attempts),
            'best_score': max([s.percentage for s in attempts]) if attempts else None,
            'can_attempt': quiz.is_available and len(attempts) < quiz.max_attempts
        })
        quiz_data.append(quiz_dict)
    
    return jsonify({
        'chapter': chapter.to_dict(),
        'quizzes': quiz_data
    })

@user_bp.route('/quizzes/<int:quiz_id>/info', methods=['GET'])
@user_required
def get_quiz_info_by_id(quiz_id):
    """Get quiz information by ID"""
    user_id = get_current_user_id()
    quiz = Quiz.query.filter_by(id=quiz_id, is_active=True).first()
    
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    if not quiz.is_available:
        return jsonify({'error': 'Quiz not available', 'status': quiz.status}), 403
    
    attempts = Score.query.filter_by(user_id=user_id, quiz_id=quiz.id).all()
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id) if chapter else None
    
    quiz_info = quiz.to_dict()
    quiz_info.update({
        'attempts_made': len(attempts),
        'attempts_remaining': quiz.max_attempts - len(attempts) if quiz.max_attempts else float('inf'),
        'can_attempt': quiz.max_attempts is None or len(attempts) < quiz.max_attempts,
        'chapter': chapter.to_dict() if chapter else None,
        'subject': subject.to_dict() if subject else None,
        'previous_scores': [{
            'attempt': idx + 1,
            'score': attempt.score,
            'total_questions': attempt.max_score,
            'percentage': attempt.percentage,
            'passed': attempt.passed,
            'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
            'time_taken': attempt.time_taken_seconds
        } for idx, attempt in enumerate(attempts)]
    })
    
    return jsonify(quiz_info)

@user_bp.route('/quizzes/<string:quiz_slug>/info', methods=['GET'])
@user_required
def get_quiz_info_by_slug(quiz_slug):
    """Get quiz information by slug"""
    user_id = get_current_user_id()
    quiz = Quiz.query.filter_by(slug=quiz_slug, is_active=True).first()
    
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    if not quiz.is_available:
        return jsonify({'error': 'Quiz not available', 'status': quiz.status}), 403
    
    attempts = Score.query.filter_by(user_id=user_id, quiz_id=quiz.id).all()
    quiz_info = quiz.to_dict()
    quiz_info.update({
        'attempts_made': len(attempts),
        'attempts_remaining': quiz.max_attempts - len(attempts),
        'can_attempt': len(attempts) < quiz.max_attempts,
        'previous_scores': [{
            'attempt': a.attempt_number,
            'score': a.percentage,
            'passed': a.passed,
            'date': a.created_at.isoformat()
        } for a in attempts]
    })
    
    return jsonify(quiz_info)

@user_bp.route('/available-quizzes', methods=['GET'])
@user_required
def get_user_available_quizzes():
    """Get available quizzes for user"""
    user_id = get_current_user_id()
    
    cache_key = f'user:{user_id}:available_quizzes'
    if redis_client:
        cached = redis_client.get(cache_key)
        if cached:
            return jsonify(json.loads(cached))
    
    quizzes = Quiz.query.filter_by(is_active=True).all()
    available_quizzes = []
    
    for quiz in quizzes:
        if not quiz.is_available:
            continue
            
        attempts = Score.query.filter_by(user_id=user_id, quiz_id=quiz.id).all()
        if len(attempts) >= quiz.max_attempts:
            continue
            
        quiz_dict = quiz.to_dict()
        quiz_dict.update({
            'user_attempts': len(attempts),
            'best_score': max([s.percentage for s in attempts]) if attempts else None,
            'can_attempt': True
        })
        available_quizzes.append(quiz_dict)
    
    data = {'quizzes': available_quizzes}
    if redis_client:
        redis_client.setex(cache_key, 300, json.dumps(data))
    
    return jsonify(data)

@user_bp.route('/scores', methods=['GET'])
@user_required
def get_user_scores():
    """Get user scores with pagination"""
    user_id = get_current_user_id()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = Score.query.filter_by(user_id=user_id).order_by(
        Score.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'scores': [score.to_dict() for score in pagination.items],
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages
    })

@user_bp.route('/scores/<int:score_id>', methods=['GET'])
@user_required
def get_score_details(score_id):
    """Get detailed score information"""
    user_id = get_current_user_id()
    score = Score.query.filter_by(id=score_id, user_id=user_id).first()
    
    if not score:
        return jsonify({'error': 'Score not found'}), 404
    
    score_data = score.to_dict_with_details()
    quiz = Quiz.query.get(score.quiz_id)
    
    if quiz:
        correct_answers = {}
        question_texts = {}
        answer_map = {'0': 'A', '1': 'B', '2': 'C', '3': 'D'}
        
        for question in quiz.questions:
            if question.is_active:
                correct_answers[str(question.id)] = answer_map.get(
                    str(question.correct_answer), 
                    question.correct_answer
                )
                question_texts[str(question.id)] = question.question_text
        
        score_data.update({
            'correct_answers': correct_answers,
            'question_texts': question_texts
        })
    
    return jsonify({'score': score_data})

@user_bp.route('/leaderboard', methods=['GET'])
@user_required
def get_leaderboard():
    """Get global leaderboard"""
    try:
        # Get top performers
        top_scores = db.session.query(
            User.full_name,
            User.email,
            db.func.count(Score.id).label('total_attempts'),
            db.func.avg(Score.percentage).label('average_score'),
            db.func.sum(db.case((Score.passed == True, 1), else_=0)).label('passed_attempts')
        ).join(Score, User.id == Score.user_id)\
         .group_by(User.id, User.full_name, User.email)\
         .having(db.func.count(Score.id) >= 1)\
         .order_by(db.func.avg(Score.percentage).desc())\
         .limit(20).all()
        
        leaderboard = []
        for i, (full_name, email, total_attempts, avg_score, passed_attempts) in enumerate(top_scores, 1):
            leaderboard.append({
                'rank': i,
                'full_name': full_name or 'Anonymous',
                'email': email,
                'total_attempts': total_attempts,
                'average_score': round(avg_score, 2),
                'passed_attempts': passed_attempts,
                'pass_rate': round((passed_attempts / total_attempts * 100) if total_attempts > 0 else 0, 2)
            })
        
        return jsonify({
            'leaderboard': leaderboard
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/leaderboard/subject/<int:subject_id>', methods=['GET'])
@user_required
def get_subject_leaderboard(subject_id):
    """Get leaderboard for a specific subject"""
    try:
        # Get top performers for specific subject
        top_scores = db.session.query(
            User.full_name,
            User.email,
            db.func.count(Score.id).label('total_attempts'),
            db.func.avg(Score.percentage).label('average_score'),
            db.func.sum(db.case((Score.passed == True, 1), else_=0)).label('passed_attempts')
        ).join(Score, User.id == Score.user_id)\
         .join(Quiz, Score.quiz_id == Quiz.id)\
         .join(Chapter, Quiz.chapter_id == Chapter.id)\
         .filter(Chapter.subject_id == subject_id)\
         .group_by(User.id, User.full_name, User.email)\
         .having(db.func.count(Score.id) >= 1)\
         .order_by(db.func.avg(Score.percentage).desc())\
         .limit(20).all()
        
        leaderboard = []
        for i, (full_name, email, total_attempts, avg_score, passed_attempts) in enumerate(top_scores, 1):
            leaderboard.append({
                'rank': i,
                'full_name': full_name or 'Anonymous',
                'email': email,
                'total_attempts': total_attempts,
                'average_score': round(avg_score, 2),
                'passed_attempts': passed_attempts,
                'pass_rate': round((passed_attempts / total_attempts * 100) if total_attempts > 0 else 0, 2)
            })
        
        return jsonify({
            'leaderboard': leaderboard
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/export/scores', methods=['POST'])
@user_required
def export_scores():
    """Trigger CSV export for user scores"""
    try:
        from celery_tasks.tasks import export_user_scores_csv
        
        user_id = get_current_user_id()
        
        # Trigger async export
        task = export_user_scores_csv.delay(user_id)
        
        return jsonify({
            'message': 'Export started',
            'task_id': task.id
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/export/status/<string:task_id>', methods=['GET'])
@user_required
def get_export_status(task_id):
    """Get export task status"""
    try:
        from celery_tasks.tasks import export_user_scores_csv
        
        task = export_user_scores_csv.AsyncResult(task_id)
        
        if task.ready():
            if task.successful():
                result = task.result
                return jsonify({
                    'status': 'completed',
                    'download_url': result.get('download_url'),
                    'filename': result.get('filename')
                }), 200
            else:
                return jsonify({
                    'status': 'failed',
                    'error': str(task.result)
                }), 500
        else:
            return jsonify({
                'status': 'processing',
                'progress': task.info.get('progress', 0) if task.info else 0
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/dashboard/stats', methods=['GET'])
@user_required
def get_user_stats():
    """Get user's dashboard statistics"""
    try:
        user_id = get_current_user_id()
        
        # Cache key specific to user
        cache_key = f'user:{user_id}:dashboard:stats'
        cached = redis_client.get(cache_key) if redis_client else None
        if cached:
            return jsonify(json.loads(cached)), 200
        
        # Calculate statistics
        total_attempts = Score.query.filter_by(user_id=user_id).count()
        passed_attempts = Score.query.filter_by(user_id=user_id, passed=True).count()
        
        # Get unique quizzes attempted
        unique_quizzes = db.session.query(Score.quiz_id).filter_by(
            user_id=user_id
        ).distinct().count()
        
        # Get average score
        avg_score = db.session.query(db.func.avg(Score.percentage)).filter_by(
            user_id=user_id
        ).scalar() or 0
        
        # Get recent scores
        recent_scores = Score.query.filter_by(
            user_id=user_id
        ).order_by(Score.created_at.desc()).limit(5).all()
        
        stats = {
            'total_attempts': total_attempts,
            'total_quizzes_taken': total_attempts,  # Alias for frontend compatibility
            'passed_attempts': passed_attempts,
            'unique_quizzes': unique_quizzes,
            'average_score': round(avg_score, 2),
            'pass_rate': round((passed_attempts / total_attempts * 100) if total_attempts > 0 else 0, 2),
            'recent_scores': [score.to_dict() for score in recent_scores]
        }
        
        # Cache for 5 minutes
        if redis_client:
            redis_client.setex(cache_key, 300, json.dumps(stats))
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/performance-trend', methods=['GET'])
@user_required
def get_performance_trend():
    """Get user's performance trend data for charts"""
    try:
        from datetime import datetime, timedelta
        user_id = get_current_user_id()
        
        # Cache key specific to user
        cache_key = f'user:{user_id}:performance:trend'
        cached = redis_client.get(cache_key) if redis_client else None
        if cached:
            return jsonify(json.loads(cached)), 200
        
        # Get scores from the last 10 attempts for attempt-based view
        scores = Score.query.filter(
            Score.user_id == user_id
        ).order_by(Score.created_at.desc()).limit(10).all()
        
        if not scores:
            return jsonify({
                'labels': [],
                'data': [],
                'message': 'No quiz data available yet'
            }), 200
        
        # Reverse to show chronological order (oldest first)
        scores = list(reversed(scores))
        
        # Create labels and data for each attempt
        labels = []
        data = []
        
        for i, score in enumerate(scores):
            # Create label with attempt number and time
            attempt_time = score.created_at.strftime('%H:%M')
            attempt_date = score.created_at.strftime('%b %d')
            labels.append(f"#{i+1} - {attempt_date} {attempt_time}")
            data.append(round(score.percentage, 1))
        
        result = {
            'labels': labels,
            'data': data,
            'total_attempts': len(scores)
        }
        
        # Cache for 10 minutes (shorter since this is attempt-based)
        if redis_client:
            redis_client.setex(cache_key, 600, json.dumps(result))
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['GET'])
@user_required
def get_profile():
    """Get user profile information"""
    try:
        from app.utils.auth import get_current_user
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'profile': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@user_required
def update_profile():
    """Update user profile"""
    try:
        from app.utils.auth import get_current_user
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 

@user_bp.route('/preferences', methods=['GET'])
@user_required
def get_preferences():
    """Get user preferences"""
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Return default preferences (can be extended with a UserPreferences model)
        preferences = {
            'email_notifications': getattr(user, 'email_notifications', True),
            'reminder_emails': getattr(user, 'reminder_emails', True),
            'monthly_reports': getattr(user, 'monthly_reports', True)
        }
        
        return jsonify(preferences), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/preferences', methods=['PUT'])
@user_required
def update_preferences():
    """Update user preferences"""
    try:
        user_id = get_current_user_id()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update preferences (can be extended with a UserPreferences model)
        if 'email_notifications' in data:
            user.email_notifications = data['email_notifications']
        if 'reminder_emails' in data:
            user.reminder_emails = data['reminder_emails']
        if 'monthly_reports' in data:
            user.monthly_reports = data['monthly_reports']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Preferences updated successfully',
            'preferences': {
                'email_notifications': getattr(user, 'email_notifications', True),
                'reminder_emails': getattr(user, 'reminder_emails', True),
                'monthly_reports': getattr(user, 'monthly_reports', True)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Reminder Management
@user_bp.route('/reminders', methods=['GET'])
@user_required
def get_user_reminders():
    """Get user's reminders"""
    try:
        user_id = get_current_user_id()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        # Build query
        query = Reminder.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        
        # Order by newest first
        query = query.order_by(Reminder.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Get counts
        total_reminders = Reminder.query.filter_by(user_id=user_id).count()
        unread_reminders = Reminder.query.filter_by(user_id=user_id, is_read=False).count()
        
        return jsonify({
            'reminders': [reminder.to_dict() for reminder in pagination.items],
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages,
            'total_reminders': total_reminders,
            'unread_reminders': unread_reminders
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/reminders/<int:reminder_id>/mark-read', methods=['PUT'])
@user_required
def mark_reminder_read(reminder_id):
    """Mark a reminder as read"""
    try:
        user_id = get_current_user_id()
        
        reminder = Reminder.query.filter_by(
            id=reminder_id,
            user_id=user_id
        ).first()
        
        if not reminder:
            return jsonify({'error': 'Reminder not found'}), 404
        
        reminder.is_read = True
        db.session.commit()
        
        return jsonify({
            'message': 'Reminder marked as read',
            'reminder': reminder.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/reminders/mark-all-read', methods=['PUT'])
@user_required
def mark_all_reminders_read():
    """Mark all user's reminders as read"""
    try:
        user_id = get_current_user_id()
        
        # Update all unread reminders for this user
        updated_count = Reminder.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({'is_read': True})
        
        db.session.commit()
        
        return jsonify({
            'message': f'Marked {updated_count} reminders as read',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/reminders/<int:reminder_id>', methods=['DELETE'])
@user_required
def delete_reminder(reminder_id):
    """Delete a reminder"""
    try:
        user_id = get_current_user_id()
        
        reminder = Reminder.query.filter_by(
            id=reminder_id,
            user_id=user_id
        ).first()
        
        if not reminder:
            return jsonify({'error': 'Reminder not found'}), 404
        
        db.session.delete(reminder)
        db.session.commit()
        
        return jsonify({
            'message': 'Reminder deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 

@user_bp.route('/quizzes/<string:quiz_slug>/take', methods=['GET'])
@user_required
def take_quiz(quiz_slug):
    """Get quiz with questions for taking"""
    try:
        user_id = get_current_user_id()
        quiz = Quiz.query.filter_by(slug=quiz_slug, is_active=True).first()
        
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
            
        if not quiz.is_available:
            return jsonify({'error': 'Quiz is not available', 'status': quiz.status}), 403
            
        # Check if user has attempts remaining
        attempts = Score.query.filter_by(user_id=user_id, quiz_id=quiz.id).all()
        if quiz.max_attempts and len(attempts) >= quiz.max_attempts:
            return jsonify({'error': 'No attempts remaining for this quiz'}), 403
            
        # Get quiz with questions
        quiz_data = quiz.to_dict(include_questions=True)
        quiz_data['user_attempts'] = len(attempts)
        quiz_data['attempts_remaining'] = quiz.max_attempts - len(attempts) if quiz.max_attempts else float('inf')
        
        return jsonify(quiz_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/quizzes/<int:quiz_id>/take', methods=['GET'])
@user_required
def take_quiz_by_id(quiz_id):
    """Get quiz with questions for taking by ID"""
    try:
        user_id = get_current_user_id()
        quiz = Quiz.query.filter_by(id=quiz_id, is_active=True).first()
        
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
            
        if not quiz.is_available:
            return jsonify({'error': 'Quiz is not available', 'status': quiz.status}), 403
            
        # Check if user has attempts remaining
        attempts = Score.query.filter_by(user_id=user_id, quiz_id=quiz.id).all()
        if quiz.max_attempts and len(attempts) >= quiz.max_attempts:
            return jsonify({'error': 'No attempts remaining for this quiz'}), 403
            
        # Get quiz with questions
        quiz_data = quiz.to_dict(include_questions=True)
        quiz_data['user_attempts'] = len(attempts)
        quiz_data['attempts_remaining'] = quiz.max_attempts - len(attempts) if quiz.max_attempts else float('inf')
        
        return jsonify(quiz_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/quizzes/<string:quiz_slug>/submit', methods=['POST'])
@user_required
def submit_quiz(quiz_slug):
    """Submit quiz answers and calculate score"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        quiz = Quiz.query.filter_by(slug=quiz_slug, is_active=True).first()
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
            
        if not quiz.is_available:
            return jsonify({'error': 'Quiz is not available'}), 403
            
        # Check attempts
        attempts = Score.query.filter_by(user_id=user_id, quiz_id=quiz.id).all()
        if len(attempts) >= quiz.max_attempts:
            return jsonify({'error': 'No attempts remaining'}), 403
            
        # Get answers
        user_answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
        
        # Calculate score
        correct_answers = 0
        total_questions = len(quiz.questions)
        
        for question in quiz.questions:
            if str(question.id) in user_answers:
                user_answer = user_answers[str(question.id)]
                # Convert both to string for comparison since correct_answer is stored as string
                if str(user_answer) == str(question.correct_answer):
                    correct_answers += 1
        
        # Calculate percentage
        percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        passed = percentage >= quiz.passing_score
        
        # Create score record
        now = datetime.utcnow()
        score = Score(
            user_id=user_id,
            quiz_id=quiz.id,
            score=correct_answers,
            max_score=total_questions,
            percentage=percentage,
            passed=passed,
            attempt_number=len(attempts) + 1,
            time_taken_seconds=time_taken,
            started_at=now,
            completed_at=now
        )
        score.set_answers(user_answers)
        
        db.session.add(score)
        db.session.commit()
        
        # Clear cache
        if redis_client:
            redis_client.delete(f'user:{user_id}:available_quizzes')
            redis_client.delete(f'user:{user_id}:dashboard:stats')
        
        return jsonify({
            'message': 'Quiz submitted successfully',
            'score': {
                'correct': correct_answers,
                'total': total_questions,
                'percentage': percentage,
                'passed': passed,
                'attempt_number': score.attempt_number
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 

@user_bp.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@user_required
def submit_quiz_by_id(quiz_id):
    """Submit quiz answers and calculate score by ID"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        quiz = Quiz.query.filter_by(id=quiz_id, is_active=True).first()
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
            
        if not quiz.is_available:
            return jsonify({'error': 'Quiz is not available'}), 403
            
        # Check attempts
        attempts = Score.query.filter_by(user_id=user_id, quiz_id=quiz.id).all()
        if quiz.max_attempts and len(attempts) >= quiz.max_attempts:
            return jsonify({'error': 'No attempts remaining'}), 403
            
        # Get answers
        user_answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
        
        # Calculate score
        correct_answers = 0
        total_questions = len(quiz.questions)
        
        for question in quiz.questions:
            if str(question.id) in user_answers:
                user_answer = user_answers[str(question.id)]
                # Convert both to string for comparison since correct_answer is stored as string
                if str(user_answer) == str(question.correct_answer):
                    correct_answers += 1
        
        # Calculate percentage
        percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        passed = percentage >= quiz.passing_score
        
        # Create score record
        now = datetime.utcnow()
        score = Score(
            user_id=user_id,
            quiz_id=quiz.id,
            score=correct_answers,
            max_score=total_questions,
            percentage=percentage,
            passed=passed,
            attempt_number=len(attempts) + 1,
            time_taken_seconds=time_taken,
            started_at=now,
            completed_at=now
        )
        score.set_answers(user_answers)
        
        db.session.add(score)
        db.session.commit()
        
        # Clear cache
        if redis_client:
            redis_client.delete(f'user:{user_id}:available_quizzes')
            redis_client.delete(f'user:{user_id}:dashboard:stats')
        
        return jsonify({
            'message': 'Quiz submitted successfully',
            'score': {
                'correct': correct_answers,
                'total': total_questions,
                'percentage': percentage,
                'passed': passed,
                'attempt_number': score.attempt_number
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/quizzes/<string:quiz_slug>/result', methods=['GET'])
@user_required
def get_quiz_result(quiz_slug):
    """Get the latest quiz result for a user"""
    try:
        user_id = get_current_user_id()
        quiz = Quiz.query.filter_by(slug=quiz_slug, is_active=True).first()
        
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
            
        # Get the latest score for this user and quiz
        latest_score = Score.query.filter_by(
            user_id=user_id, 
            quiz_id=quiz.id
        ).order_by(Score.created_at.desc()).first()
        
        if not latest_score:
            return jsonify({'error': 'No quiz result found'}), 404
            
        # Get all previous attempts
        all_attempts = Score.query.filter_by(
            user_id=user_id, 
            quiz_id=quiz.id
        ).order_by(Score.created_at.desc()).all()
        
        quiz_data = quiz.to_dict()
        score_data = latest_score.to_dict()
        
        # Add previous attempts (excluding the latest one)
        previous_attempts = [a.to_dict() for a in all_attempts[1:]]
        
        return jsonify({
            'quiz': quiz_data,
            'score': score_data,
            'previous_attempts': previous_attempts
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 