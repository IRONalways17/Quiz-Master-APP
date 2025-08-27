from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from backend.app.models import User, Admin

def jwt_required_custom(fn):
    """Custom JWT required decorator that handles both User and Admin"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        return fn(*args, **kwargs)
    return wrapper

def user_required(fn):
    """Decorator to require user role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        if claims.get('role') != 'user':
            return jsonify({'error': 'User access required'}), 403
            
        return fn(*args, **kwargs)
    return wrapper

def get_current_user():
    """Get current user from JWT token"""
    identity = get_jwt_identity()
    claims = get_jwt()
    
    if claims.get('role') == 'admin':
        return Admin.query.filter_by(email=identity).first()
    else:
        return User.query.filter_by(email=identity).first()

def get_current_user_id():
    """Get current user ID from JWT token"""
    identity = get_jwt_identity()
    claims = get_jwt()
    
    if claims.get('role') == 'admin':
        admin = Admin.query.filter_by(email=identity).first()
        return admin.id if admin else None
    else:
        user = User.query.filter_by(email=identity).first()
        return user.id if user else None 
