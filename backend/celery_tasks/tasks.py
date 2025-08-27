from celery import shared_task
from datetime import datetime, timedelta
import pandas as pd
import os
import json
import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from jinja2 import Template

@shared_task
def send_daily_reminders():
    """Create daily reminder notifications in database for inactive users and new quizzes"""
    try:
        from app import create_app
        from app.models import User, Quiz, Score, Reminder
        from app.database import db
        
        app = create_app()
        with app.app_context():
            # Get current time
            now = datetime.utcnow()
            yesterday = now - timedelta(days=1)
            
            # Get all active users
            users = User.query.filter_by(is_active=True).all()
            
            reminders_created = 0
            
            for user in users:
                # Check if user has been inactive (no quiz attempts in last 1 day)
                recent_activity = Score.query.filter(
                    Score.user_id == user.id,
                    Score.created_at >= yesterday
                ).count()
                
                # Check for new quizzes available to user
                available_quizzes = []
                quizzes = Quiz.query.filter_by(is_active=True).all()
                
                for quiz in quizzes:
                    if quiz.is_available:
                        # Check if user has attempts remaining
                        attempts = Score.query.filter_by(
                            user_id=user.id,
                            quiz_id=quiz.id
                        ).count()
                        
                        if attempts < quiz.max_attempts:
                            available_quizzes.append(quiz)
                
                # Create reminders based on conditions
                
                # 1. Inactive user reminder
                if recent_activity == 0 and available_quizzes:
                    message = f"Hey {user.full_name}! You haven't attempted any quizzes today. You have {len(available_quizzes)} quiz(s) available to attempt."
                    
                    # Check if similar reminder already exists today
                    existing_reminder = Reminder.query.filter(
                        Reminder.user_id == user.id,
                        Reminder.reminder_type == 'inactive_user',
                        Reminder.created_at >= now.replace(hour=0, minute=0, second=0, microsecond=0)
                    ).first()
                    
                    if not existing_reminder:
                        reminder = Reminder(
                            user_id=user.id,
                            message=message,
                            reminder_type='inactive_user'
                        )
                        db.session.add(reminder)
                        reminders_created += 1
                
                # 2. New quiz reminders (for quizzes created in last day)
                new_quizzes = [q for q in available_quizzes if q.created_at >= yesterday]
                if new_quizzes:
                    for quiz in new_quizzes:
                        message = f"New quiz available: '{quiz.title}' in {quiz.chapter.subject.name}. Don't miss out!"
                        
                        # Check if reminder for this specific quiz already exists
                        existing_quiz_reminder = Reminder.query.filter(
                            Reminder.user_id == user.id,
                            Reminder.reminder_type == 'new_quiz',
                            Reminder.message.contains(quiz.title),
                            Reminder.created_at >= now.replace(hour=0, minute=0, second=0, microsecond=0)
                        ).first()
                        
                        if not existing_quiz_reminder:
                            reminder = Reminder(
                                user_id=user.id,
                                message=message,
                                reminder_type='new_quiz'
                            )
                            db.session.add(reminder)
                            reminders_created += 1
            
            # Commit all reminders
            db.session.commit()
            
            print(f"[REMINDER] Created {reminders_created} new reminders for users")
            return {'status': 'success', 'message': f'Created {reminders_created} daily reminders', 'reminders_created': reminders_created}
        
    except Exception as e:
        print(f"[REMINDER ERROR] {str(e)}")
        return {'status': 'error', 'message': str(e)}

@shared_task
def generate_monthly_reports():
    """Generate and send monthly activity reports via email"""
    try:
        from app import create_app
        from app.models import User, Score, Quiz
        from app.database import db
        
        app = create_app()
        with app.app_context():
            # Get last month's date range
            today = datetime.utcnow()
            first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last_day_last_month = today.replace(day=1) - timedelta(days=1)
            
            # Get all users with activity last month
            users_with_scores = db.session.query(User).join(Score).filter(
                Score.created_at >= first_day_last_month,
                Score.created_at <= last_day_last_month
            ).distinct().all()
            
            reports_sent = 0
            for user in users_with_scores:
                # Generate report for each user
                report_data = generate_user_monthly_report(user.id, first_day_last_month, last_day_last_month)
                
                # Send email with HTML report
                if send_monthly_report_email(user, report_data, first_day_last_month):
                    reports_sent += 1
                    print(f"[REPORT] Sent monthly report to {user.email}")
            
            return {
                'status': 'success',
                'message': f'Sent {reports_sent} monthly reports'
            }
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@shared_task
def export_user_scores_csv(user_id):
    """Export user's scores to CSV and send notification"""
    try:
        from app import create_app
        from app.models import User, Score
        from app.database import db
        
        app = create_app()
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return {'status': 'error', 'message': 'User not found'}
            
            # Get all scores for the user
            scores = Score.query.filter_by(user_id=user_id).order_by(Score.created_at.desc()).all()
            
            # Prepare data for CSV
            data = []
            for score in scores:
                data.append({
                    'Quiz ID': score.quiz_id,
                    'Quiz Title': score.quiz.title,
                    'Subject': score.quiz.chapter.subject.name,
                    'Chapter': score.quiz.chapter.name,
                    'Date of Quiz': score.quiz.start_date.strftime('%Y-%m-%d'),
                    'Score': f"{score.score}/{score.max_score}",
                    'Percentage': f"{score.percentage}%",
                    'Passed': 'Yes' if score.passed else 'No',
                    'Attempt Number': score.attempt_number,
                    'Time Taken (minutes)': score.time_taken_seconds // 60 if score.time_taken_seconds else 0,
                    'Completed Date': score.created_at.strftime('%Y-%m-%d %H:%M')
                })
            
            # Create DataFrame and save to CSV
            df = pd.DataFrame(data)
            filename = f"user_{user_id}_scores_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join('exports', filename)
            os.makedirs('exports', exist_ok=True)
            
            df.to_csv(filepath, index=False)
            
            # Send notification to user
            email_sent = send_export_notification(user, filename, 'user_scores')
            
            return {
                'status': 'success',
                'message': 'CSV exported successfully',
                'filename': filename,
                'filepath': filepath,
                'rows': len(data),
                'email_sent': email_sent
            }
            
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def create_daily_reminder_message(user, available_quizzes):
    """Create a formatted message for daily reminders"""
    message = {
        "cards": [{
            "header": {
                "title": f"Daily Quiz Reminder for {user.full_name or user.username}",
                "subtitle": f"Good evening! You have {len(available_quizzes)} quiz(zes) available."
            },
            "sections": [{
                "widgets": [{
                    "keyValue": {
                        "topLabel": "Available Quizzes",
                        "content": f"{len(available_quizzes)} quiz(zes) waiting for you"
                    }
                }]
            }]
        }]
    }
    
    # Add quiz details
    quiz_details = []
    for quiz in available_quizzes[:5]:  # Limit to 5 quizzes
        quiz_details.append({
            "widgets": [{
                "keyValue": {
                    "topLabel": quiz.title,
                    "content": f"Ends: {quiz.end_date.strftime('%Y-%m-%d')} | Duration: {quiz.duration_minutes} min"
                }
            }]
        })
    
    if quiz_details:
        message["cards"][0]["sections"].extend(quiz_details)
    
    return message

def send_google_chat_notification(webhook_url, message):
    """Send notification to Google Chat"""
    try:
        response = requests.post(
            webhook_url,
            json=message,
            headers={'Content-Type': 'application/json'}
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send Google Chat notification: {e}")
        return False

def generate_user_monthly_report(user_id, start_date, end_date):
    """Generate comprehensive monthly report data for a user"""
    from app.models import Score
    
    scores = Score.query.filter(
        Score.user_id == user_id,
        Score.created_at >= start_date,
        Score.created_at <= end_date
    ).all()
    
    if not scores:
        return {
            'total_attempts': 0,
            'average_score': 0,
            'passed_count': 0,
            'failed_count': 0,
            'top_subjects': [],
            'recent_activity': []
        }
    
    # Calculate statistics
    avg_score = sum(s.percentage for s in scores) / len(scores)
    passed_count = sum(1 for s in scores if s.passed)
    
    # Get top subjects
    subject_scores = {}
    for score in scores:
        subject = score.quiz.chapter.subject.name
        if subject not in subject_scores:
            subject_scores[subject] = []
        subject_scores[subject].append(score.percentage)
    
    top_subjects = []
    for subject, percentages in subject_scores.items():
        avg_percentage = sum(percentages) / len(percentages)
        top_subjects.append({
            'name': subject,
            'average': avg_percentage,
            'attempts': len(percentages)
        })
    
    top_subjects.sort(key=lambda x: x['average'], reverse=True)
    
    return {
        'total_attempts': len(scores),
        'average_score': avg_score,
        'passed_count': passed_count,
        'failed_count': len(scores) - passed_count,
        'top_subjects': top_subjects[:5],
        'recent_activity': scores[:10],
        'scores': scores
    }

def send_monthly_report_email(user, report_data, month_date):
    """Send monthly report via email"""
    try:
        # Email configuration
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        
        if not all([smtp_username, smtp_password]):
            print("SMTP credentials not configured")
            return False
        
        # Create HTML report
        html_content = create_monthly_report_html(user, report_data, month_date)
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Monthly Quiz Report - {month_date.strftime("%B %Y")}'
        msg['From'] = smtp_username
        msg['To'] = user.email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"Failed to send monthly report email: {e}")
        return False

def create_monthly_report_html(user, report_data, month_date):
    """Create HTML content for monthly report"""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #3498db; color: white; padding: 20px; text-align: center; }
            .stats { display: flex; justify-content: space-around; margin: 20px 0; }
            .stat-box { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }
            .subject-list { margin: 20px 0; }
            .subject-item { background: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 3px; }
            .activity-list { margin: 20px 0; }
            .activity-item { border-bottom: 1px solid #ddd; padding: 10px 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Monthly Quiz Report</h1>
            <p>{{ month_name }} {{ year }}</p>
        </div>
        
        <h2>Hello {{ user_name }}!</h2>
        <p>Here's your quiz activity summary for {{ month_name }} {{ year }}:</p>
        
        <div class="stats">
            <div class="stat-box">
                <h3>{{ total_attempts }}</h3>
                <p>Total Attempts</p>
            </div>
            <div class="stat-box">
                <h3>{{ average_score }}%</h3>
                <p>Average Score</p>
            </div>
            <div class="stat-box">
                <h3>{{ passed_count }}</h3>
                <p>Passed Quizzes</p>
            </div>
        </div>
        
        {% if top_subjects %}
        <h3>Top Performing Subjects</h3>
        <div class="subject-list">
            {% for subject in top_subjects %}
            <div class="subject-item">
                <strong>{{ subject.name }}</strong> - {{ subject.average }}% ({{ subject.attempts }} attempts)
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if recent_activity %}
        <h3>Recent Activity</h3>
        <div class="activity-list">
            {% for score in recent_activity %}
            <div class="activity-item">
                <strong>{{ score.quiz.title }}</strong> - {{ score.percentage }}% 
                ({{ score.created_at.strftime('%Y-%m-%d') }})
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <p>Keep up the great work! Continue practicing to improve your scores.</p>
    </body>
    </html>
    """
    
    jinja_template = Template(template)
    return jinja_template.render(
        user_name=user.full_name or user.username,
        month_name=month_date.strftime('%B'),
        year=month_date.year,
        total_attempts=report_data['total_attempts'],
        average_score=f"{report_data['average_score']:.1f}",
        passed_count=report_data['passed_count'],
        top_subjects=report_data['top_subjects'],
        recent_activity=report_data['recent_activity']
    )

def send_export_notification(user, filename, export_type):
    """Send notification to user about completed export"""
    try:
        # Send email notification
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        
        print(f"SMTP Configuration - Server: {smtp_server}, Port: {smtp_port}")
        print(f"SMTP Username: {'SET' if smtp_username else 'NOT SET'}")
        print(f"SMTP Password: {'SET' if smtp_password else 'NOT SET'}")
        
        if not all([smtp_username, smtp_password]):
            print("SMTP credentials not configured. Email notification skipped.")
            return False
        
        if smtp_username == 'your-email@gmail.com' or smtp_password == 'your-app-password':
            print("SMTP credentials are still using placeholder values. Email notification skipped.")
            return False
        
        msg = MIMEMultipart()
        msg['Subject'] = 'Quiz Export Completed'
        msg['From'] = smtp_username
        msg['To'] = user.email
        
        body = f"""
        Hello {user.full_name or user.username},
        
        Your quiz export has been completed successfully!
        
        File: {filename}
        Export Type: {export_type}
        
        The file has been saved to the server and is available for download.
        
        Best regards,
        Quiz Master Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        print(f"Attempting to send email to {user.email}")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"Email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        print(f"Failed to send export notification: {e}")
        return False

def generate_user_report(user_id, start_date, end_date):
    """Generate user performance report data"""
    from app.models import Score
    from app.database import db
    
    scores = Score.query.filter(
        Score.user_id == user_id,
        Score.created_at >= start_date,
        Score.created_at <= end_date
    ).all()
    
    if not scores:
        return {
            'total_attempts': 0,
            'average_score': 0,
            'passed_count': 0,
            'failed_count': 0
        }
    
    return {
        'total_attempts': len(scores),
        'average_score': sum(s.percentage for s in scores) / len(scores),
        'passed_count': sum(1 for s in scores if s.passed),
        'failed_count': sum(1 for s in scores if not s.passed),
        'scores': scores
    } 