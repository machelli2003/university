from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ApplicationFormStatusEnum(str, Enum):
    """Status of an application form (PIN + Serial)"""
    PURCHASED = "purchased"  # Paid but not used
    USED = "used"  # Successfully used to login
    EXPIRED = "expired"  # Admission cycle closed
    CANCELLED = "cancelled"  # Refunded or cancelled


class ApplicationForm(Document):
    """
    Application form purchase record with PIN and Serial number.
    
    In Ghana, universities provide PIN and Serial numbers to applicants
    who have paid the application fee. These credentials are then used
    to access the application portal.
    
    This model stores:
    - The generated PIN and Serial number
    - Payment information
    - Status tracking
    - Usage tracking
    """
    
    # Unique identifiers (generated at purchase)
    pin: Indexed(str)  # Unique PIN for this form
    serial_number: Indexed(str)  # Unique Serial for this form
    
    # Reference information
    admission_cycle_id: str  # Which admission cycle this is for
    academic_year: str  # e.g., "2023/2024"
    
    # Applicant information (optional until they use it)
    applicant_id: Optional[str] = None  # Linked after first login
    applicant_email: Optional[str] = None  # Email used to purchase
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    
    # Payment information
    amount: float  # Amount paid in currency
    currency: str = "GHS"  # Default to Ghana Cedis
    payment_method: str = "paystack"
    payment_reference: str  # Paystack reference or internal ref
    paystack_reference: Optional[str] = None  # Paystack payment reference
    payment_status: str = "completed"  # Payment verification status
    
    # Status tracking
    status: ApplicationFormStatusEnum = ApplicationFormStatusEnum.PURCHASED
    
    # Usage tracking
    first_login_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    login_count: int = 0
    
    # Real Credentials Transition
    # After applicant is accepted, real permanent credentials are issued
    permanent_credential_id: Optional[str] = None  # Link to PermanentCredential record
    has_real_credentials: bool = False  # Whether real credentials have been issued
    credential_issued_at: Optional[datetime] = None  # When real credentials were issued
    application_decision: Optional[str] = None  # OFFERED, REJECTED, WAITLISTED
    decision_date: Optional[datetime] = None  # When decision was made
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    
    # Notes
    notes: Optional[str] = None
    
    class Settings:
        name = "application_forms"
        indexes = [
            [("pin", 1)],  # Fast lookup by PIN
            [("serial_number", 1)],  # Fast lookup by Serial
            [("applicant_id", 1)],  # Find forms by applicant
            [("admission_cycle_id", 1), ("status", 1)],  # Find active forms for cycle
            [("payment_reference", 1)],  # Track payments
            [("created_at", -1)],  # Recent forms first
        ]
