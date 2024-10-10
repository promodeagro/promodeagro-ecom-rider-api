# **API Documentation**

## **Authentication and Rider Profile Management**

### **1. Sign In**

-   **Endpoint:** `POST /auth/signin`

-   **Request Body:**

```json
{ "number": "9876543210" }
```

### **2. Validate OTP**

-   **Endpoint:** `POST /auth/validate-otp`

-   **Request Body:**

```json
{ "number": "9876543210", "otp": "123456" }
```

### **3. Update Personal Details**

-   **Endpoint:** `PUT /rider/personal-details`

-   **Request Body:**

```json
{
	"id": "uuid",
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
	"reference": { "relation": "Friend", "number": "9876543210" }
}
```

### **4. Update Bank Details**

-   **Endpoint:** `PUT /rider/bank-details`

-   **Request Body:**

```json
{
	"id": "uuid",
	"bankName": "Bank of America",
	"acc": "1234567890",
	"ifsc": "BOFA0001234"
}
```

### **5. Update Document Details**

-   **Endpoint:** `PUT /rider/document-details`

-   **Request Body:**

```json
{
	"id": "uuid",
	"userPhoto": "https://example.com/photo.jpg",
	"aadharFront": "https://example.com/aadhar_front.jpg",
	"aadharBack": "https://example.com/aadhar_back.jpg",
	"pan": "https://example.com/pan.jpg",
	"dl": "https://example.com/dl.jpg",
	"vehicleImage": "https://example.com/vehicle.jpg",
	"rcBook": "https://example.com/rcbook.jpg"
}
```

### **6. Submit Rider Profile**

-   **Endpoint:** `PUT /rider/submit/{id}`

-   **Request Body:**

```json
{ "id": "uuid" }
```

### **7. Get Upload URL**

-   **Endpoint:** `GET /uploadUrl`

-   **Request Query Parameters:**

    -   `fileName`: The name of the file to upload.

-   **Responses:**

    -   `200`: Returns the pre-signed S3 URL for file upload.
