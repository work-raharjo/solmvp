# Sol MVP API Design

## 1. Data Models

### User
- `id`: UUID (Primary Key)
- `passport_number`: String (Unique)
- `full_name`: String
- `email`: String (Unique)
- `phone_number`: String
- `kyc_status`: Enum (PENDING, APPROVED, REJECTED)
- `wallet_balance`: Decimal (Default: 0.00)
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Transaction
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to User)
- `type`: Enum (TOPUP, QRIS_PAYMENT, REFUND)
- `amount`: Decimal
- `currency`: String (e.g., IDR)
- `status`: Enum (PENDING, SUCCESS, FAILED)
- `xendit_transaction_id`: String (Optional)
- `privy_kyc_id`: String (Optional)
- `description`: String
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Admin
- `id`: UUID (Primary Key)
- `username`: String (Unique)
- `password_hash`: String
- `email`: String
- `created_at`: Timestamp
- `updated_at`: Timestamp

## 2. API Endpoints

### User Management
- `POST /api/v1/auth/register`: User registration with passport and selfie upload.
  - Request: `{ passport_number, full_name, email, phone_number, selfie_image, passport_image }`
  - Response: `{ user_id, kyc_status }`
- `POST /api/v1/auth/login`: User login.
  - Request: `{ email, password }`
  - Response: `{ token, user_id, kyc_status }`
- `GET /api/v1/users/{user_id}/profile`: Get user profile and KYC status.
  - Response: `{ user_id, full_name, email, kyc_status, wallet_balance }`

### Wallet & Transactions
- `POST /api/v1/wallet/topup`: Initiate wallet top-up via Xendit.
  - Request: `{ user_id, amount, payment_method (VA, CC, E-WALLET) }`
  - Response: `{ transaction_id, payment_url/va_number }`
- `POST /api/v1/wallet/qris-pay`: Initiate QRIS payment via Xendit.
  - Request: `{ user_id, amount, merchant_qris_code }`
  - Response: `{ transaction_id, status }`
- `GET /api/v1/wallet/transactions`: Get user transaction history.
  - Response: `[ { transaction_id, type, amount, status, description, created_at } ]`
- `GET /api/v1/wallet/balance`: Get user wallet balance.
  - Response: `{ balance }`

### Webhooks
- `POST /api/v1/webhooks/privy`: Privy webhook for KYC status updates.
  - Request: `{ privy_payload }`
  - Response: `200 OK`
- `POST /api/v1/webhooks/xendit`: Xendit webhook for transaction status updates.
  - Request: `{ xendit_payload }`
  - Response: `200 OK`

### Admin Dashboard
- `POST /api/v1/admin/login`: Admin login.
  - Request: `{ username, password }`
  - Response: `{ token }`
- `GET /api/v1/admin/users`: View all users and their KYC status.
  - Response: `[ { user_id, full_name, email, kyc_status } ]`
- `GET /api/v1/admin/transactions`: Monitor all top-up and QRIS transactions.
  - Response: `[ { transaction_id, user_id, type, amount, status, created_at } ]`
- `POST /api/v1/admin/refund`: Trigger manual refund (optional).
  - Request: `{ transaction_id, amount }`
  - Response: `{ status }`




## 3. Technology Stack

- **Backend**: Node.js with Express.js
- **Frontend**: React Native
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Deployment**: Docker

## 4. Security Considerations

- **Authentication**: Implement JWT for secure API authentication. Tokens will be short-lived and refreshed regularly.
- **API Keys**: Store Privy and Xendit API keys securely using environment variables.
- **Data Encryption**: Encrypt sensitive user data at rest and in transit (HTTPS).
- **Input Validation**: Implement robust input validation on all API endpoints to prevent injection attacks.
- **Rate Limiting**: Implement rate limiting on authentication and critical API endpoints to prevent abuse.
- **Audit Logs**: Maintain comprehensive audit logs for all sensitive operations and transactions.
- **Error Handling**: Implement proper error handling to avoid leaking sensitive information in error responses.
- **Dockerization**: Containerize the application for isolated and consistent deployment environments, enhancing security and portability.

