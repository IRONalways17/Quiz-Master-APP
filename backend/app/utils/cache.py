import json
import hashlib
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify
from app import redis_client

class CacheManager:
    """Centralized cache management with expiry and performance optimizations"""
    
    @staticmethod
    def generate_cache_key(prefix, *args, **kwargs):
        """Generate a unique cache key based on prefix and arguments"""
        key_parts = [prefix]
        
        # Add args to key
        for arg in args:
            key_parts.append(str(arg))
        
        # Add sorted kwargs to key
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        # Create hash for long keys
        key_string = ":".join(key_parts)
        if len(key_string) > 200:
            return f"{prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"
        
        return key_string
    
    @staticmethod
    def get_cached_data(key, default=None):
        """Get data from cache with error handling"""
        if not redis_client:
            return default
        
        try:
            cached = redis_client.get(key)
            return json.loads(cached) if cached else default
        except Exception as e:
            print(f"Cache get error: {e}")
            return default
    
    @staticmethod
    def set_cached_data(key, data, expiry=300):
        """Set data in cache with expiry"""
        if not redis_client:
            return False
        
        try:
            redis_client.setex(key, expiry, json.dumps(data))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    @staticmethod
    def clear_cache_pattern(pattern):
        """Clear cache by pattern"""
        if not redis_client:
            return False
        
        try:
            keys = list(redis_client.scan_iter(match=pattern))
            for key in keys:
                redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalidate all cache related to a specific user"""
        patterns = [
            f'user:{user_id}:*',
            f'stats:user:{user_id}*',
            f'scores:user:{user_id}*'
        ]
        
        for pattern in patterns:
            CacheManager.clear_cache_pattern(pattern)
    
    @staticmethod
    def invalidate_subject_cache(subject_id=None):
        """Invalidate subject-related cache"""
        if subject_id:
            patterns = [
                f'subject:{subject_id}:*',
                f'chapters:subject:{subject_id}*'
            ]
        else:
            patterns = ['subjects:*', 'chapters:*']
        
        for pattern in patterns:
            CacheManager.clear_cache_pattern(pattern)
    
    @staticmethod
    def invalidate_quiz_cache(quiz_id=None):
        """Invalidate quiz-related cache"""
        if quiz_id:
            patterns = [
                f'quiz:{quiz_id}:*',
                f'questions:quiz:{quiz_id}*'
            ]
        else:
            patterns = ['quizzes:*', 'questions:*']
        
        for pattern in patterns:
            CacheManager.clear_cache_pattern(pattern)

def cache_response(expiry=300, key_prefix='api'):
    """Decorator to cache API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip cache for non-GET requests
            if request.method != 'GET':
                return f(*args, **kwargs)
            
            # Generate cache key
            cache_key = CacheManager.generate_cache_key(
                key_prefix,
                request.path,
                request.args.get('page', 1),
                request.args.get('per_page', 20),
                request.args.get('search', ''),
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_data = CacheManager.get_cached_data(cache_key)
            if cached_data is not None:
                return jsonify(cached_data)
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            
            # Cache successful responses
            if isinstance(result, tuple) and len(result) == 2:
                response_data, status_code = result
                if status_code == 200:
                    CacheManager.set_cached_data(cache_key, response_data, expiry)
            
            return result
        
        return decorated_function
    return decorator

def cache_user_data(expiry=600):
    """Decorator to cache user-specific data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.utils.auth import get_current_user_id
            
            user_id = get_current_user_id()
            if not user_id:
                return f(*args, **kwargs)
            
            # Generate cache key with user ID
            cache_key = CacheManager.generate_cache_key(
                'user_data',
                user_id,
                request.path,
                request.args.get('page', 1),
                request.args.get('per_page', 20),
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_data = CacheManager.get_cached_data(cache_key)
            if cached_data is not None:
                return jsonify(cached_data)
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            
            # Cache successful responses
            if isinstance(result, tuple) and len(result) == 2:
                response_data, status_code = result
                if status_code == 200:
                    CacheManager.set_cached_data(cache_key, response_data, expiry)
            
            return result
        
        return decorated_function
    return decorator

def cache_admin_data(expiry=300):
    """Decorator to cache admin-specific data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            cache_key = CacheManager.generate_cache_key(
                'admin_data',
                request.path,
                request.args.get('page', 1),
                request.args.get('per_page', 20),
                request.args.get('search', ''),
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_data = CacheManager.get_cached_data(cache_key)
            if cached_data is not None:
                return jsonify(cached_data)
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            
            # Cache successful responses
            if isinstance(result, tuple) and len(result) == 2:
                response_data, status_code = result
                if status_code == 200:
                    CacheManager.set_cached_data(cache_key, response_data, expiry)
            
            return result
        
        return decorated_function
    return decorator

# Cache configuration
CACHE_CONFIG = {
    'subjects': 600,  # 10 minutes
    'chapters': 600,  # 10 minutes
    'quizzes': 300,   # 5 minutes
    'questions': 300, # 5 minutes
    'user_scores': 300,  # 5 minutes
    'user_stats': 300,   # 5 minutes
    'admin_stats': 300,  # 5 minutes
    'search_results': 180,  # 3 minutes
    'dashboard_data': 300,  # 5 minutes
}

# Cache patterns for invalidation
CACHE_PATTERNS = {
    'subjects': 'subjects:*',
    'chapters': 'chapters:*',
    'quizzes': 'quizzes:*',
    'questions': 'questions:*',
    'user_data': 'user:*',
    'admin_data': 'admin:*',
    'stats': 'stats:*',
    'search': 'search:*'
} 