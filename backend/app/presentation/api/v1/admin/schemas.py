from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class AdminCreateUserRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    age: Optional[int] = None
    password: str
    role: str
    tenant_id: Optional[str] = None
    permissions: Optional[List[str]] = []
    must_change_password: Optional[bool] = None

class AdminUpdateUserRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    permissions: Optional[List[str]] = None
    login_attempts: Optional[int] = None
    locked_until: Optional[datetime] = None

class ChangeStaffRoleRequest(BaseModel):
    new_role: str
    permissions: Optional[List[str]] = None
    reason: Optional[str] = None

class AddPermissionRequest(BaseModel):
    permission: str
    reason: Optional[str] = None
