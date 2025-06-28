# Promodeagro E-commerce Rider API

A serverless API built with AWS Lambda and Python for e-commerce rider management system.

## 🚀 Features

- **Authentication System**: Phone-based OTP authentication
- **Token Management**: JWT-based access and refresh tokens
- **File Upload**: Secure S3 upload URLs
- **Notifications**: Real-time notification system
- **Serverless Architecture**: Built with AWS Lambda and API Gateway

## 📋 Prerequisites

- Python 3.12+
- Node.js 18+ (for Serverless Framework)
- AWS CLI
- AWS Account with appropriate permissions

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd promodeagro-ecom-rider-api
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Serverless Framework (if not installed)
```bash
npm install -g serverless
```

### 5. Configure AWS Credentials
```bash
aws configure
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=your-dynamodb-table
JWT_SECRET=your-jwt-secret-key
```

### Serverless Configuration
The `serverless.yml` file contains the service configuration. Update the following:
- Service name
- AWS region
- DynamoDB table names
- Environment variables

## 🚀 Local Development

### Start Local Server
```bash
serverless offline start --stage dev
```

The API will be available at `http://localhost:3000`

### Run Tests
```bash
# Install test dependencies
pip install pytest requests

# Run tests
pytest test/
```

## 📚 API Endpoints

### Authentication

#### 1. Sign In
```http
POST /signin
Content-Type: application/json

{
  "phone": "1234567890"
}
```

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "message": "OTP sent successfully",
    "otp": "123456"
  }
}
```

#### 2. Validate OTP
```http
POST /validate-otp
Content-Type: application/json

{
  "phone": "1234567890",
  "otp": "123456"
}
```

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "message": "OTP validated successfully",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "refresh_token_here"
  }
}
```

#### 3. Refresh Token
```http
POST /refresh-token
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "message": "Token refreshed successfully",
    "access_token": "new_access_token_here"
  }
}
```

### File Management

#### 4. Get Upload URL
```http
POST /upload-url
Content-Type: application/json
Authorization: Bearer your_access_token

{
  "file_name": "document.pdf",
  "file_type": "application/pdf"
}
```

### Notifications

#### 5. Get Notifications
```http
GET /notifications
Authorization: Bearer your_access_token
```

## 🧪 Testing

### Manual Testing with Postman

1. **Import the collection** (if available)
2. **Set up environment variables**:
   - `base_url`: `http://localhost:3000`
   - `access_token`: (will be set after login)
   - `refresh_token`: (will be set after login)

### Automated Testing

Run the test suite:
```bash
pytest test/ -v
```

Run specific test:
```bash
pytest test/test_api.py::test_signin -v
```

## 📁 Project Structure

```
promodeagro-ecom-rider-api/
├── src/
│   ├── handlers/
│   │   ├── signin.py
│   │   ├── validate_otp.py
│   │   ├── refresh_token.py
│   │   ├── upload_url.py
│   │   └── get_notifications.py
│   └── commonfunctions/
│       └── dynamodb.py
├── test/
│   └── test_api.py
├── api-specs/
│   └── procurement-ApiSpecs.yml
├── serverless.yml
├── requirements.txt
└── README.md
```

## 🚀 Deployment

### Deploy to AWS
```bash
serverless deploy --stage prod
```

### Deploy to Specific Stage
```bash
serverless deploy --stage dev
```

### Remove Deployment
```bash
serverless remove --stage prod
```

## 🔍 Monitoring and Logs

### View CloudWatch Logs
```bash
serverless logs -f functionName --stage prod
```

### View API Gateway Logs
```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/apigateway"
```

## 🛡️ Security

- JWT tokens for authentication
- DynamoDB for secure data storage
- AWS IAM roles for Lambda functions
- API Gateway for request validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation in `api-specs/`

## 🔄 Version History

- **v1.0.0**: Initial release with authentication and basic endpoints
- **v1.1.0**: Added file upload functionality
- **v1.2.0**: Added notification system

---

**Note**: Make sure to update the AWS credentials and environment variables according to your setup before running the application.
