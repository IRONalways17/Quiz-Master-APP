from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import sys
import os
sys.path.append('..')
from backend.config import Config
from backend.app.database import db

# Initialize extensions
jwt = JWTManager()
redis_client = None
limiter = None  # Will be initialized after Redis

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database and JWT first
    db.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS - Allow all origins for production deployment
    CORS(app, 
         origins=['*'], 
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Initialize Redis
    global redis_client, limiter
    redis_client = redis.from_url(app.config['REDIS_URL'], decode_responses=True)
    
    # Test Redis connection
    try:
        redis_client.ping()
        print("✓ Redis connection established")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        redis_client = None
    
    # Initialize rate limiter with Redis storage
    if redis_client:
        limiter = Limiter(
            key_func=get_remote_address,
            storage_uri=app.config['REDIS_URL'],
            default_limits=["200000 per day", "5000 per hour"]
        )
    else:
        # Fallback to memory storage
        limiter = Limiter(key_func=get_remote_address)
    
    limiter.init_app(app)
    
    # Import models to ensure they're registered with SQLAlchemy
    from backend.app.models import User, Admin, Subject, Chapter, Quiz, Question, Score
    
    # Register blueprints
    from backend.app.routes.auth import auth_bp
    from backend.app.routes.admin import admin_bp
    from backend.app.routes.user import user_bp
    from backend.app.routes.quiz import quiz_bp
    from backend.app.routes.common import common_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(common_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        from app.utils.init_db import create_default_admin
        create_default_admin()
    
    # Serve frontend static files
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'frontend', 'dist')
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(frontend_dist, path)):
            return send_from_directory(frontend_dist, path)
        else:
            return send_file(os.path.join(frontend_dist, 'index.html'))
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Quiz Master API is running'}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {'error': f'Rate limit exceeded: {e.description}'}, 429
    
    return app 