"""
Authentication utilities
JWT token generation, validation, and RBAC decorators
"""
import os
import jwt
import bcrypt
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify
from bson.objectid import ObjectId


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def generate_jwt_token(user_id: str, role: str) -> str:
    """
    Generate JWT token for authenticated user
    
    Args:
        user_id: User's MongoDB ObjectId
        role: User's role (user or admin)
    
    Returns:
        JWT token string
    """
    jwt_secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    payload = {
        'user_id': str(user_id),
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, jwt_secret_key, algorithm='HS256')


def decode_jwt_token(token: str) -> dict:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        jwt_secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        payload = jwt.decode(token, jwt_secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_request() -> str:
    """Extract JWT token from Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    return auth_header[7:]  # Remove 'Bearer ' prefix


def token_required(f):
    """
    Decorator to protect routes with JWT authentication
    Validates token and injects user_id and role into route function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        payload = decode_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Inject user info into kwargs
        kwargs['user_id'] = payload['user_id']
        kwargs['user_role'] = payload['role']
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    Decorator to protect admin routes
    Validates JWT token and checks for admin role
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        payload = decode_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        if payload.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        kwargs['user_id'] = payload['user_id']
        kwargs['user_role'] = payload['role']
        return f(*args, **kwargs)
    
    return decorated


def objectid_to_string(obj):
    """
    Recursively convert ObjectId instances to strings in dictionaries/lists
    Used for JSON serialization
    """
    if isinstance(obj, dict):
        return {key: objectid_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [objectid_to_string(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj
