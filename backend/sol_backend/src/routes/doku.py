from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, Transaction, db
import base64
import uuid
import requests
import os
import logging
import hashlib
import hmac
import json
from datetime import datetime, timezone
from decimal import Decimal
import time

doku_bp = Blueprint('doku', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DOKU API configuration
DOKU_API_BASE_URL = os.getenv('DOKU_API_BASE_URL', 'https://api-sandbox.doku.com')
DOKU_CLIENT_ID = os.getenv('DOKU_CLIENT_ID', 'MCH-0008-1296507211683')
DOKU_CLIENT_SECRET = os.getenv('DOKU_CLIENT_SECRET', 'mock-doku-client-secret')
DOKU_MERCHANT_ID = os.getenv('DOKU_MERCHANT_ID', '2997')
DOKU_TERMINAL_ID = os.getenv('DOKU_TERMINAL_ID', 'K45')

# In-memory token storage (in production, use Redis or database)
_token_cache = {
    'access_token': None,
    'expires_at': 0
}

def get_current_timestamp():
    """Get current timestamp in ISO8601 format"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')

def generate_external_id():
    """Generate unique external ID for requests"""
    return str(int(time.time() * 1000000))

def generate_asymmetric_signature(client_id, timestamp):
    """Generate asymmetric signature for Get Token API"""
    # In real implementation, this would use RSA private key
    # For MVP, we'll use a mock signature
    string_to_sign = f"{client_id}|{timestamp}"
    # Mock signature - in production, use actual RSA private key
    return base64.b64encode(f"mock_signature_{string_to_sign}".encode()).decode()

def generate_symmetric_signature(method, endpoint, access_token, request_body, timestamp):
    """Generate symmetric signature for API requests"""
    # Minify request body
    minified_body = json.dumps(request_body, separators=(',', ':')) if request_body else ""
    
    # Generate SHA-256 hash of request body
    body_hash = hashlib.sha256(minified_body.encode()).hexdigest().lower()
    
    # Create string to sign
    string_to_sign = f"{method}:{endpoint}:{access_token}:{body_hash}:{timestamp}"
    
    # Generate HMAC-SHA512 signature
    signature = hmac.new(
        DOKU_CLIENT_SECRET.encode(),
        string_to_sign.encode(),
        hashlib.sha512
    ).digest()
    
    return base64.b64encode(signature).decode()

def get_access_token():
    """Get access token from DOKU API"""
    global _token_cache
    
    # Check if token is still valid
    current_time = time.time()
    if _token_cache['access_token'] and current_time < _token_cache['expires_at']:
        return _token_cache['access_token']
    
    # Get new token
    timestamp = get_current_timestamp()
    external_id = generate_external_id()
    
    headers = {
        'X-SIGNATURE': generate_asymmetric_signature(DOKU_CLIENT_ID, timestamp),
        'X-TIMESTAMP': timestamp,
        'X-CLIENT-KEY': DOKU_CLIENT_ID,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'grantType': 'client_credentials'
    }
    
    try:
        # For MVP, return mock token
        # In production, make actual API call to DOKU
        mock_token = f"mock_token_{int(time.time())}"
        _token_cache['access_token'] = mock_token
        _token_cache['expires_at'] = current_time + 900  # 15 minutes
        
        logger.info(f"Generated new DOKU access token: {mock_token[:20]}...")
        return mock_token
        
    except Exception as e:
        logger.error(f"Failed to get DOKU access token: {str(e)}")
        raise Exception(f"DOKU authentication failed: {str(e)}")

def create_virtual_account(amount, reference_id):
    """Create virtual account using DOKU API"""
    access_token = get_access_token()
    timestamp = get_current_timestamp()
    external_id = generate_external_id()
    
    # For MVP, return mock VA response
    # In production, make actual API call to DOKU
    va_number = f"8808{str(uuid.uuid4())[:8]}"
    
    return {
        'responseCode': '2004700',
        'responseMessage': 'Request has been processed successfully',
        'virtualAccountInfo': {
            'virtualAccountNumber': va_number,
            'bankCode': 'BCA',
            'amount': amount,
            'expiredTime': '2024-12-31T23:59:59+07:00'
        },
        'partnerReferenceNo': reference_id,
        'referenceNo': f"doku_{reference_id}"
    }

def generate_qris(amount, reference_id):
    """Generate QRIS using DOKU API"""
    access_token = get_access_token()
    timestamp = get_current_timestamp()
    external_id = generate_external_id()
    
    endpoint = '/snap-adapter/b2b/v1.0/qr/qr-mpm-generate'
    
    payload = {
        'partnerReferenceNo': reference_id,
        'amount': {
            'value': f"{amount:.2f}",
            'currency': 'IDR'
        },
        'feeAmount': {
            'value': '0.00',
            'currency': 'IDR'
        },
        'merchantId': DOKU_MERCHANT_ID,
        'terminalId': DOKU_TERMINAL_ID,
        'validityPeriod': '2024-12-31T23:59:59+07:00',
        'additionalInfo': {
            'postalCode': 13120,
            'feeType': 2
        }
    }
    
    headers = {
        'X-PARTNER-ID': DOKU_CLIENT_ID,
        'X-EXTERNAL-ID': external_id,
        'X-SIGNATURE': generate_symmetric_signature('POST', endpoint, access_token, payload, timestamp),
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # For MVP, return mock QRIS response
    # In production, make actual API call to DOKU
    qr_content = f"00020101021226530012COM.DOKU.WWW0118936008990000{reference_id}020429970303UMI51440014ID.CO.QRIS.WWW0215ID20200622029970303UMI52045411530336054{amount:07.2f}5502025606500.525802ID5911Green Pages6007Jakarta61051312062430703K455032{reference_id}6304F6EA"
    
    return {
        'responseCode': '2004700',
        'responseMessage': 'Request has been processed successfully',
        'referenceNo': f"doku_{reference_id}",
        'partnerReferenceNo': reference_id,
        'qrContent': qr_content,
        'terminalId': DOKU_TERMINAL_ID,
        'additionalInfo': {
            'validityPeriod': '2024-12-31T23:59:59+07:00'
        }
    }

def query_qris_status(reference_id, partner_reference_id):
    """Query QRIS payment status"""
    access_token = get_access_token()
    timestamp = get_current_timestamp()
    external_id = generate_external_id()
    
    endpoint = '/snap-adapter/b2b/v1.0/qr/qr-mpm-query'
    
    payload = {
        'originalReferenceNo': reference_id,
        'originalPartnerReferenceNo': partner_reference_id,
        'serviceCode': '47',
        'merchantId': DOKU_MERCHANT_ID
    }
    
    headers = {
        'X-PARTNER-ID': DOKU_CLIENT_ID,
        'X-TIMESTAMP': timestamp,
        'X-EXTERNAL-ID': external_id,
        'X-SIGNATURE': generate_symmetric_signature('POST', endpoint, access_token, payload, timestamp),
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # For MVP, return mock status response
    # In production, make actual API call to DOKU
    return {
        'responseCode': '2004700',
        'responseMessage': 'Request has been processed successfully',
        'originalReferenceNo': reference_id,
        'originalPartnerReferenceNo': partner_reference_id,
        'serviceCode': '47',
        'latestTransactionStatus': '00',
        'transactionStatusDesc': 'Success',
        'paidTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S+07:00'),
        'amount': {
            'value': 1000,
            'currency': 'IDR'
        },
        'additionalInfo': {
            'approvalCode': '328591',
            'convenienceFee': 'C00000000',
            'issuerId': '93600014',
            'issuerName': 'BCA',
            'terminalId': DOKU_TERMINAL_ID,
            'customerName': 'JOHN DOE'
        }
    }

@doku_bp.route('/doku/virtual-account', methods=['POST'])
@jwt_required()
def create_va_payment():
    """Create virtual account for top-up"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check KYC status
        if user.kyc_status != 'APPROVED':
            return jsonify({'error': 'KYC verification required before top-up'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('amount') or not data.get('payment_method'):
            return jsonify({'error': 'Amount and payment_method are required'}), 400
        
        amount = Decimal(str(data['amount']))
        payment_method = data['payment_method']
        
        # Validate amount
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        if amount > 10000000:  # 10 million IDR limit
            return jsonify({'error': 'Amount exceeds maximum limit'}), 400
        
        # Create transaction record
        transaction = Transaction(
            user_id=user_id,
            type='TOPUP',
            amount=amount,
            status='PENDING',
            description=f"Top-up via {payment_method}"
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Create DOKU virtual account
        doku_response = create_virtual_account(
            amount=float(amount),
            reference_id=str(transaction.id)
        )
        
        # Store DOKU reference
        transaction.xendit_transaction_id = doku_response['referenceNo']  # Reuse field for DOKU reference
        db.session.commit()
        
        logger.info(f"Created DOKU VA for user {user_id}: {doku_response['referenceNo']}")
        
        return jsonify({
            'transaction_id': transaction.id,
            'reference_no': doku_response['referenceNo'],
            'partner_reference_no': doku_response['partnerReferenceNo'],
            'amount': float(amount),
            'payment_method': payment_method,
            'status': 'PENDING',
            'va_number': doku_response['virtualAccountInfo']['virtualAccountNumber'],
            'bank_code': doku_response['virtualAccountInfo']['bankCode'],
            'expired_time': doku_response['virtualAccountInfo']['expiredTime']
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating DOKU VA: {str(e)}")
        return jsonify({'error': 'Failed to create virtual account', 'details': str(e)}), 500

@doku_bp.route('/doku/qris-generate', methods=['POST'])
@jwt_required()
def generate_qris_payment():
    """Generate QRIS for payment"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check KYC status
        if user.kyc_status != 'APPROVED':
            return jsonify({'error': 'KYC verification required before payment'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('amount'):
            return jsonify({'error': 'Amount is required'}), 400
        
        amount = Decimal(str(data['amount']))
        
        # Validate amount
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        # Check wallet balance
        if user.wallet_balance < amount:
            return jsonify({'error': 'Insufficient wallet balance'}), 400
        
        # Create transaction record
        transaction = Transaction(
            user_id=user_id,
            type='QRIS_PAYMENT',
            amount=amount,
            status='PENDING',
            description=f"QRIS payment"
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Generate DOKU QRIS
        doku_response = generate_qris(
            amount=float(amount),
            reference_id=str(transaction.id)
        )
        
        # Store DOKU reference
        transaction.xendit_transaction_id = doku_response['referenceNo']  # Reuse field for DOKU reference
        db.session.commit()
        
        logger.info(f"Generated DOKU QRIS for user {user_id}: {doku_response['referenceNo']}")
        
        return jsonify({
            'transaction_id': transaction.id,
            'reference_no': doku_response['referenceNo'],
            'partner_reference_no': doku_response['partnerReferenceNo'],
            'amount': float(amount),
            'status': 'PENDING',
            'qr_content': doku_response['qrContent'],
            'terminal_id': doku_response['terminalId'],
            'validity_period': doku_response['additionalInfo']['validityPeriod']
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error generating DOKU QRIS: {str(e)}")
        return jsonify({'error': 'Failed to generate QRIS', 'details': str(e)}), 500

@doku_bp.route('/doku/qris-pay', methods=['POST'])
@jwt_required()
def process_qris_payment():
    """Process QRIS payment (simulate payment completion)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('qr_content') or not data.get('amount'):
            return jsonify({'error': 'QR content and amount are required'}), 400
        
        amount = Decimal(str(data['amount']))
        
        # Validate amount
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        # Check wallet balance
        if user.wallet_balance < amount:
            return jsonify({'error': 'Insufficient wallet balance'}), 400
        
        # Create transaction record
        transaction = Transaction(
            user_id=user_id,
            type='QRIS_PAYMENT',
            amount=amount,
            status='SUCCESS',  # Simulate immediate success
            description=f"QRIS payment to merchant"
        )
        
        # Deduct from wallet balance
        user.wallet_balance -= amount
        
        db.session.add(transaction)
        db.session.commit()
        
        logger.info(f"Processed DOKU QRIS payment for user {user_id}: {amount}")
        
        return jsonify({
            'transaction_id': transaction.id,
            'status': transaction.status,
            'amount': float(amount),
            'remaining_balance': float(user.wallet_balance),
            'qr_content': data['qr_content']
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing DOKU QRIS payment: {str(e)}")
        return jsonify({'error': 'Failed to process QRIS payment', 'details': str(e)}), 500

@doku_bp.route('/doku/payment-status/<reference_no>', methods=['GET'])
@jwt_required()
def get_payment_status(reference_no):
    """Get payment status from DOKU"""
    try:
        user_id = get_jwt_identity()
        
        # Find transaction by DOKU reference
        transaction = Transaction.query.filter_by(
            user_id=user_id,
            xendit_transaction_id=reference_no  # Reused field for DOKU reference
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Payment not found'}), 404
        
        return jsonify({
            'reference_no': reference_no,
            'transaction_id': transaction.id,
            'status': transaction.status,
            'amount': float(transaction.amount),
            'currency': 'IDR',
            'type': transaction.type,
            'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
            'updated_at': transaction.updated_at.isoformat() if transaction.updated_at else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting DOKU payment status: {str(e)}")
        return jsonify({'error': 'Failed to get payment status', 'details': str(e)}), 500

@doku_bp.route('/doku/simulate-payment', methods=['POST'])
def simulate_payment():
    """Simulate payment completion for testing (test mode only)"""
    try:
        data = request.get_json()
        
        if not data.get('reference_no'):
            return jsonify({'error': 'reference_no is required'}), 400
        
        reference_no = data['reference_no']
        status = data.get('status', 'SUCCESS')  # SUCCESS or FAILED
        
        # Find transaction
        transaction = Transaction.query.filter_by(
            xendit_transaction_id=reference_no  # Reused field for DOKU reference
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Update transaction status
        transaction.status = status
        
        # If successful top-up, update wallet balance
        if status == 'SUCCESS' and transaction.type == 'TOPUP':
            user = User.query.get(transaction.user_id)
            if user:
                user.wallet_balance += transaction.amount
                logger.info(f"Updated wallet balance for user {user.id}: {user.wallet_balance}")
        
        db.session.commit()
        
        logger.info(f"Simulated DOKU payment {reference_no}: {status}")
        
        return jsonify({
            'message': f'Payment {status.lower()} simulated successfully',
            'reference_no': reference_no,
            'transaction_id': transaction.id,
            'status': transaction.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error simulating DOKU payment: {str(e)}")
        return jsonify({'error': 'Failed to simulate payment', 'details': str(e)}), 500

