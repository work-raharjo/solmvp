from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.user import User, db
import bcrypt
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_passport_number(passport_number):
    # Basic validation - alphanumeric, 6-15 characters
    pattern = r'^[A-Z0-9]{6,15}$'
    return re.match(pattern, passport_number.upper()) is not None

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['passport_number', 'full_name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate passport number format
        if not validate_passport_number(data['passport_number']):
            return jsonify({'error': 'Invalid passport number format'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == data['email']) | 
            (User.passport_number == data['passport_number'].upper())
        ).first()
        
        if existing_user:
            return jsonify({'error': 'User with this email or passport number already exists'}), 409
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create new user
        user = User(
            passport_number=data['passport_number'].upper(),
            full_name=data['full_name'],
            email=data['email'].lower(),
            phone_number=data.get('phone_number'),
            password_hash=password_hash,
            kyc_status='PENDING'
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id,
            'kyc_status': user.kyc_status,
            'access_token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=data['email'].lower()).first()
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check password
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'kyc_status': user.kyc_status,
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user_id': user.id,
            'full_name': user.full_name,
            'email': user.email,
            'passport_number': user.passport_number,
            'phone_number': user.phone_number,
            'kyc_status': user.kyc_status,
            'wallet_balance': float(user.wallet_balance)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

