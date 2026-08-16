from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    UNIVERSITY_ADMIN = "university_admin"
    REGISTRAR = "registrar"
    ADMISSIONS_OFFICER = "admissions_officer"
    DEAN = "dean"
    HEAD_OF_DEPARTMENT = "head_of_department"
    FINANCE_OFFICER = "finance_officer"
    HOSTEL_ADMINISTRATOR = "hostel_administrator"
    LIBRARIAN = "librarian"
    COUNSELOR = "counselor"
    LECTURER = "lecturer"
    STUDENT = "student"
    APPLICANT = "applicant"
    PARENT_GUARDIAN = "parent_guardian"
    AUDITOR = "auditor"

class User(Document):
    # Single-university compatibility field. The platform now runs as one institutional
    # deployment, so all users are scoped to the same university context.
    tenant_id: Optional[str] = "single-university"
    email: Indexed(EmailStr, unique=True)
    first_name: str
    last_name: str
    phone: Optional[str] = None
    age: Optional[int] = None
    password_hash: str
    role: RoleEnum
    permissions: List[str] = []
    created_by: Optional[str] = None

    is_active: bool = True
    is_verified: bool = False
    must_change_password: bool = False
    email_verified_at: Optional[datetime] = None

    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None

    last_login: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            [("email", 1)],
            [("tenant_id", 1), ("email", 1)],
            [("role", 1)],
        ]

class Role(Document):
    tenant_id: Optional[str] = None
    name: str
    description: str
    permissions: List[str] = []
    is_system_role: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "roles"

class Permission(Document):
    tenant_id: Optional[str] = None
    code: Indexed(str, unique=True)
    description: str
    module: str
    action: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "permissions"
