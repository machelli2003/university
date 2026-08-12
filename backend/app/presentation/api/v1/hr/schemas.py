from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateStaffRequest(BaseModel):
    user_id: str
    employee_id: str
    first_name: str
    last_name: str
    department_id: Optional[str] = None
    position: str
    employment_date: datetime
    contract_type: str

class LeaveRequest(BaseModel):
    leave_type: str
    start_date: datetime
    end_date: datetime
    reason: str

class ApproveLeaveRequest(BaseModel):
    leave_id: str
