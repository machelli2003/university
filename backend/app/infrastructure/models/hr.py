from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime

class StaffMember(Document):
    tenant_id: str
    user_id: str

    employee_id: str
    first_name: str
    last_name: str

    department_id: Optional[str] = None
    position: str

    employment_date: datetime
    contract_type: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "staff_members"

class Leave(Document):
    tenant_id: str
    staff_id: str

    leave_type: str
    start_date: datetime
    end_date: datetime

    reason: str
    status: str = "pending"
    approved_by: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "leaves"

class PerformanceAppraisal(Document):
    tenant_id: str
    staff_id: str

    appraisal_period: str
    rating: float
    comments: str

    reviewed_by: str
    review_date: datetime

    class Settings:
        name = "performance_appraisals"
