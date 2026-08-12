from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class HealthRecord(Document):
    tenant_id: str
    student_id: str

    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None

    emergency_contact: str
    emergency_phone: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "health_records"

class ClinicAppointment(Document):
    tenant_id: str
    student_id: str

    appointment_date: datetime
    reason: str
    status: str = "scheduled"

    notes: Optional[str] = None

    class Settings:
        name = "clinic_appointments"

class Counseling(Document):
    tenant_id: str
    student_id: str

    request_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"

    topic: Optional[str] = None
    is_anonymous: bool = True

    class Settings:
        name = "counseling"
