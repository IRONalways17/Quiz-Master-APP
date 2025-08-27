from celery import Celery
from celery.schedules import crontab
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import Config

# Create Celery instance
celery = Celery(
    'quizmaster',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=['celery_tasks.tasks']
)

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'daily-reminder': {
            'task': 'celery_tasks.tasks.send_daily_reminders',
            'schedule': crontab(hour=12, minute=30),  # Daily at 6:00 PM IST (12:30 PM UTC)
            'options': {'queue': 'periodic'}
        },
        'monthly-report': {
            'task': 'celery_tasks.tasks.generate_monthly_reports',
            'schedule': crontab(hour=9, minute=0, day_of_month=1),  # First day of month at 2:30 PM IST
            'options': {'queue': 'periodic'}
        },
    }
)

if __name__ == '__main__':
    celery.start() 