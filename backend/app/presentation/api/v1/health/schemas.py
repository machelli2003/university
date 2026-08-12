from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateHealthRecordRequest(BaseModel):
    student_id: str
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    emergency_contact: str
    emergency_phone: str

class BookAppointmentRequest(BaseModel):
    student_id: str
    appointment_date: datetime
    reason: str

class CounselingRequestSchema(BaseModel):
    topic: Optional[str] = None
    is_anonymous: bool = True
