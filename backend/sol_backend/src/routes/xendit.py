from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, Transaction, db
import base64
import uuid
import requests
import os
import logging
from decimal import Decimal

xendit_bp = Blueprint('xendit', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Xendit API configuration
XENDIT_API_BASE_URL = os.getenv('XENDIT_API_BASE_URL', 'https://api.xendit.co')
XENDIT_API_KEY = os.getenv('XENDIT_API_KEY', 'mock-xendit-api-key')

def get_xendit_auth_header():
    """Generate Xendit Basic Auth header"""
    # Xendit uses API key as username with empty password
    auth_string = f"{XENDIT_API_KEY}:"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    return f"Basic {encoded_auth}"

def mock_xendit_payment_request(amount, channel_code, reference_id):
    """Mock Xendit payment request creation"""
    # In real implementation, this would call Xendit API
    # For MVP, return mock response based on channel
    
    payment_request_id = f"pr-{str(uuid.uuid4())}"
    
    if channel_code == "QRIS":
        return {
            "payment_request_id": payment_request_id,
            "reference_id": reference_id,
            "status": "ACCEPTING_PAYMENTS",
            "channel_code": "QRIS",
            "actions": [
                {
                    "action": "QR_CHECKOUT",
                    "url": f"https://checkout.xendit.co/qr/{payment_request_id}",
                    "qr_string": f"00020101021226670016COM.XENDIT.WWW01189999{payment_request_id}520454995303360540{amount}5802ID5909XENDIT6007Jakarta61051234562070703A016304ABCD"
                }
            ],
            "request_amount": amount,
            "currency": "IDR"
        }
    
    elif channel_code in ["BCA_VA", "BNI_VA", "BRI_VA", "MANDIRI_VA"]:
        bank_code = channel_code.split("_")[0]
        va_number = f"8808{str(uuid.uuid4())[:8]}"
        
        return {
            "payment_request_id": payment_request_id,
            "reference_id": reference_id,
            "status": "ACCEPTING_PAYMENTS",
            "channel_code": channel_code,
            "channel_properties": {
                "virtual_account_number": va_number,
                "bank_code": bank_code
            },
            "request_amount": amount,
            "currency": "IDR"
        }
    
    elif channel_code in ["CREDIT_CARD", "DEBIT_CARD"]:
        return {
            "payment_request_id": payment_request_id,
            "reference_id": reference_id,
            "status": "ACCEPTING_PAYMENTS",
            "channel_code": channel_code,
            "actions": [
                {
                    "action": "AUTH",
                    "url": f"https://checkout.xendit.co/web/{payment_request_id}"
                }
            ],
            "request_amount": amount,
            "currency": "IDR"
        }
    
    else:  # E-wallets (OVO, GOPAY, DANA, etc.)
        return {
            "payment_request_id": payment_request_id,
            "reference_id": reference_id,
            "status": "ACCEPTING_PAYMENTS",
            "channel_code": channel_code,
            "actions": [
                {
                    "action": "DEEPLINK_CHECKOUT",
                    "url": f"https://checkout.xendit.co/web/{payment_request_id}",
                    "mobile_deeplink_checkout_url": f"{channel_code.lower()}://pay?id={payment_request_id}"
                }
            ],
            "request_amount": amount,
            "currency": "IDR"
        }

@xendit_bp.route('/xendit/payment-request', methods=['POST'])
@jwt_required()
def create_payment_request():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check KYC status for payments
        if user.kyc_status != 'APPROVED':
            return jsonify({'error': 'KYC verification required before making payments'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'channel_code', 'type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        amount = Decimal(str(data['amount']))
        channel_code = data['channel_code']
        payment_type = data['type']  # TOPUP or QRIS_PAYMENT
        
        # Validate amount
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        # For QRIS payments, check wallet balance
        if payment_type == 'QRIS_PAYMENT':
            if user.wallet_balance < amount:
                return jsonify({'error': 'Insufficient wallet balance'}), 400
        
        # Validate channel code
        valid_channels = [
            'QRIS', 'BCA_VA', 'BNI_VA', 'BRI_VA', 'MANDIRI_VA',
            'CREDIT_CARD', 'DEBIT_CARD', 'OVO', 'GOPAY', 'DANA', 'LINKAJA'
        ]
        
        if channel_code not in valid_channels:
            return jsonify({'error': f'Invalid channel code. Must be one of: {valid_channels}'}), 400
        
        # Create transaction record
        transaction = Transaction(
            user_id=user_id,
            type=payment_type,
            amount=amount,
            status='PENDING',
            description=f"{payment_type} via {channel_code}"
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Create Xendit payment request
        xendit_response = mock_xendit_payment_request(
            amount=float(amount),
            channel_code=channel_code,
            reference_id=transaction.id
        )
        
        # Store Xendit payment request ID
        transaction.xendit_transaction_id = xendit_response['payment_request_id']
        db.session.commit()
        
        logger.info(f"Created payment request for user {user_id}: {xendit_response['payment_request_id']}")
        
        return jsonify({
            'transaction_id': transaction.id,
            'payment_request_id': xendit_response['payment_request_id'],
            'status': xendit_response['status'],
            'channel_code': channel_code,
            'amount': float(amount),
            'currency': 'IDR',
            'actions': xendit_response.get('actions', []),
            'channel_properties': xendit_response.get('channel_properties', {}),
            'expires_at': None  # Mock - would be set by real Xendit API
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating payment request: {str(e)}")
        return jsonify({'error': 'Failed to create payment request', 'details': str(e)}), 500

@xendit_bp.route('/xendit/payment-status/<payment_request_id>', methods=['GET'])
@jwt_required()
def get_payment_status(payment_request_id):
    try:
        user_id = get_jwt_identity()
        
        # Find transaction by Xendit payment request ID
        transaction = Transaction.query.filter_by(
            user_id=user_id,
            xendit_transaction_id=payment_request_id
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Payment request not found'}), 404
        
        # Mock payment status check
        # In real implementation, this would call Xendit API
        return jsonify({
            'payment_request_id': payment_request_id,
            'transaction_id': transaction.id,
            'status': transaction.status,
            'amount': float(transaction.amount),
            'currency': 'IDR',
            'type': transaction.type,
            'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
            'updated_at': transaction.updated_at.isoformat() if transaction.updated_at else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        return jsonify({'error': 'Failed to get payment status', 'details': str(e)}), 500

@xendit_bp.route('/xendit/simulate-payment', methods=['POST'])
def simulate_payment():
    """Simulate payment completion for testing (test mode only)"""
    try:
        data = request.get_json()
        
        if not data.get('payment_request_id'):
            return jsonify({'error': 'payment_request_id is required'}), 400
        
        payment_request_id = data['payment_request_id']
        status = data.get('status', 'SUCCEEDED')  # SUCCEEDED or FAILED
        
        # Find transaction
        transaction = Transaction.query.filter_by(
            xendit_transaction_id=payment_request_id
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Payment request not found'}), 404
        
        # Update transaction status
        transaction.status = 'SUCCESS' if status == 'SUCCEEDED' else 'FAILED'
        
        # If successful top-up, update wallet balance
        if status == 'SUCCEEDED' and transaction.type == 'TOPUP':
            user = User.query.get(transaction.user_id)
            if user:
                user.wallet_balance += transaction.amount
                logger.info(f"Updated wallet balance for user {user.id}: {user.wallet_balance}")
        
        # If successful QRIS payment, deduct from wallet
        elif status == 'SUCCEEDED' and transaction.type == 'QRIS_PAYMENT':
            user = User.query.get(transaction.user_id)
            if user:
                user.wallet_balance -= transaction.amount
                logger.info(f"Deducted from wallet for user {user.id}: {user.wallet_balance}")
        
        db.session.commit()
        
        logger.info(f"Simulated payment {payment_request_id}: {status}")
        
        return jsonify({
            'message': f'Payment {status.lower()} simulated successfully',
            'payment_request_id': payment_request_id,
            'transaction_id': transaction.id,
            'status': transaction.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error simulating payment: {str(e)}")
        return jsonify({'error': 'Failed to simulate payment', 'details': str(e)}), 500

# Real Xendit API integration functions (for future implementation)
def call_xendit_api(endpoint, method='GET', data=None):
    """Call actual Xendit API (placeholder for real implementation)"""
    headers = {
        'Authorization': get_xendit_auth_header(),
        'Content-Type': 'application/json',
        'api-version': '2024-11-11'
    }
    
    url = f"{XENDIT_API_BASE_URL}/{endpoint}"
    
    try:
        if method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=30)
        else:
            response = requests.get(url, headers=headers, timeout=30)
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Xendit API call failed: {str(e)}")
        raise Exception(f"Xendit API error: {str(e)}")

def real_xendit_create_payment_request(amount, channel_code, reference_id):
    """Real Xendit payment request creation (placeholder for actual implementation)"""
    payload = {
        "reference_id": reference_id,
        "type": "PAY",
        "country": "ID",
        "currency": "IDR",
        "request_amount": amount,
        "channel_code": channel_code,
        "capture_method": "AUTOMATIC"
    }
    
    return call_xendit_api('v3/payment_requests', 'POST', payload)

