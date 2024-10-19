# **API Documentation**

## **Authentication and Rider Profile Management**

### **Sign In**

-   **Endpoint:** `POST /auth/signin`

-   **Request Body:**

```json
{ "number": "9876543210" }
```

### **Validate OTP**

-   **Endpoint:** `POST /auth/validate-otp`

-   **Request Body:**

```json
{ "number": "9876543210", "otp": "123456" }
```

### **Refresh Token**

-   **Endpoint:** `POST /auth/refresh-token`

## Description
This endpoint allows clients to refresh their access tokens using a valid refresh token. It generates a new access token for the user.

## Request

### Headers
- **Content-Type**: `application/json`

### Body
The request body must be a JSON object containing the `refreshToken`. 

#### Example
```json
{
  "refreshToken": "your_refresh_token_here"
} 
```

### **Update Personal Details**

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

### **Update Bank Details**

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

### **Update Document Details**

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

### **Submit Rider Profile**

-   **Endpoint:** `PUT /rider/submit/{id}`

-   **Request Body:**

```json
{ "id": "uuid" }
```

### **Get Upload URL**

-   **Endpoint:** `GET /uploadUrl`

-   **Request Query Parameters:**

    -   `fileName`: The name of the file to upload.

-   **Responses:**

    -   `200`: Returns the pre-signed S3 URL for file upload.


- **Endpoint:** `GET /rider/{id}/runsheet`

- **Description:** Retrieves a list of runsheets for the specified rider ID.

- **Path Parameters:**

  - `id` (string, required): The ID of the rider.

- **Responses:**

  - **200 OK**

    ```json
    [
      {
        "id": "string",
        "orders": "number",
        "pendingOrders": "number",
        "deliveredOrders": "number",
        "amountCollectable": "number"
      }
    ]
    ```

  - **400 Bad Request**

    ```json
    {
      "message": "invalid id"
    }
    ```

### Accept Runsheet

- **Endpoint:** `GET /rider/{id}/runsheet/{runsheetId}/accept`

- **Description:** Accepts the specified runsheet for the rider.

- **Path Parameters:**

  - `id` (string, required): The ID of the rider.

  - `runsheetId` (string, required): The ID of the runsheet.

- **Responses:**

  - **200 OK** (Returns the updated runsheet object)

  - **400 Bad Request**

    ```json
    {
      "message": "invalid id"
    }
    ```

### Get Runsheet

- **Endpoint:** `GET /rider/{id}/runsheet/{runsheetId}`

- **Description:** Retrieves details of a specific runsheet by its ID.

- **Path Parameters:**

  - `id` (string, required): The ID of the rider.

  - `runsheetId` (string, required): The ID of the runsheet.

- **Responses:**

  - **200 OK**

    ```json
    {
      "id": "string",
      "orders": [
        {
          "id": "string",
          "status": "string",
          "paymentDetails": {
            // payment details structure
          }
        }
      ]
    }
    ```

  - **400 Bad Request**

    ```json
    {
      "message": "invalid id"
    }
    ```

### Confirm Order

- **Endpoint:** `PUT /rider/{id}/runsheet/{runsheetId}/order/{orderId}/complete`

- **Description:** Confirms the completion of an order within a runsheet.

- **Path Parameters:**

  - `id` (string, required): The ID of the rider.

  - `runsheetId` (string, required): The ID of the runsheet.

  - `orderId` (string, required): The ID of the order to confirm.

- **Request Body:**

  ````json
  {
    "image": "string"
  }
  <!-- ``` -->

  ````

- **Responses:**

  - **200 OK** (Returns the updated order object)

  - **400 Bad Request**

    ```
    json
    ```

    Copy code

    `{ "message": "invalid id" }`

### Cancel Order

- **Endpoint:** `PUT /rider/{id}/runsheet/{runsheetId}/order/{orderId}/cancel`

- **Description:** Cancels a specified order within a runsheet.

- **Path Parameters:**

  - `id` (string, required): The ID of the rider.

  - `runsheetId` (string, required): The ID of the runsheet.

  - `orderId` (string, required): The ID of the order to cancel.

- **Request Body:**

  ```
  json
  ```

  Copy code

  `{ "reason": "string" }`

- **Responses:**

  - **200 OK** (Returns the updated order object)

  - **400 Bad Request**

    ```
    json
    ```

    Copy code

    `{ "message": "invalid id" }`
