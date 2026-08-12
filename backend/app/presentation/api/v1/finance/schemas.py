from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.infrastructure.models.tenant import SubscriptionTierEnum

class InitiatePaymentRequest(BaseModel):
    student_id: str
    amount: float
    fee_type: str
    payment_method: str

class ConfirmPaymentRequest(BaseModel):
    payment_id: str
    paystack_reference: str

class PaymentResponse(BaseModel):
    payment_id: str
    payment_reference: str
    amount: float
    status: str

class PaymentHistoryItem(BaseModel):
    id: str
    amount: float
    fee_type: str
    status: str
    payment_date: Optional[datetime]
    receipt_number: Optional[str]

class PaymentListItem(BaseModel):
    id: str
    tenant_id: str
    student_id: Optional[str] = None
    applicant_id: Optional[str] = None
    amount: float
    fee_type: str
    academic_year: Optional[str] = None
    payment_method: str
    payment_reference: str
    status: str
    paystack_reference: Optional[str] = None
    payment_date: Optional[datetime] = None
    receipt_number: Optional[str] = None
    created_at: datetime

class BalanceResponse(BaseModel):
    total_due: float
    total_paid: float
    total_scholarships: float
    balance: float

class ClearanceResponse(BaseModel):
    student_id: str
    tenant_id: str
    is_cleared: bool
    message: str
    balance: float
    pending_payments: int

class FeeStructureCreateRequest(BaseModel):
    programme_id: Optional[str] = None
    level: Optional[str] = None
    academic_year: str
    fees: Dict[str, float]

class FeeStructureResponse(BaseModel):
    id: str
    programme_id: Optional[str] = None
    level: Optional[str] = None
    academic_year: str
    fees: Dict[str, float]

class FeeStructureUpdateRequest(BaseModel):
    programme_id: Optional[str] = None
    level: Optional[str] = None
    academic_year: Optional[str] = None
    fees: Optional[Dict[str, float]] = None

class ScholarshipRequest(BaseModel):
    student_id: str
    name: str
    scholarship_type: str
    amount: float
    percentage: Optional[float] = None
    start_date: datetime
    end_date: Optional[datetime] = None

class ScholarshipResponse(BaseModel):
    id: str
    student_id: str
    name: str
    scholarship_type: str
    amount: float
    percentage: Optional[float] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool

class TenantResponse(BaseModel):
    id: str
    name: str
    subdomain: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    admin_email: str
    admin_phone: Optional[str] = None
    country: str
    timezone: str
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    subscription_tier: SubscriptionTierEnum
    subscription_start: datetime
    subscription_end: Optional[datetime] = None
    is_active: bool
    is_trial: bool
    features: Dict[str, bool]

class TenantCreateRequest(BaseModel):
    name: str
    subdomain: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    admin_email: EmailStr
    admin_phone: Optional[str] = None
    country: str = "Ghana"
    timezone: str = "Africa/Accra"
    primary_color: Optional[str] = "#3b82f6"
    secondary_color: Optional[str] = "#8b5cf6"
    accent_color: Optional[str] = "#ec4899"
    subscription_tier: Optional[SubscriptionTierEnum] = SubscriptionTierEnum.STARTER
    features: Optional[Dict[str, bool]] = None

class TenantUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    admin_email: Optional[EmailStr] = None
    admin_phone: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    subscription_tier: Optional[SubscriptionTierEnum] = None
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_trial: Optional[bool] = None
    features: Optional[Dict[str, bool]] = None

class AuditSummaryResponse(BaseModel):
    total_events: int
    event_types: Dict[str, int]
    recent_events: List[Dict[str, Any]]


class AuditEventResponse(BaseModel):
    event_type: str
    entity_type: str
    entity_id: Optional[str] = None
    action: str
    performed_by: Optional[str] = None
    details: Dict[str, Any]
    created_at: datetime


class AuditListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    events: List[AuditEventResponse]
