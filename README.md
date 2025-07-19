# Promodeagro Rider API

A serverless Python API for rider management and delivery operations built with AWS Lambda, DynamoDB, and Cognito.

## 🚀 Features

- **Rider Authentication**: OTP-based signin, token management
- **Rider Registration**: Personal details, bank details, document upload
- **Runsheet Management**: Order assignment, delivery tracking
- **Media Management**: Image upload and management
- **Notifications**: Real-time notifications for riders

## 🛠️ Tech Stack

- **Backend**: Python 3.11, FastAPI, Pydantic
- **Serverless**: AWS Lambda, API Gateway
- **Database**: DynamoDB
- **Authentication**: AWS Cognito
- **Storage**: AWS S3
- **Framework**: Serverless Framework

## 📋 Prerequisites

- **Node.js** (v18 or higher)
- **Python** (3.11 or higher)
- **AWS CLI** configured
- **Serverless Framework** (installed globally)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (optional)
npm install
```

### 2. Environment Setup

Copy the local environment file:
```bash
cp local.env.example local.env
```

Update the environment variables in `local.env` with your AWS credentials and configuration.

### 3. Run Locally

#### Option A: FastAPI Development Server
```bash
# Start the local development server
python local_server.py
```

#### Option B: Serverless Offline
```bash
# Install serverless offline plugin
npm install -g serverless-offline

# Start serverless offline
serverless offline start
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Base URL**: http://localhost:8000

## 📚 API Endpoints

### Authentication
- `POST /auth/signin` - Send OTP for rider signin
- `POST /auth/validate-otp` - Validate OTP and get tokens
- `POST /auth/refresh-token` - Refresh access token
- `POST /auth/signout` - Sign out rider

### Rider Management
- `POST /register` - Register new rider
- `PUT /rider/personal-details` - Update personal details
- `PUT /rider/bank-details` - Update bank details
- `PUT /rider/document-details` - Update document details

### Runsheet Management
- `GET /rider/{id}/runsheet` - List rider runsheets
- `GET /rider/{id}/runsheet/{runsheetId}` - Get specific runsheet
- `GET /rider/{id}/runsheet/{runsheetId}/accept` - Accept runsheet
- `PUT /rider/{id}/runsheet/{runsheetId}/order/{orderId}/complete` - Complete order
- `PUT /rider/{id}/runsheet/{runsheetId}/order/{orderId}/cancel` - Cancel order

### Media Management
- `GET /rider/uploadUrl` - Get presigned upload URL
- `GET /rider/deleteImage` - Delete image

### Notifications
- `GET /notification/{id}` - List notifications for rider

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=src

# Run specific test file
python -m pytest tests/test_auth.py
```

## 🚀 Deployment

### Development Deployment
```bash
serverless deploy --stage dev
```

### Production Deployment
```bash
serverless deploy --stage prod
```

### Remove Deployment
```bash
serverless remove --stage dev
```

## 📁 Project Structure

```
rider-api-serverless/
├── api-spec/                 # API specifications
├── src/                      # Source code
│   ├── auth.py              # Authentication service
│   ├── models.py            # Pydantic models
│   ├── commonfunctions/     # Shared utilities
│   │   └── db.py           # DynamoDB operations
│   └── handlers/            # Lambda handlers
│       ├── auth_handlers.py
│       ├── rider_handlers.py
│       ├── runsheet_handlers.py
│       ├── media_handlers.py
│       └── notification_handlers.py
├── tests/                   # Test files
├── serverless.yml           # Serverless configuration
├── requirements.txt         # Python dependencies
├── local_server.py         # Local development server
├── package.json            # Node.js configuration
└── README.md               # This file
```

## 🔧 Development

### Adding New Endpoints

1. Create handler in appropriate `handlers/` file
2. Add endpoint to `serverless.yml`
3. Add route to `local_server.py` for local testing
4. Write tests in `tests/` directory

### Environment Variables

Key environment variables:
- `USERS_TABLE` - DynamoDB table for users
- `RUNSHEET_TABLE` - DynamoDB table for runsheets
- `ORDERS_TABLE` - DynamoDB table for orders
- `USER_POOL_ID` - Cognito User Pool ID
- `COGNITO_CLIENT` - Cognito Client ID
- `MEDIA_BUCKET` - S3 bucket for media storage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs` endpoint 