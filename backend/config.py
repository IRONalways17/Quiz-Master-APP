import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Database - Handle Heroku PostgreSQL URL
    database_url = os.getenv('DATABASE_URL', 'sqlite:///quizmaster.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS - Allow all origins for Heroku deployment
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Celery (using SQLite as backend instead of Redis)
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'sqla+sqlite:///celery.db')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'db+sqlite:///celery.db')
    
    # Rate Limiting (using memory storage)
    RATELIMIT_DEFAULT = os.getenv('API_RATE_LIMIT', '100 per hour')
    
    # Admin
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@quizmaster.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Cache
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Production settings
    if not DEBUG:
        # Use secure cookies in production
        SESSION_COOKIE_SECURE = True
        SESSION_COOKIE_HTTPONLY = True
        SESSION_COOKIE_SAMESITE = 'Lax'
        # Allow JWT from any IP in production
        JWT_ACCESS_CSRF_HEADER_NAME = None
        JWT_REFRESH_CSRF_HEADER_NAME = None 