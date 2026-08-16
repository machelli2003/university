from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class CredentialStatusEnum(str, Enum):
    """Status of permanent credentials"""
    GENERATED = "generated"  # Created but not yet used
    ACTIVE = "active"  # In use
    DEACTIVATED = "deactivated"  # User deactivated
    EXPIRED = "expired"  # Credentials expired


class PermanentCredential(Document):
    """
    Real, permanent credentials issued to applicants after acceptance.
    
    These are issued ONLY when applicant is OFFERED admission.
    They replace the temporary PIN + Serial number for enrollment and student access.
    
    Features:
    - Username (generated from email or custom)
    - Temporary password (applicant must change on first login)
    - Status tracking
    - Audit trail
    """
    
    # Reference to applicant and application
    applicant_id: Indexed(str)  # The user/applicant ID
    application_form_id: Indexed(str)  # Link back to application form
    
    # Credentials
    username: Indexed(str)  # Unique username (e.g., derived from email)
    email: str  # Associated email
    
    # Password management
    password_hash: str  # Hashed password (bcrypt)
    temporary_password_hash: Optional[str] = None  # Temporary password before first change
    is_temporary_password: bool = True  # Flag: password needs to be changed
    
    # Admission info
    admission_cycle_id: str
    academic_year: str
    
    # Status and usage
    status: CredentialStatusEnum = CredentialStatusEnum.GENERATED
    
    # First login tracking
    first_login_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    login_count: int = 0
    
    # Credentials lifecycle
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    activation_deadline: Optional[datetime] = None  # Deadline to change password
    expires_at: Optional[datetime] = None  # When credentials expire
    
    # Access control
    is_active: bool = True
    last_password_change: Optional[datetime] = None
    password_change_required: bool = True  # Must change password on first login
    
    # Audit
    issued_by: str  # Admin/system ID that issued these
    issued_reason: str = "admission_offered"  # Why these were issued
    notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "permanent_credentials"
        indexes = [
            [("applicant_id", 1)],  # Find credentials by applicant
            [("application_form_id", 1)],  # Find by form
            [("username", 1)],  # Find by username
            [("email", 1)],  # Find by email
            [("status", 1)],  # Find by status
            [("issued_at", -1)],  # Recent credentials first
        ]
