from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ApplicationFormLoginRequest(BaseModel):
    """Login using PIN and Serial number from application form purchase"""
    pin: str = Field(..., min_length=6, max_length=6, description="6-digit PIN")
    serial_number: str = Field(..., min_length=8, max_length=8, description="8-character Serial")
    email: EmailStr = Field(..., description="Applicant email for verification")
    first_name: Optional[str] = Field(None, description="First name (optional, from form purchase)")
    last_name: Optional[str] = Field(None, description="Last name (optional, from form purchase)")

class PermanentCredentialLoginRequest(BaseModel):
    """Login with permanent credentials (after acceptance)"""
    username: str = Field(..., min_length=3, description="Username")
    password: str = Field(..., min_length=8, description="Password")

class ChangeTemporaryPasswordRequest(BaseModel):
    """Change temporary password on first permanent credential login"""
    old_password: str = Field(..., description="Current temporary password")
    new_password: str = Field(..., min_length=8, description="New permanent password")

class RegisterRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class UserResponse(BaseModel):
    id: str
    tenant_id: Optional[str] = None
    email: str
    first_name: str
    last_name: str
    age: Optional[int] = None
    role: str
    permissions: List[str]
    is_active: bool
    is_verified: bool
    must_change_password: bool = False
    login_attempts: Optional[int] = None
    locked_until: Optional[datetime] = None
    created_at: datetime

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse

class RegisterResponse(BaseModel):
    id: str
    email: str
    message: str = "Registration successful"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class PermanentCredentialIssuedResponse(BaseModel):
    """Response when real credentials are issued to an applicant"""
    success: bool
    message: str
    credential_id: str
    username: str
    activation_deadline: datetime
    must_change_password: bool


