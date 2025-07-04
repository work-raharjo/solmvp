from flask import Blueprint, jsonify, request
from src.models.user import User, Transaction, db
from decimal import Decimal
import logging

webhooks_bp = Blueprint('webhooks', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@webhooks_bp.route('/webhooks/privy', methods=['POST'])
def privy_webhook():
    try:
        data = request.get_json()
        logger.info(f"Received Privy webhook: {data}")
        
        # Extract relevant information from Privy webhook
        # This is a mock implementation - actual Privy webhook structure may differ
        kyc_id = data.get('kyc_id')
        status = data.get('status')  # e.g., 'approved', 'rejected'
        user_identifier = data.get('user_identifier')  # Could be email or passport number
        
        if not kyc_id or not status or not user_identifier:
            logger.error("Missing required fields in Privy webhook")
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find user by email or passport number
        user = User.query.filter(
            (User.email == user_identifier) | 
            (User.passport_number == user_identifier)
        ).first()
        
        if not user:
            logger.error(f"User not found for identifier: {user_identifier}")
            return jsonify({'error': 'User not found'}), 404
        
        # Update user KYC status
        if status.lower() == 'approved':
            user.kyc_status = 'APPROVED'
        elif status.lower() == 'rejected':
            user.kyc_status = 'REJECTED'
        else:
            user.kyc_status = 'PENDING'
        
        user.privy_kyc_id = kyc_id
        
        db.session.commit()
        
        logger.info(f"Updated KYC status for user {user.id}: {user.kyc_status}")
        
        return jsonify({'message': 'KYC status updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing Privy webhook: {str(e)}")
        return jsonify({'error': 'Failed to process webhook', 'details': str(e)}), 500

@webhooks_bp.route('/webhooks/xendit', methods=['POST'])
def xendit_webhook():
    try:
        data = request.get_json()
        logger.info(f"Received Xendit webhook: {data}")
        
        # Extract relevant information from Xendit webhook
        # This is a mock implementation - actual Xendit webhook structure may differ
        external_id = data.get('external_id')  # Should match our transaction ID
        status = data.get('status')  # e.g., 'PAID', 'EXPIRED', 'FAILED'
        amount = data.get('amount')
        payment_method = data.get('payment_method')
        
        if not external_id or not status:
            logger.error("Missing required fields in Xendit webhook")
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find transaction by ID
        transaction = Transaction.query.get(external_id)
        
        if not transaction:
            logger.error(f"Transaction not found: {external_id}")
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Update transaction status
        if status.upper() == 'PAID':
            transaction.status = 'SUCCESS'
            
            # If it's a top-up transaction, update user wallet balance
            if transaction.type == 'TOPUP':
                user = User.query.get(transaction.user_id)
                if user:
                    user.wallet_balance += transaction.amount
                    logger.info(f"Updated wallet balance for user {user.id}: {user.wallet_balance}")
                    
        elif status.upper() in ['EXPIRED', 'FAILED']:
            transaction.status = 'FAILED'
        
        # Store Xendit transaction ID for reference
        transaction.xendit_transaction_id = data.get('id')
        
        db.session.commit()
        
        logger.info(f"Updated transaction {transaction.id}: {transaction.status}")
        
        return jsonify({'message': 'Transaction status updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing Xendit webhook: {str(e)}")
        return jsonify({'error': 'Failed to process webhook', 'details': str(e)}), 500

@webhooks_bp.route('/webhooks/test', methods=['POST'])
def test_webhook():
    """Test endpoint for webhook functionality"""
    try:
        data = request.get_json()
        logger.info(f"Received test webhook: {data}")
        
        return jsonify({
            'message': 'Test webhook received successfully',
            'received_data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing test webhook: {str(e)}")
        return jsonify({'error': 'Failed to process test webhook', 'details': str(e)}), 500

