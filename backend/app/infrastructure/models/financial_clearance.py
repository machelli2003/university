from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ClearanceStatusEnum(str, Enum):
    """Financial clearance status for students"""
    PENDING = "pending"  # Not yet evaluated
    CLEARED = "cleared"  # Student has paid all fees
    CONDITIONAL = "conditional"  # Payment plan approved
    OUTSTANDING = "outstanding"  # Student owes balance
    HOLD = "hold"  # Clearance on hold (debt recovery in progress)
    REVOKED = "revoked"  # Previously cleared, now owing money again

class FinancialClearance(Document):
    """Track financial clearance status for each student"""
    tenant_id: str
    student_id: str
    academic_year: str

    status: ClearanceStatusEnum = ClearanceStatusEnum.PENDING
    
    # Financial breakdown
    total_fees: float = 0.0
    total_paid: float = 0.0
    total_scholarships: float = 0.0
    outstanding_balance: float = 0.0
    
    # Clearance tracking
    cleared_by: Optional[str] = None  # Staff ID who approved clearance
    cleared_at: Optional[datetime] = None
    revoked_by: Optional[str] = None
    revoked_at: Optional[datetime] = None
    revoked_reason: Optional[str] = None
    
    # Payment plan
    has_payment_plan: bool = False
    payment_plan_approved_by: Optional[str] = None
    payment_plan_approved_at: Optional[datetime] = None
    payment_plan_deadline: Optional[datetime] = None
    
    # Audit trail
    clearance_history: list = []  # List of {status_change, timestamp, actor}
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Notes
    notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "financial_clearances"
        indexes = [
            [("tenant_id", 1), ("student_id", 1), ("academic_year", 1)],
            [("status", 1)],
            [("cleared_at", 1)],
        ]
