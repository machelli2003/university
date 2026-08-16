"""
Pydantic schemas for application form purchase and authentication.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class PurchaseApplicationFormRequest(BaseModel):
    """Request to purchase an application form"""
    
    email: EmailStr = Field(..., description="Email address")
    first_name: str = Field(..., min_length=1, description="First name")
    last_name: str = Field(..., min_length=1, description="Last name")
    phone_number: str = Field(..., min_length=10, description="Phone number")
    admission_cycle_id: str = Field(..., description="Admission cycle ID")


class PurchaseApplicationFormResponse(BaseModel):
    """Response after initiating application form purchase"""
    
    payment_url: str = Field(..., description="URL to redirect to for payment")
    reference: str = Field(..., description="Payment reference for tracking")
    access_code: str = Field(..., description="Paystack access code")
    amount: float = Field(..., description="Amount to pay in Cedis")


class VerifyApplicationFormPurchaseRequest(BaseModel):
    """Request to verify a payment and generate PIN/Serial"""
    
    reference: str = Field(..., description="Paystack payment reference")


class ApplicationFormCredentials(BaseModel):
    """Generated credentials for accessing application"""
    
    pin: str = Field(..., description="6-digit PIN for login")
    serial_number: str = Field(..., description="8-character serial number")
    payment_reference: str = Field(..., description="Internal payment reference")


class ApplicationFormPurchaseConfirmation(BaseModel):
    """Confirmation after successful purchase"""
    
    success: bool
    message: str
    credentials: Optional[ApplicationFormCredentials] = None
    email: Optional[str] = None


class ApplicationLoginRequest(BaseModel):
    """Request to login using PIN and Serial"""
    
    pin: str = Field(..., min_length=6, max_length=6, description="6-digit PIN")
    serial_number: str = Field(..., min_length=8, max_length=8, description="8-character Serial")
    email: Optional[EmailStr] = None


class ApplicationFormInfo(BaseModel):
    """Information about an application form"""
    
    id: str
    pin: str
    serial_number: str
    status: str
    admission_cycle_id: str
    academic_year: str
    amount: float
    currency: str
    applicant_id: Optional[str] = None
    applicant_email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    first_login_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    login_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True
