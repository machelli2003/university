from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PaymentMethodEnum(str, Enum):
    MOBILE_MONEY = "mobile_money"
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"
    CASH = "cash"

class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FeeStructure(Document):
    tenant_id: str
    programme_id: Optional[str] = None
    level: Optional[str] = None
    academic_year: str

    fees: dict = {}

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "fee_structures"

class Payment(Document):
    tenant_id: str
    student_id: Optional[str] = None
    applicant_id: Optional[str] = None

    amount: float
    fee_type: str
    academic_year: Optional[str] = None

    payment_method: PaymentMethodEnum
    payment_reference: str
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING

    paystack_reference: Optional[str] = None

    payment_date: Optional[datetime] = None
    receipt_number: Optional[str] = None
    receipt_pdf_url: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "payments"
        indexes = [
            [("tenant_id", 1), ("student_id", 1)],
            [("status", 1)],
            [("payment_date", 1)],
        ]

class Scholarship(Document):
    tenant_id: str
    student_id: str

    name: str
    scholarship_type: str
    amount: float
    percentage: Optional[float] = None

    approved_by: str
    approved_date: datetime

    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True

    class Settings:
        name = "scholarships"
