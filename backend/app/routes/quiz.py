from flask import Blueprint, request, jsonify
from backend.app.database import db
from backend.app.models import Quiz, Question, Score
from backend.app.utils.auth import user_required, get_current_user_id
from datetime import datetime
import json

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/<int:quiz_id>/info', methods=['GET'])
@user_required
def get_quiz_info(quiz_id):
    """Get quiz information before starting"""
    try:
        user_id = get_current_user_id()
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz or not quiz.is_active:
            return jsonify({'error': 'Quiz not found'}), 404
        
        if not quiz.is_available:
            return jsonify({'error': 'Quiz is not available', 'status': quiz.status}), 403
        
        # Get user's previous attempts
        attempts = Score.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id
        ).all()
        
        quiz_info = quiz.to_dict()
        quiz_info['attempts_made'] = len(attempts)
        quiz_info['attempts_remaining'] = quiz.max_attempts - len(attempts)
        quiz_info['previous_scores'] = [
            {
                'attempt': a.attempt_number,
                'score': a.percentage,
                'passed': a.passed,
                'date': a.created_at.isoformat()
            } for a in attempts
        ]
        quiz_info['can_attempt'] = len(attempts) < quiz.max_attempts
        
        return jsonify(quiz_info), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/<int:quiz_id>/start', methods=['POST'])
@user_required
def start_quiz(quiz_id):
    """Start a quiz attempt"""
    try:
        user_id = get_current_user_id()
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz or not quiz.is_active:
            return jsonify({'error': 'Quiz not found'}), 404
        
        if not quiz.is_available:
            return jsonify({'error': 'Quiz is not available', 'status': quiz.status}), 403
        
        # Check if user has attempts remaining
        attempts = Score.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id
        ).count()
        
        if attempts >= quiz.max_attempts:
            return jsonify({'error': 'No attempts remaining'}), 403
        
        # Get questions for the quiz
        questions = Question.query.filter_by(
            quiz_id=quiz_id,
            is_active=True
        ).order_by(Question.order).all()
        
        if not questions:
            return jsonify({'error': 'No questions found for this quiz'}), 404
        
        # Create a quiz session in Redis
        session_key = f'quiz_session:{user_id}:{quiz_id}'
        session_data = {
            'user_id': user_id,
            'quiz_id': quiz_id,
            'started_at': datetime.utcnow().isoformat(),
            'questions': [q.id for q in questions],
            'attempt_number': attempts + 1
        }
        
        # Session storage removed - quiz sessions will be handled without Redis
        return jsonify({
            'message': 'Quiz started successfully',
            'quiz': quiz.to_dict(),
            'questions': [q.to_dict_for_quiz() for q in questions],
            'duration_minutes': quiz.duration_minutes,
            'started_at': session_data['started_at'],
            'session_key': session_key
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/<int:quiz_id>/submit', methods=['POST'])
@user_required
def submit_quiz(quiz_id):
    """Submit quiz answers"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        if 'answers' not in data:
            return jsonify({'error': 'Answers are required'}), 400
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Session storage removed - skip session validation for now
        # Note: In production, implement proper session management without Redis
        
        # Get all questions
        questions = Question.query.filter_by(
            quiz_id=quiz_id,
            is_active=True
        ).all()
        
        # Calculate score
        total_points = 0
        earned_points = 0
        correct_answers = 0
        
        for question in questions:
            total_points += question.points
            answer = data['answers'].get(str(question.id))
            
            if answer is not None and str(answer) == str(question.correct_answer):
                earned_points += question.points
                correct_answers += 1
        
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = percentage >= quiz.passing_score
        
        # Get attempt number
        existing_attempts = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).count()
        
        # Create score record
        score = Score(
            user_id=user_id,
            quiz_id=quiz_id,
            score=earned_points,
            max_score=total_points,
            percentage=percentage,
            passed=passed,
            started_at=datetime.utcnow(),  # Use current time since session is not tracked
            completed_at=datetime.utcnow(),
            attempt_number=existing_attempts + 1
        )
        score.set_answers(data['answers'])
        score.calculate_time_taken()
        
        db.session.add(score)
        db.session.commit()
        
        # Session management removed - no cache invalidation needed
        
        # Prepare result with explanations
        question_results = []
        for question in questions:
            user_answer = data['answers'].get(str(question.id))
            is_correct = str(user_answer) == str(question.correct_answer) if user_answer is not None else False
            
            question_results.append({
                'question_id': question.id,
                'question_text': question.question_text,
                'user_answer': user_answer,
                'correct_answer': question.correct_answer,
                'is_correct': is_correct,
                'explanation': question.explanation if not is_correct else None,
                'points': question.points,
                'earned': question.points if is_correct else 0
            })
        
        return jsonify({
            'message': 'Quiz submitted successfully',
            'score': score.to_dict(),
            'results': {
                'total_questions': len(questions),
                'correct_answers': correct_answers,
                'percentage': round(percentage, 2),
                'passed': passed,
                'time_taken_seconds': score.time_taken_seconds,
                'question_results': question_results
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/<int:quiz_id>/leaderboard', methods=['GET'])
@user_required
def get_quiz_leaderboard(quiz_id):
    """Get leaderboard for a specific quiz"""
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Cache removed - fetch data directly
        # Get top 10 scores for this quiz
        top_scores = db.session.query(
            Score,
            db.func.max(Score.percentage).label('best_score')
        ).filter_by(
            quiz_id=quiz_id
        ).group_by(Score.user_id).order_by(
            db.desc('best_score')
        ).limit(10).all()
        
        leaderboard = []
        for idx, (score, _) in enumerate(top_scores, 1):
            leaderboard.append({
                'rank': idx,
                'user_id': score.user_id,
                'username': score.user.username,
                'score': score.percentage,
                'time_taken': score.time_taken_seconds,
                'date': score.created_at.isoformat()
            })
        
        data = {
            'quiz': quiz.to_dict(),
            'leaderboard': leaderboard
        }
        
        # Cache removed - return data directly
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
