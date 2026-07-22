from flask import Blueprint, request, jsonify, current_app
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from app.utils.auth import hash_password, verify_password, generate_jwt_token, objectid_to_string
from app.utils.email import generate_otp, send_otp_email
from app.models.validators import UserModel, OTPModel, validate_email, validate_password
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user with email and password
    Triggers OTP-based email verification
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        # Validation
        if not email or not password or not full_name:
            return jsonify({'error': 'Email, password, and full name are required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        db = current_app.mongo.db
        existing_user = db.users.find_one({'email': email})
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        password_hash = hash_password(password)
        new_user = UserModel.create(email, password_hash, full_name)
        
        result = db.users.insert_one(new_user)
        new_user['_id'] = result.inserted_id
        
        # Generate and send OTP
        otp = generate_otp()
        otp_doc = OTPModel.create(email, otp, expiry_minutes=int(os.getenv("OTP_EXPIRY_MINUTES", 10)))
        db.otps.insert_one(otp_doc)
        
        # Send OTP email
        email_sent = send_otp_email(email, otp, full_name)
        
        return jsonify({
            'message': 'User registered successfully. Please verify your email.',
            'email': email,
            'otp_sent': email_sent
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """
    Verify user email using OTP
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        email = data.get('email', '').strip().lower()
        otp = data.get('otp', '').strip()
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        db = current_app.mongo.db
        
        # Find and validate OTP
        otp_doc = db.otps.find_one({
            'email': email,
            'otp': otp,
            'is_used': False
        })
        
        if not otp_doc:
            return jsonify({'error': 'Invalid OTP'}), 400
        
        # Check if OTP has expired
        if datetime.utcnow() > otp_doc['expires_at']:
            return jsonify({'error': 'OTP has expired'}), 400
        
        # Mark OTP as used and verify user
        db.otps.update_one({'_id': otp_doc['_id']}, {'$set': {'is_used': True}})
        db.users.update_one({'email': email}, {'$set': {'is_verified': True}})
        
        return jsonify({'message': 'Email verified successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """
    Resend OTP to user's email
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        db = current_app.mongo.db
        
        # Check if user exists
        user = db.users.find_one({'email': email})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.get('is_verified'):
            return jsonify({'error': 'Email already verified'}), 400
        
        # Generate and send new OTP
        otp = generate_otp()
        otp_doc = OTPModel.create(email, otp, expiry_minutes=int(os.getenv("OTP_EXPIRY_MINUTES", 10)))
        db.otps.insert_one(otp_doc)
        
        email_sent = send_otp_email(email, otp, user.get('full_name', 'User'))
        
        return jsonify({
            'message': 'OTP resent successfully',
            'otp_sent': email_sent
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user with email and password
    Returns JWT access token
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        db = current_app.mongo.db
        
        # Find user
        user = db.users.find_one({'email': email})
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if email is verified
        if not user.get('is_verified'):
            return jsonify({'error': 'Email not verified. Please verify your email first.'}), 401
        
        # Verify password
        if not verify_password(password, user['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate JWT token
        token = generate_jwt_token(str(user['_id']), user.get('role', 'user'))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': token,
            'token_type': 'Bearer',
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'full_name': user.get('full_name'),
                'role': user.get('role', 'user')
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
