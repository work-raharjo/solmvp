# Sol MVP API Documentation

## Overview

The Sol MVP API provides a comprehensive backend service for a passport-based QRIS wallet application designed for foreign tourists in Indonesia. The API handles user authentication, KYC verification through Privy, payment processing via Xendit, and administrative functions.

**Base URL**: `http://localhost:5000/api`  
**Authentication**: JWT Bearer Token  
**Content-Type**: `application/json` (unless specified otherwise)

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Error Responses

All endpoints may return the following error responses:

```json
{
  "error": "Error message description",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

Common HTTP status codes:
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Authentication Endpoints

### POST /auth/register

Register a new user account with passport information.

**Request Body:**
```json
{
  "email": "john.smith@example.com",
  "password": "securepassword123",
  "passport_number": "A12345678",
  "full_name": "John Smith",
  "phone_number": "+1234567890"
}
```

**Validation Rules:**
- `email`: Valid email format, unique
- `password`: Minimum 8 characters
- `passport_number`: Alphanumeric, 6-15 characters, unique
- `full_name`: 2-100 characters
- `phone_number`: Valid international format

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1,
  "kyc_status": "PENDING",
  "expires_in": 86400
}
```

**Error Responses:**
- `400` - Email or passport number already exists
- `422` - Validation errors

### POST /auth/login

Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "john.smith@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1,
  "kyc_status": "APPROVED",
  "wallet_balance": 500000.00,
  "expires_in": 86400
}
```

**Error Responses:**
- `401` - Invalid credentials

### GET /auth/profile

Get current user profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "user_id": 1,
  "email": "john.smith@example.com",
  "full_name": "John Smith",
  "passport_number": "A12345678",
  "phone_number": "+1234567890",
  "kyc_status": "APPROVED",
  "wallet_balance": 500000.00,
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-20T14:22:00Z"
}
```

## KYC Verification Endpoints

### POST /privy/verify

Submit passport and selfie images for KYC verification.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
- `passport_image`: File (JPEG/PNG, max 5MB)
- `selfie_image`: File (JPEG/PNG, max 5MB)

**Response (200 OK):**
```json
{
  "message": "KYC verification initiated",
  "verification_id": "privy_verification_123",
  "status": "PROCESSING",
  "estimated_completion": "2024-01-20T15:00:00Z"
}
```

**Error Responses:**
- `400` - Invalid file format or size
- `409` - KYC already completed

### GET /privy/status

Get current KYC verification status.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "kyc_status": "APPROVED",
  "verification_id": "privy_verification_123",
  "submitted_at": "2024-01-20T14:30:00Z",
  "completed_at": "2024-01-20T14:45:00Z",
  "verification_details": {
    "passport_verified": true,
    "selfie_verified": true,
    "liveness_check": true,
    "confidence_score": 0.95
  }
}
```

## Wallet Management Endpoints

### GET /wallet/balance

Get current wallet balance and recent transactions.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "balance": 500000.00,
  "currency": "IDR",
  "last_updated": "2024-01-20T14:30:00Z",
  "recent_transactions": [
    {
      "id": "tx_001",
      "type": "QRIS_PAYMENT",
      "amount": -25000.00,
      "merchant": "Starbucks Coffee",
      "status": "SUCCESS",
      "created_at": "2024-01-20T13:15:00Z"
    }
  ]
}
```

### POST /wallet/topup

Initiate wallet top-up using various payment methods.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "amount": 100000,
  "payment_method": "BCA_VA",
  "return_url": "https://yourapp.com/topup/success",
  "callback_url": "https://yourapp.com/webhook/topup"
}
```

**Payment Methods:**
- `BCA_VA` - BCA Virtual Account
- `MANDIRI_VA` - Mandiri Virtual Account
- `BNI_VA` - BNI Virtual Account
- `CREDIT_CARD` - Credit/Debit Card
- `GOPAY` - GoPay E-wallet
- `OVO` - OVO E-wallet
- `DANA` - DANA E-wallet

**Response (201 Created):**
```json
{
  "transaction_id": "tx_topup_001",
  "payment_id": "xendit_payment_123",
  "amount": 100000,
  "payment_method": "BCA_VA",
  "status": "PENDING",
  "payment_details": {
    "va_number": "1234567890123456",
    "bank_code": "BCA",
    "expiry_date": "2024-01-21T14:30:00Z"
  },
  "payment_url": "https://checkout.xendit.co/payment/123"
}
```

### POST /wallet/qris-payment

Process QRIS payment to merchant.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "qr_code": "00020101021226280014ID.CO.QRIS.WWW0215ID20220000000010303UMI51440014ID.LINKAJA.WWW0215901234567890203UMI5204481253033605802ID5909MERCHANT6006JAKARTA61051234562070703A0163044B2D",
  "amount": 25000,
  "description": "Coffee purchase"
}
```

**Response (200 OK):**
```json
{
  "transaction_id": "tx_qris_001",
  "payment_id": "xendit_qris_123",
  "amount": 25000,
  "merchant_name": "Starbucks Coffee",
  "merchant_location": "Jakarta",
  "status": "SUCCESS",
  "remaining_balance": 475000.00,
  "created_at": "2024-01-20T13:15:00Z"
}
```

**Error Responses:**
- `400` - Invalid QR code format
- `402` - Insufficient balance
- `422` - Payment processing failed

### GET /wallet/transactions

Get transaction history with pagination and filtering.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `type`: Filter by transaction type (`TOPUP`, `QRIS_PAYMENT`, `REFUND`)
- `status`: Filter by status (`PENDING`, `SUCCESS`, `FAILED`)
- `start_date`: Start date filter (ISO 8601)
- `end_date`: End date filter (ISO 8601)

**Example Request:**
```
GET /wallet/transactions?page=1&limit=10&type=QRIS_PAYMENT&status=SUCCESS
```

**Response (200 OK):**
```json
{
  "transactions": [
    {
      "id": "tx_001",
      "type": "QRIS_PAYMENT",
      "amount": -25000.00,
      "status": "SUCCESS",
      "payment_method": "QRIS",
      "merchant_name": "Starbucks Coffee",
      "description": "Coffee purchase",
      "created_at": "2024-01-20T13:15:00Z",
      "updated_at": "2024-01-20T13:15:30Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 47,
    "items_per_page": 10
  }
}
```

## Xendit Integration Endpoints

### POST /xendit/create-payment

Create a new payment request via Xendit.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "amount": 100000,
  "payment_method": "BCA_VA",
  "description": "Wallet top-up",
  "customer": {
    "name": "John Smith",
    "email": "john.smith@example.com",
    "phone": "+1234567890"
  }
}
```

**Response (201 Created):**
```json
{
  "payment_id": "xendit_payment_123",
  "status": "PENDING",
  "payment_url": "https://checkout.xendit.co/payment/123",
  "payment_details": {
    "va_number": "1234567890123456",
    "bank_code": "BCA",
    "expiry_date": "2024-01-21T14:30:00Z"
  }
}
```

### POST /xendit/qris

Generate QRIS payment request.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "amount": 25000,
  "merchant_qr": "qris_merchant_code",
  "description": "Payment to merchant"
}
```

**Response (200 OK):**
```json
{
  "qris_id": "qris_123",
  "status": "ACTIVE",
  "qr_string": "00020101021226280014ID.CO.QRIS...",
  "amount": 25000,
  "expiry_date": "2024-01-20T14:00:00Z"
}
```

## Webhook Endpoints

### POST /webhooks/privy

Receive KYC status updates from Privy.

**Headers:**
```
X-Privy-Signature: <signature>
Content-Type: application/json
```

**Request Body:**
```json
{
  "verification_id": "privy_verification_123",
  "user_id": "1",
  "status": "APPROVED",
  "verification_result": {
    "passport_verified": true,
    "selfie_verified": true,
    "liveness_check": true,
    "confidence_score": 0.95
  },
  "timestamp": "2024-01-20T14:45:00Z"
}
```

**Response (200 OK):**
```json
{
  "message": "Webhook processed successfully"
}
```

### POST /webhooks/xendit

Receive payment status updates from Xendit.

**Headers:**
```
X-Callback-Token: <webhook_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "id": "xendit_payment_123",
  "external_id": "tx_topup_001",
  "status": "PAID",
  "amount": 100000,
  "paid_amount": 100000,
  "payment_method": "BCA_VA",
  "paid_at": "2024-01-20T14:30:00Z",
  "user_id": "1"
}
```

**Response (200 OK):**
```json
{
  "message": "Payment webhook processed successfully"
}
```

## Admin Endpoints

### POST /admin/login

Authenticate admin user.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin_password"
}
```

**Response (200 OK):**
```json
{
  "message": "Admin login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "admin_id": 1,
  "role": "admin",
  "expires_in": 86400
}
```

### GET /admin/users

Get all users with pagination and filtering (admin only).

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)
- `kyc_status`: Filter by KYC status
- `search`: Search by name, email, or passport number

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": 1,
      "email": "john.smith@example.com",
      "full_name": "John Smith",
      "passport_number": "A12345678",
      "kyc_status": "APPROVED",
      "wallet_balance": 500000.00,
      "created_at": "2024-01-15T10:30:00Z",
      "last_login": "2024-01-20T14:22:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "total_items": 200,
    "items_per_page": 20
  }
}
```

### GET /admin/transactions

Get all transactions with filtering (admin only).

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Query Parameters:**
- `page`: Page number
- `limit`: Items per page
- `user_id`: Filter by user ID
- `status`: Filter by transaction status
- `type`: Filter by transaction type
- `start_date`: Start date filter
- `end_date`: End date filter

**Response (200 OK):**
```json
{
  "transactions": [
    {
      "id": "tx_001",
      "user_id": 1,
      "user_name": "John Smith",
      "type": "QRIS_PAYMENT",
      "amount": 25000,
      "status": "SUCCESS",
      "payment_method": "QRIS",
      "merchant_name": "Starbucks Coffee",
      "created_at": "2024-01-20T13:15:00Z",
      "xendit_id": "xendit_payment_123"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 25,
    "total_items": 500,
    "items_per_page": 20
  }
}
```

### POST /admin/refund

Process manual refund (admin only).

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Request Body:**
```json
{
  "transaction_id": "tx_001",
  "amount": 25000,
  "reason": "Customer complaint - merchant error"
}
```

**Response (200 OK):**
```json
{
  "message": "Refund processed successfully",
  "refund_id": "refund_001",
  "amount": 25000,
  "status": "PROCESSING",
  "estimated_completion": "2024-01-20T16:00:00Z"
}
```

## Health Check Endpoint

### GET /health

Check API health status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T14:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "privy": "available",
    "xendit": "available"
  }
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authentication endpoints**: 5 requests per minute per IP
- **General endpoints**: 100 requests per minute per user
- **Admin endpoints**: 200 requests per minute per admin
- **Webhook endpoints**: 1000 requests per minute per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642694400
```

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_CREDENTIALS` | Invalid email or password |
| `USER_NOT_FOUND` | User account not found |
| `INSUFFICIENT_BALANCE` | Wallet balance too low |
| `KYC_REQUIRED` | KYC verification required |
| `KYC_PENDING` | KYC verification in progress |
| `KYC_REJECTED` | KYC verification failed |
| `PAYMENT_FAILED` | Payment processing failed |
| `INVALID_QR_CODE` | Invalid QRIS code format |
| `MERCHANT_UNAVAILABLE` | Merchant not available |
| `TRANSACTION_NOT_FOUND` | Transaction not found |
| `VALIDATION_ERROR` | Request validation failed |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Internal server error |

## SDK and Libraries

### JavaScript/Node.js
```javascript
const SolAPI = require('sol-api-client');

const client = new SolAPI({
  baseURL: 'http://localhost:5000/api',
  apiKey: 'your-api-key'
});

// Register user
const user = await client.auth.register({
  email: 'user@example.com',
  password: 'password',
  passport_number: 'A12345678',
  full_name: 'John Smith'
});
```

### Python
```python
from sol_api import SolClient

client = SolClient(
    base_url='http://localhost:5000/api',
    api_key='your-api-key'
)

# Get wallet balance
balance = client.wallet.get_balance()
```

## Testing

### Postman Collection

A comprehensive Postman collection is available with all endpoints pre-configured:
- Authentication flows
- KYC verification process
- Payment scenarios
- Admin operations
- Error handling examples

### Test Environment

- **Base URL**: `http://localhost:5000/api`
- **Test User**: john.smith@example.com / password123
- **Test Admin**: admin / admin
- **Mock Integrations**: Privy and Xendit responses are mocked for testing

---

For additional support or questions about the API, please contact the development team.

