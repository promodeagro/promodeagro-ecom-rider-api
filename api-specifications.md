# PromodeAgro E-commerce Rider APIs - API Documentation

## Overview

This document provides comprehensive API specifications for the PromodeAgro E-commerce Rider Management System. The API enables rider authentication, profile management, runsheet operations, and order management.

**Base URL:** `https://api.promodeagro.com/v1`

## Authentication

All API endpoints (except authentication endpoints) require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 1. Authentication Endpoints

### 1.1 Sign In
**Endpoint:** `POST /auth/signin`

Initiates the sign-in process by sending OTP to the provided mobile number.

**Request Body:**
```json
{
  "number": "9876543210"
}
```

**Response (200):**
```json
{
  "message": "OTP sent successfully",
  "success": true
}
```

**Error Responses:**
- `400` - Invalid mobile number
- `500` - Internal server error

---

### 1.2 Validate OTP
**Endpoint:** `POST /auth/validate-otp`

Validates the OTP and returns access and refresh tokens upon successful validation.

**Request Body:**
```json
{
  "number": "9876543210",
  "otp": "123456"
}
```

**Response (200):**
```json
{
  "message": "OTP validated successfully",
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "rider": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "number": "9876543210",
    "status": "pending"
  }
}
```

**Error Responses:**
- `400` - Invalid OTP or mobile number
- `401` - Invalid OTP
- `500` - Internal server error

---

### 1.3 Refresh Token
**Endpoint:** `POST /auth/refresh-token`

Generates a new access token using a valid refresh token.

**Request Body:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**
- `401` - Invalid refresh token
- `500` - Internal server error

---

## 2. Rider Profile Management

### 2.1 Update Personal Details
**Endpoint:** `PUT /rider/personal-details`

Updates the personal information of a rider including name, DOB, email, address, and reference.

**Request Body:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "fullName": "John Doe",
  "dob": "2000-01-01T00:00:00Z",
  "email": "john.doe@example.com",
  "address": {
    "address1": "123 Main St",
    "address2": "Apt 4",
    "landmark": "Near Park",
    "state": "CA",
    "city": "Los Angeles",
    "pincode": "90001"
  },
  "reference": {
    "relation": "Friend",
    "number": "9876543210"
  }
}
```

**Response (200):**
```json
{
  "message": "Personal details updated successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Error Responses:**
- `400` - Invalid request data
- `401` - Unauthorized
- `404` - Rider not found
- `500` - Internal server error

---

### 2.2 Update Bank Details
**Endpoint:** `PUT /rider/bank-details`

Updates the bank account information of a rider.

**Request Body:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "bankName": "Bank of America",
  "acc": "1234567890",
  "ifsc": "BOFA0001234"
}
```

**Response (200):**
```json
{
  "message": "Bank details updated successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Error Responses:**
- `400` - Invalid request data
- `401` - Unauthorized
- `404` - Rider not found
- `500` - Internal server error

---

### 2.3 Update Document Details
**Endpoint:** `PUT /rider/document-details`

Updates the document information of a rider including photos and identity documents.

**Request Body:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "documents": [
    {
      "name": "userPhoto",
      "image": "https://example.com/photo.jpg"
    },
    {
      "name": "aadharFront",
      "image": "https://example.com/aadhar_front.jpg"
    },
    {
      "name": "aadharBack",
      "image": "https://example.com/aadhar_back.jpg"
    },
    {
      "name": "pan",
      "image": "https://example.com/pan.jpg"
    },
    {
      "name": "dl",
      "image": "https://example.com/dl.jpg"
    },
    {
      "name": "vehicleImage",
      "image": "https://example.com/vehicle.jpg"
    },
    {
      "name": "rcBook",
      "image": "https://example.com/rcbook.jpg"
    }
  ]
}
```

**Document Types:**
- `userPhoto` - Rider's profile photo
- `aadharFront` - Front side of Aadhar card
- `aadharBack` - Back side of Aadhar card
- `pan` - PAN card
- `dl` - Driving license
- `vehicleImage` - Vehicle photo
- `rcBook` - RC book

**Response (200):**
```json
{
  "message": "Document details updated successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Error Responses:**
- `400` - Invalid request data
- `401` - Unauthorized
- `404` - Rider not found
- `500` - Internal server error

---

### 2.4 Submit Rider Profile
**Endpoint:** `PUT /rider/submit/{id}`

Submits the rider profile for review and approval.

**Request Body:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200):**
```json
{
  "message": "Profile submitted successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending_approval"
  }
}
```

**Error Responses:**
- `400` - Invalid rider ID or incomplete profile
- `401` - Unauthorized
- `404` - Rider not found
- `500` - Internal server error

---

## 3. File Upload

### 3.1 Get Upload URL
**Endpoint:** `GET /uploadUrl`

Generates a pre-signed S3 URL for file upload.

**Query Parameters:**
- `fileName` (required): Name of the file to upload

**Response (200):**
```json
{
  "uploadUrl": "https://s3.amazonaws.com/bucket/presigned-url",
  "fileKey": "uploads/rider_photo_123.jpg",
  "expiresIn": 3600
}
```

**Error Responses:**
- `400` - Invalid file name
- `401` - Unauthorized
- `500` - Internal server error

---

## 4. Runsheet Management

### 4.1 Get Rider Runsheets
**Endpoint:** `GET /rider/{id}/runsheet`

Retrieves a list of runsheets for the specified rider.

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "orders": 10,
    "pendingOrders": 3,
    "deliveredOrders": 7,
    "amountCollectable": 1500.50,
    "status": "pending",
    "createdAt": "2024-01-01T10:00:00Z",
    "updatedAt": "2024-01-01T10:00:00Z"
  }
]
```

**Error Responses:**
- `400` - Invalid rider ID
- `401` - Unauthorized
- `404` - Rider not found
- `500` - Internal server error

---

### 4.2 Get Specific Runsheet
**Endpoint:** `GET /rider/{id}/runsheet/{runsheetId}`

Retrieves detailed information of a specific runsheet including all orders.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "orders": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "status": "pending",
      "paymentDetails": {
        "method": "cod",
        "status": "pending",
        "amount": 150.00
      },
      "customerDetails": {
        "name": "John Customer",
        "phone": "9876543210",
        "email": "customer@example.com"
      },
      "deliveryAddress": {
        "address1": "456 Customer St",
        "address2": "Unit 2",
        "landmark": "Near Mall",
        "state": "CA",
        "city": "Los Angeles",
        "pincode": "90002"
      },
      "amount": 150.00,
      "createdAt": "2024-01-01T10:00:00Z"
    }
  ],
  "status": "pending",
  "createdAt": "2024-01-01T10:00:00Z",
  "updatedAt": "2024-01-01T10:00:00Z"
}
```

**Error Responses:**
- `400` - Invalid rider ID or runsheet ID
- `401` - Unauthorized
- `404` - Rider or runsheet not found
- `500` - Internal server error

---

### 4.3 Accept Runsheet
**Endpoint:** `GET /rider/{id}/runsheet/{runsheetId}/accept`

Accepts the specified runsheet for the rider.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "orders": 10,
  "pendingOrders": 3,
  "deliveredOrders": 7,
  "amountCollectable": 1500.50,
  "status": "accepted",
  "createdAt": "2024-01-01T10:00:00Z",
  "updatedAt": "2024-01-01T11:00:00Z"
}
```

**Error Responses:**
- `400` - Invalid rider ID or runsheet ID
- `401` - Unauthorized
- `404` - Rider or runsheet not found
- `409` - Runsheet already accepted or in progress
- `500` - Internal server error

---

### 4.4 Complete Order
**Endpoint:** `PUT /rider/{id}/runsheet/{runsheetId}/order/{orderId}/complete`

Confirms the completion of an order within a runsheet.

**Request Body:**
```json
{
  "image": "https://example.com/delivery_confirmation.jpg"
}
```

**Response (200):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "delivered",
  "paymentDetails": {
    "method": "cod",
    "status": "completed",
    "amount": 150.00
  },
  "customerDetails": {
    "name": "John Customer",
    "phone": "9876543210",
    "email": "customer@example.com"
  },
  "deliveryAddress": {
    "address1": "456 Customer St",
    "address2": "Unit 2",
    "landmark": "Near Mall",
    "state": "CA",
    "city": "Los Angeles",
    "pincode": "90002"
  },
  "amount": 150.00,
  "deliveryImage": "https://example.com/delivery_confirmation.jpg",
  "completedAt": "2024-01-01T12:00:00Z",
  "createdAt": "2024-01-01T10:00:00Z"
}
```

**Error Responses:**
- `400` - Invalid request data
- `401` - Unauthorized
- `404` - Rider, runsheet, or order not found
- `409` - Order already completed or cancelled
- `500` - Internal server error

---

### 4.5 Cancel Order
**Endpoint:** `PUT /rider/{id}/runsheet/{runsheetId}/order/{orderId}/cancel`

Cancels a specified order within a runsheet.

**Request Body:**
```json
{
  "reason": "Customer not available at delivery location"
}
```

**Response (200):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "paymentDetails": {
    "method": "cod",
    "status": "cancelled",
    "amount": 150.00
  },
  "customerDetails": {
    "name": "John Customer",
    "phone": "9876543210",
    "email": "customer@example.com"
  },
  "deliveryAddress": {
    "address1": "456 Customer St",
    "address2": "Unit 2",
    "landmark": "Near Mall",
    "state": "CA",
    "city": "Los Angeles",
    "pincode": "90002"
  },
  "amount": 150.00,
  "cancellationReason": "Customer not available at delivery location",
  "cancelledAt": "2024-01-01T12:00:00Z",
  "createdAt": "2024-01-01T10:00:00Z"
}
```

**Error Responses:**
- `400` - Invalid request data
- `401` - Unauthorized
- `404` - Rider, runsheet, or order not found
- `409` - Order already completed or cancelled
- `500` - Internal server error

---

## 5. Notifications

### 5.1 Get Rider Notifications
**Endpoint:** `GET /rider/{id}/notifications`

Retrieves a list of unread notifications for the specified rider.

**Response (200):**
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "title": "New Runsheet Assigned",
    "message": "You have been assigned a new runsheet with 10 orders.",
    "read": false,
    "createdAt": "2024-01-02T10:00:00Z",
    "type": "runsheet_assigned"
  },
  {
    "id": "880e8400-e29b-41d4-a716-446655440000",
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Profile Approved",
    "message": "Your profile has been approved. You can now start accepting runsheets.",
    "read": false,
    "createdAt": "2024-01-01T18:00:00Z",
    "type": "profile_approved"
  }
]
```

**Error Responses:**
- `400` - Invalid rider ID
- `401` - Unauthorized
- `404` - Rider not found
- `500` - Internal server error

---

## Data Models

### Rider Status
- `pending` - Profile created but not submitted
- `pending_approval` - Profile submitted for approval
- `active` - Profile approved and rider is active
- `inactive` - Rider account is inactive
- `suspended` - Rider account is suspended

### Runsheet Status
- `pending` - Runsheet created but not accepted
- `accepted` - Runsheet accepted by rider
- `in_progress` - Runsheet is being executed
- `completed` - Runsheet completed

### Order Status
- `pending` - Order assigned but not picked up
- `picked_up` - Order picked up by rider
- `delivered` - Order delivered successfully
- `cancelled` - Order cancelled

### Payment Method
- `cod` - Cash on delivery
- `online` - Online payment
- `wallet` - Wallet payment

### Payment Status
- `pending` - Payment pending
- `completed` - Payment completed
- `failed` - Payment failed
- `cancelled` - Payment cancelled

### Notification Type
- `runsheet_assigned` - A new runsheet is assigned
- `payment_received` - A payment has been received
- `profile_approved` - Rider profile has been approved
- `general` - General notification

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Invalid or missing authentication |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource state conflict |
| 500 | Internal Server Error - Server error |

---

## Rate Limiting

- Authentication endpoints: 5 requests per minute
- Profile management endpoints: 10 requests per minute
- Runsheet management endpoints: 20 requests per minute
- File upload endpoints: 30 requests per minute

---

## Versioning

The API version is included in the URL path. Current version is `v1`.

---

## Support

For API support and questions, please contact:
- Email: support@promodeagro.com
- Documentation: https://docs.promodeagro.com 