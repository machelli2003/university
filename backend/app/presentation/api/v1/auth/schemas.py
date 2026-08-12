from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

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
