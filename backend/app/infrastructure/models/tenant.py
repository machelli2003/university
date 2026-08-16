from beanie import Document
from pydantic import Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

DEFAULT_TENANT_FEATURES = {
    "admissions": True,
    "finance": True,
    "academic": True,
    "exam": True,
    "accommodation": True,
    "library": True,
    "hr": True,
    "health": True,
    "research": True,
    "alumni": True,
}

class SubscriptionTierEnum(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class Tenant(Document):
    name: str
    description: Optional[str] = None
    subdomain: str
    school_code: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None

    primary_color: str = "#3b82f6"
    secondary_color: str = "#8b5cf6"
    accent_color: str = "#ec4899"

    subscription_tier: SubscriptionTierEnum = SubscriptionTierEnum.STARTER
    subscription_start: datetime = Field(default_factory=datetime.utcnow)
    subscription_end: Optional[datetime] = None

    is_active: bool = True
    is_trial: bool = True

    admin_email: str
    admin_phone: Optional[str] = None
    country: str = "Ghana"
    timezone: str = "Africa/Accra"

    features: dict = Field(default_factory=lambda: DEFAULT_TENANT_FEATURES.copy())

    @field_validator("features", mode="before")
    @classmethod
    def normalize_features(cls, value):
        return DEFAULT_TENANT_FEATURES.copy() if value is None else value

    identifier_formats: dict = Field(default_factory=lambda: {
        "student_id": "{SCHOOL_CODE}-{YEAR}-{SEQUENCE}",
        "staff_id": "{SCHOOL_CODE}-STF-{SEQUENCE}",
        "applicant_id": "{SCHOOL_CODE}-APP-{YEAR}-{SEQUENCE}",
        "university_application_id": "UAPP-{YEAR}-{SEQUENCE}",
    })

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "tenants"

class Subscription(Document):
    tenant_id: str
    tier: SubscriptionTierEnum
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True
    payment_status: str

    class Settings:
        name = "subscriptions"
