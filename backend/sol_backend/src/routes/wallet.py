from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, Transaction, db
from decimal import Decimal

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/wallet/balance', methods=['GET'])
@jwt_required()
def get_balance():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'balance': float(user.wallet_balance),
            'currency': 'IDR'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get balance', 'details': str(e)}), 500

@wallet_bp.route('/wallet/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters for pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Query transactions with pagination
        transactions = Transaction.query.filter_by(user_id=user_id)\
            .order_by(Transaction.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'transactions': [transaction.to_dict() for transaction in transactions.items],
            'total': transactions.total,
            'pages': transactions.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get transactions', 'details': str(e)}), 500

@wallet_bp.route('/wallet/topup', methods=['POST'])
@jwt_required()
def initiate_topup():
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
        
        # Map payment method to Xendit channel code
        channel_mapping = {
            'VA': 'BCA_VA',  # Default to BCA VA
            'BCA_VA': 'BCA_VA',
            'BNI_VA': 'BNI_VA',
            'BRI_VA': 'BRI_VA',
            'MANDIRI_VA': 'MANDIRI_VA',
            'CC': 'CREDIT_CARD',
            'CREDIT_CARD': 'CREDIT_CARD',
            'E-WALLET': 'OVO',  # Default to OVO
            'OVO': 'OVO',
            'GOPAY': 'GOPAY',
            'DANA': 'DANA',
            'LINKAJA': 'LINKAJA'
        }
        
        channel_code = channel_mapping.get(payment_method)
        if not channel_code:
            return jsonify({'error': f'Invalid payment method: {payment_method}'}), 400
        
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
        
        # Create DOKU virtual account (replacing Xendit)
        from src.routes.doku import create_virtual_account
        doku_response = create_virtual_account(
            amount=float(amount),
            reference_id=str(transaction.id)
        )
        
        # Store DOKU reference
        transaction.xendit_transaction_id = doku_response['referenceNo']
        db.session.commit()
        
        # Prepare response based on payment method
        response_data = {
            'transaction_id': transaction.id,
            'reference_no': doku_response['referenceNo'],
            'partner_reference_no': doku_response['partnerReferenceNo'],
            'amount': float(amount),
            'payment_method': payment_method,
            'status': 'PENDING'
        }
        
        # Add method-specific data for Virtual Account
        if 'VA' in payment_method or payment_method == 'VA':
            response_data['va_number'] = doku_response['virtualAccountInfo']['virtualAccountNumber']
            response_data['bank_code'] = doku_response['virtualAccountInfo']['bankCode']
            response_data['expired_time'] = doku_response['virtualAccountInfo']['expiredTime']
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to initiate top-up', 'details': str(e)}), 500

@wallet_bp.route('/wallet/qris-pay', methods=['POST'])
@jwt_required()
def qris_payment():
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
        if not data.get('amount') or not data.get('merchant_qris_code'):
            return jsonify({'error': 'Amount and merchant_qris_code are required'}), 400
        
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
            description=f"QRIS payment to merchant"
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Create DOKU QRIS payment (replacing Xendit)
        from src.routes.doku import generate_qris
        doku_response = generate_qris(
            amount=float(amount),
            reference_id=str(transaction.id)
        )
        
        # Store DOKU reference
        transaction.xendit_transaction_id = doku_response['referenceNo']
        
        # For QRIS payments, simulate immediate success (in real implementation, this would be handled by webhook)
        transaction.status = 'SUCCESS'
        user.wallet_balance -= amount
        
        db.session.commit()
        
        return jsonify({
            'transaction_id': transaction.id,
            'reference_no': doku_response['referenceNo'],
            'partner_reference_no': doku_response['partnerReferenceNo'],
            'status': transaction.status,
            'amount': float(amount),
            'remaining_balance': float(user.wallet_balance),
            'qr_content': doku_response['qrContent'],
            'merchant_qris_code': data['merchant_qris_code']
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to process QRIS payment', 'details': str(e)}), 500

