from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum

class SubscriptionTierEnum(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class Tenant(Document):
    name: str
    description: Optional[str] = None
    subdomain: str
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

    features: dict = {
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
