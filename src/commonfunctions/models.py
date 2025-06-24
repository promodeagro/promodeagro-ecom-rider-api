from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum


class DocumentType(str, Enum):
    USER_PHOTO = "userPhoto"
    AADHAR_FRONT = "aadharFront"
    AADHAR_BACK = "aadharback"
    PAN = "pan"
    DRIVING_FRONT = "drivingFront"
    DRIVING_BACK = "drivingBack"
    VEHICLE_IMAGE = "VehicleImage"
    RC_FRONT = "rcFront"
    RC_BACK = "rcBack"


class PaymentMethod(str, Enum):
    CASH = "cash"
    UPI = "upi"


class Address(BaseModel):
    address1: str = Field(..., min_length=1, description="Address line 1")
    address2: Optional[str] = Field(None, description="Address line 2")
    landmark: Optional[str] = Field(None, description="Landmark")
    state: str = Field(..., min_length=1, description="State")
    city: str = Field(..., min_length=1, description="City")
    pincode: str = Field(..., min_length=5, description="Pincode")


class Reference(BaseModel):
    relation: str = Field(..., min_length=1, description="Relation")
    number: str = Field(..., pattern=r'^\d{10}$', description="Reference phone number")


class PersonalDetails(BaseModel):
    fullName: str = Field(..., min_length=3, description="Full name")
    dob: str = Field(..., description="Date of birth in ISO format")
    email: str = Field(..., description="Email address")
    number: str = Field(..., pattern=r'^\d{10}$', description="Phone number")
    address: Address
    reference: Reference


class BankDetails(BaseModel):
    bankName: str = Field(..., min_length=3, description="Bank name")
    acc: str = Field(..., min_length=1, description="Account number")
    ifsc: str = Field(..., min_length=11, description="IFSC code")


class Document(BaseModel):
    name: DocumentType
    image: str = Field(..., description="Document image URL")


class RiderRegistration(BaseModel):
    personalDetails: PersonalDetails
    bankDetails: BankDetails
    documents: List[Document] = Field(..., min_items=1, description="Required documents")


class PhoneNumberRequest(BaseModel):
    number: str = Field(..., pattern=r'^\d{10}$', description="Phone number")


class OTPValidationRequest(BaseModel):
    number: str = Field(..., pattern=r'^\d{10}$', description="Phone number")
    code: str = Field(..., pattern=r'^\d{6}$', description="6-digit OTP")
    session: str = Field(..., description="Session token")


class RefreshTokenRequest(BaseModel):
    refreshToken: str = Field(..., description="Refresh token")


class SignoutRequest(BaseModel):
    accessToken: str = Field(..., description="Access token")


class OrderCompletionRequest(BaseModel):
    image: str = Field(..., description="Delivery image URL")
    via: Optional[PaymentMethod] = Field(None, description="Payment method")


class OrderCancellationRequest(BaseModel):
    reason: str = Field(..., min_length=1, description="Cancellation reason")


class RiderUpdateRequest(BaseModel):
    id: str = Field(..., description="Rider ID")
    personalDetails: Optional[PersonalDetails] = None
    bankDetails: Optional[BankDetails] = None
    document: Optional[Document] = None


class APIResponse(BaseModel):
    statusCode: int
    body: dict
    headers: Optional[dict] = None


class ErrorResponse(BaseModel):
    message: str
    error: Optional[str] = None


class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None


# Response models for specific endpoints
class SigninResponse(BaseModel):
    message: str
    session: str


class OTPValidationResponse(BaseModel):
    message: str
    user: dict
    tokens: dict


class RiderResponse(BaseModel):
    id: str
    number: str
    name: str
    profileStatus: dict
    personalDetails: PersonalDetails
    bankDetails: BankDetails
    documents: List[Document]
    reviewStatus: str
    submittedAt: str
    updatedAt: str
    accountVerified: bool
    role: str


class RunsheetResponse(BaseModel):
    id: str
    orders: int
    pendingOrders: int
    status: str
    deliveredOrders: int
    undeliveredOrders: int
    amountCollectable: float


class OrderResponse(BaseModel):
    id: str
    status: str
    paymentDetails: dict
    deliveredAt: Optional[str] = None
    deliveredImage: Optional[str] = None


class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    read: bool
    createdAt: str
    ttl: Optional[int] = None