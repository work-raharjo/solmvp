from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.user import User, Transaction, Admin, db
import bcrypt
from decimal import Decimal

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find admin by username
        admin = Admin.query.filter_by(username=data['username']).first()
        
        if not admin:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Check password
        if not bcrypt.checkpw(data['password'].encode('utf-8'), admin.password_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create access token with admin identity
        access_token = create_access_token(identity=f"admin:{admin.id}")
        
        return jsonify({
            'message': 'Admin login successful',
            'admin_id': admin.id,
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Admin login failed', 'details': str(e)}), 500

def admin_required(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        identity = get_jwt_identity()
        if not identity.startswith('admin:'):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    try:
        # Get query parameters for pagination and filtering
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        kyc_status = request.args.get('kyc_status')
        
        # Build query
        query = User.query
        
        if kyc_status:
            query = query.filter_by(kyc_status=kyc_status)
        
        # Apply pagination
        users = query.order_by(User.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'users': [
                {
                    'user_id': user.id,
                    'full_name': user.full_name,
                    'email': user.email,
                    'passport_number': user.passport_number,
                    'kyc_status': user.kyc_status,
                    'wallet_balance': float(user.wallet_balance),
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
                for user in users.items
            ],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get users', 'details': str(e)}), 500

@admin_bp.route('/admin/transactions', methods=['GET'])
@admin_required
def get_all_transactions():
    try:
        # Get query parameters for pagination and filtering
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        transaction_type = request.args.get('type')
        status = request.args.get('status')
        
        # Build query
        query = Transaction.query
        
        if transaction_type:
            query = query.filter_by(type=transaction_type)
        
        if status:
            query = query.filter_by(status=status)
        
        # Apply pagination
        transactions = query.order_by(Transaction.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'transactions': [
                {
                    'transaction_id': transaction.id,
                    'user_id': transaction.user_id,
                    'user_name': transaction.user.full_name if transaction.user else None,
                    'type': transaction.type,
                    'amount': float(transaction.amount),
                    'currency': transaction.currency,
                    'status': transaction.status,
                    'description': transaction.description,
                    'created_at': transaction.created_at.isoformat() if transaction.created_at else None
                }
                for transaction in transactions.items
            ],
            'total': transactions.total,
            'pages': transactions.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get transactions', 'details': str(e)}), 500

@admin_bp.route('/admin/refund', methods=['POST'])
@admin_required
def process_refund():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('transaction_id') or not data.get('amount'):
            return jsonify({'error': 'Transaction ID and amount are required'}), 400
        
        # Find the original transaction
        original_transaction = Transaction.query.get(data['transaction_id'])
        
        if not original_transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Validate refund amount
        refund_amount = Decimal(str(data['amount']))
        if refund_amount <= 0 or refund_amount > original_transaction.amount:
            return jsonify({'error': 'Invalid refund amount'}), 400
        
        # Get user
        user = User.query.get(original_transaction.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create refund transaction
        refund_transaction = Transaction(
            user_id=user.id,
            type='REFUND',
            amount=refund_amount,
            status='SUCCESS',
            description=f"Refund for transaction {original_transaction.id}"
        )
        
        # Update user wallet balance
        user.wallet_balance += refund_amount
        
        db.session.add(refund_transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Refund processed successfully',
            'refund_transaction_id': refund_transaction.id,
            'amount': float(refund_amount),
            'user_new_balance': float(user.wallet_balance)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to process refund', 'details': str(e)}), 500

@admin_bp.route('/admin/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    try:
        # Get basic statistics
        total_users = User.query.count()
        approved_users = User.query.filter_by(kyc_status='APPROVED').count()
        pending_kyc = User.query.filter_by(kyc_status='PENDING').count()
        
        total_transactions = Transaction.query.count()
        successful_transactions = Transaction.query.filter_by(status='SUCCESS').count()
        
        # Get total wallet balance across all users
        total_wallet_balance = db.session.query(db.func.sum(User.wallet_balance)).scalar() or 0
        
        return jsonify({
            'total_users': total_users,
            'approved_users': approved_users,
            'pending_kyc': pending_kyc,
            'total_transactions': total_transactions,
            'successful_transactions': successful_transactions,
            'total_wallet_balance': float(total_wallet_balance)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboard stats', 'details': str(e)}), 500

