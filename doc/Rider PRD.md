# 📦 Rider App – Product Requirements Document (PRD)

## 🧭 Purpose
The Rider app is designed to streamline the last-mile delivery process. It allows delivery personnel (riders) to receive runsheets, manage and fulfill orders, collect payments, and track daily cash summaries — all in one mobile-first interface.

## 🧑‍💼 Target Users
- Delivery Riders / Agents
- Internal Admin/Operations Teams (for verification & assignment)

## 🧱 Functional Modules

### 1️⃣ Authentication & Onboarding

#### 1.1 Login Screen
- **Elements:**
    - Rider logo + illustration
    - Input field: Mobile Number
    - Buttons: Sign In, Register
- **Flow:**
    - On Sign In → Navigate to OTP Verification screen

#### 1.2 OTP Verification
- **Elements:**
    - OTP input (6 digits)
    - Verify OTP button
    - Resend OTP link
- **Behavior:**
    - Valid OTP → Navigate to Dashboard
    - Invalid OTP → Error message shown

#### 1.3 Registration Flow (Triggered via Register link)
A 4-step onboarding flow:

- **Step 1: Personal Details**
    - Full Name, DOB, Mobile, Email
    - Address (Lines 1 & 2, Landmark, State, City, Pincode)
    - Reference Contact: Relation, Mobile
- **Step 2: Bank Details**
    - Select Bank (Dropdown), Account Number (with confirmation), IFSC Code
- **Step 3: Documents Upload**
    - Uploads: Photo, Aadhaar (front/back), PAN, DL (front/back), RC Book (front/back), Vehicle Image
- **Step 4: Review and Submit**
    - Editable view of all inputs before submission

#### 1.4 Application Status Screen
- **Shown after registration:**
    - Message: "Your account is under verification."
    - Button: Go to Sign In
- **Post-verification, the user logs in and reaches the Dashboard**

### 2️⃣ Home Dashboard

#### 2.1 No Runsheet Assigned
- **Center message:** "No Runsheet Assigned!"
- **Refresh button (to fetch updated runsheet assignments)**

#### 2.2 Runsheet Assigned
- **Runsheet cards display:**
    - Runsheet Number
    - Total Orders / Pending / Delivered
    - Cash to be Collected
    - Continue button → navigates to Single Runsheet Page

### 3️⃣ Single Runsheet View

#### 3.1 Runsheet Details Page
- **Header:**
    - App bar (Logo, Notification, Profile)
    - Breadcrumb: Home > Runsheet
    - Refresh button
- **Filters:**
    - Tabs for Pending, Delivered, Undelivered
- **Search Bar:**
    - Filter by customer name
- **Shipment Cards:**
    - Customer Name
    - Payment Type: COD / Prepaid
    - Address, Items count, Payment amount

### 4️⃣ Shipment Handling

#### 4.1 Single Shipment Page
- **Customer Info**
- **Order ID, Amount to Collect**
- **Items Table (Product, Quantity, Price)**
- **Buttons:** Confirm Order, Cancel

#### 4.2 Cancel Flow
- **Modal with:**
    - Reason (radio buttons)
    - Optional Notes
    - Ok (confirm cancel) | Go Back

#### 4.3 Confirm Flow
- **Navigates to Camera Page**
    - Rider takes photo of delivered items
    - Button: Verified

### 5️⃣ Order Completion Logic

#### 5.1 Prepaid Orders
- **Post-verification page shows:**
    - ₹0 to collect
    - Delivered Order button
    - Modal: Complete Order | Go Back
    - Success: "Order delivered successfully."

#### 5.2 COD Orders
- **Post-verification page shows:**
    - Amount to Collect
    - Button: Collect Amount

**Options for Collection:**
- **Collect Cash**
    - Modal: Confirm cash collection
    - Success: "Amount collected."
- **Generate QR**
    - QR code display
    - Verify Payment button becomes active
    - Success: "Amount collected online."

### 6️⃣ Navigation & UI Features

#### 6.1 Notification Page
- **Accessible via notification icon**
- **List of alerts/updates shown in card format**

#### 6.2 Profile Page
- **Rider's Profile Info:**
    - User ID, Full Name, Approval Status

#### 6.3 Side Navigation Drawer
- **Links to:**
    - Home
    - Amount Summary
    - Profile
    - Notifications

### 7️⃣ Amount Summary
- **List view of completed runsheets with:**
    - Runsheet No.
    - Total Orders
    - Runsheet Transactional Summary:
        - Upcoming Transactions
        - QR Payments Amount
        - Cash on Hand

## ⚙️ Technical Considerations

### Backend Integration Points
- OTP service
- Registration & document upload storage
- Runsheet & order assignment (from Admin panel)
- Payment verification (UPI integration)
- Notification delivery (Firebase / internal push system)

### Roles & Permissions
- **Rider (App user):** Full access to assigned modules
- **Admin (Backend panel user):** Approve/reject registrations, assign runsheets, track deliveries

## 📱 Platform Support
- **Primary:** Android app
- **Optional:** iOS (based on rider availability and demand)

## 🧪 QA and Error Handling

### Validation
- Input validations for forms, bank details
- Image upload size and format checks
- OTP expiry and resend cooldown

### Errors
- Clear error messages for invalid OTP, form inputs, failed uploads
- Retry options for failed payment verifications or photo uploads

## 🛠️ Future Enhancements (Post-MVP)
- Route optimization for delivery sequence
- GPS location tagging per delivery
- Chat with customer
- Offline mode for low-connectivity areas
- Multilingual support
