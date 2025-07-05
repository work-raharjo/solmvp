# Sol MVP - Passport-Based QRIS Wallet for Foreign Tourists

Sol is a digital wallet application designed specifically for foreign tourists visiting Indonesia. It enables users to scan and pay at any QRIS merchant without requiring an Indonesian phone number, e-KTP, or local bank account. The system uses passport-based KYC verification through Privy and supports multiple payment methods via DOKU.

## 🚀 Features

### User Features
- **Passport-Based Registration**: Register using passport information without Indonesian requirements
- **KYC Verification**: Secure identity verification using Privy API with OCR and liveness detection
- **Multiple Top-up Methods**: Support for Virtual Account, Credit Card, and E-wallet payments
- **QRIS Payments**: Scan and pay at any QRIS merchant across Indonesia
- **Transaction History**: Complete record of all transactions and wallet activities
- **Real-time Balance**: Live wallet balance updates

### Admin Features
- **User Management**: View and manage all registered users and their KYC status
- **Transaction Monitoring**: Real-time monitoring of all transactions and payment flows
- **Analytics Dashboard**: Comprehensive charts and statistics
- **Manual Refunds**: Ability to process manual refunds when needed
- **Audit Logs**: Complete audit trail of all system activities

### Compliance & Security
- **KYC Compliance**: Full KYC verification using Privy's passport OCR and selfie matching
- **Secure Payments**: All payments processed through DOKU as registered Payment Service Provider
- **Audit Trail**: Complete transaction and user activity logging
- **Data Protection**: Secure handling of sensitive user data and documents

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python Flask with SQLAlchemy ORM
- **Frontend**: React with modern hooks and context API
- **Admin Dashboard**: React with Recharts for data visualization
- **Database**: PostgreSQL with proper indexing and relationships
- **Authentication**: JWT-based authentication with bcrypt password hashing
- **File Storage**: Local file system with planned cloud storage integration
- **Containerization**: Docker and Docker Compose for easy deployment

### API Integrations
- **Privy**: KYC verification, passport OCR, and liveness detection
- **DOKU**: Payment processing, QRIS generation, and webhook handling

## 📦 Project Structure

```
sol_mvp/
├── backend/sol_backend/          # Flask backend API
│   ├── src/
│   │   ├── models/              # Database models
│   │   ├── routes/              # API route handlers
│   │   └── main.py             # Application entry point
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile              # Backend container configuration
├── frontend/sol_frontend/        # React mobile web app
│   ├── src/
│   │   ├── components/         # React components
│   │   └── App.jsx            # Main application component
│   ├── package.json           # Node.js dependencies
│   └── Dockerfile            # Frontend container configuration
├── admin_dashboard/sol_admin/    # React admin dashboard
│   ├── src/
│   │   └── App.jsx           # Admin dashboard component
│   ├── package.json          # Node.js dependencies
│   └── Dockerfile           # Admin container configuration
├── database/
│   └── init.sql             # Database initialization script
├── docker-compose.yml       # Multi-container orchestration
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git for cloning the repository

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sol_mvp
   ```

2. **Start the development environment**
   ```bash
   docker-compose up -d
   ```

3. **Access the applications**
   - Frontend (Mobile App): http://localhost:3000
   - Admin Dashboard: http://localhost:3001
   - Backend API: http://localhost:5000
   - Database: localhost:5432

### Manual Development Setup

If you prefer to run components individually:

#### Backend Setup
```bash
cd backend/sol_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

#### Frontend Setup
```bash
cd frontend/sol_frontend
npm install
npm run dev
```

#### Admin Dashboard Setup
```bash
cd admin_dashboard/sol_admin
npm install
npm run dev
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://sol_user:sol_password@localhost:5432/sol_mvp

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Privy API Configuration
PRIVY_API_KEY=your-privy-api-key
PRIVY_API_URL=https://api.privy.id

# DOKU API Configuration
DOKU_CLIENT_ID=your-doku-client-id
DOKU_SECRET_KEY=your-doku-secret-key
DOKU_WEBHOOK_SECRET=your-doku-webhook-secret

# Application Configuration
FLASK_ENV=development
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### API Keys Setup

1. **Privy API Key**
   - Sign up at [Privy.id](https://privy.id)
   - Obtain API credentials for KYC services
   - Configure webhook endpoints for status updates

2. **DOKU API Key**
   - Register at [DOKU](https://doku.com)
   - Get API keys for payment processing
   - Set up webhook URLs for transaction updates

## 📚 API Documentation

### Authentication Endpoints

#### POST /api/auth/register
Register a new user with passport information.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "passport_number": "A12345678",
  "full_name": "John Smith",
  "phone_number": "+1234567890"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "access_token": "jwt_token_here",
  "user_id": 1,
  "kyc_status": "PENDING"
}
```

#### POST /api/auth/login
Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### KYC Endpoints

#### POST /api/privy/verify
Submit passport and selfie for KYC verification.

**Request Body (multipart/form-data):**
- `passport_image`: File upload
- `selfie_image`: File upload

### Wallet Endpoints

#### GET /api/wallet/balance
Get current wallet balance (requires authentication).

#### POST /api/wallet/topup
Initiate wallet top-up via DOKU.

**Request Body:**
```json
{
  "amount": 100000,
  "payment_method": "BCA_VA"
}
```

**Response:**
```json
{
  "transaction_id": 123,
  "reference_no": "DOKU_REF_123",
  "partner_reference_no": "PARTNER_REF_456",
  "amount": 100000,
  "payment_method": "BCA_VA",
  "status": "PENDING",
  "va_number": "88881234567890",
  "bank_code": "BCA",
  "expired_time": "2025-07-05T10:00:00Z"
}
```

#### POST /api/wallet/qris-payment
Process QRIS payment.

**Request Body:**
```json
{
  "qr_code": "qris_code_string",
  "amount": 25000
}
```

**Response:**
```json
{
  "transaction_id": 123,
  "reference_no": "DOKU_REF_123",
  "partner_reference_no": "PARTNER_REF_456",
  "status": "SUCCESS",
  "amount": 25000,
  "remaining_balance": 1000000,
  "qr_content": "QR_CODE_CONTENT_STRING",
  "merchant_qris_code": "MERCHANT_QRIS_XYZ"
}
```

### Admin Endpoints

#### GET /api/admin/users
Get all users with pagination (admin only).

#### GET /api/admin/transactions
Get all transactions with filtering (admin only).

## 🧪 Testing

### Demo Credentials

**User Account:**
- Email: john.smith@example.com
- Password: password123

**Admin Account:**
- Username: admin
- Password: admin

### Test Data

The system includes sample data for testing:
- 3 test users with different KYC statuses
- Sample transactions showing various payment methods
- Mock Privy and Xendit integrations for development

## 🚀 Deployment

### Production Deployment

1. **Update environment variables** for production
2. **Build and deploy with Docker Compose:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Cloud Deployment Options

- **AWS**: Use ECS or EKS for container orchestration
- **Google Cloud**: Deploy on Google Kubernetes Engine
- **Azure**: Use Azure Container Instances or AKS
- **DigitalOcean**: Deploy on App Platform or Kubernetes

### Security Considerations

- Change all default passwords and API keys
- Use HTTPS in production with proper SSL certificates
- Implement rate limiting and DDoS protection
- Regular security audits and dependency updates
- Secure file upload validation and storage

## 📊 Monitoring & Analytics

### Key Metrics to Monitor

- User registration and KYC approval rates
- Transaction success rates and volumes
- API response times and error rates
- Wallet balance distributions
- Geographic usage patterns

### Logging

The application includes comprehensive logging for:
- User authentication and authorization
- Transaction processing and status changes
- KYC verification attempts and results
- API requests and responses
- Error tracking and debugging

## 🔄 Integration Guide

### Privy Integration

The system integrates with Privy for KYC verification:

1. **Document Upload**: Users upload passport and selfie images
2. **OCR Processing**: Privy extracts passport information
3. **Liveness Detection**: Selfie verification against passport photo
4. **Webhook Updates**: Real-time status updates via webhooks

### Xendit Integration

Payment processing through Xendit includes:

1. **Payment Methods**: Virtual Account, Credit Card, E-wallets
2. **QRIS Processing**: Dynamic QR code generation and payment
3. **Webhook Handling**: Real-time transaction status updates
4. **Refund Processing**: Automated and manual refund capabilities

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript/React code
- Implement proper error handling and logging
- Write comprehensive API documentation

### Database Migrations
- Use Alembic for database schema migrations
- Always backup before applying migrations
- Test migrations in staging environment first

### Testing Strategy
- Unit tests for business logic
- Integration tests for API endpoints
- End-to-end tests for critical user flows
- Load testing for payment processing

## 📞 Support & Contact

For technical support or questions about the Sol MVP:

- **Development Team**: [Your contact information]
- **Documentation**: [Link to detailed docs]
- **Issue Tracking**: [GitHub issues or similar]

## 📄 License

This project is proprietary software developed for Sol MVP. All rights reserved.

---

**Note**: This is an MVP (Minimum Viable Product) designed for demonstration and pilot testing. For production deployment, additional security hardening, performance optimization, and compliance measures should be implemented.

