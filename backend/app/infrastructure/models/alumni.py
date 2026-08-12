from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class AlumniProfile(Document):
    tenant_id: str
    student_id: str

    current_occupation: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None

    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    linkedin_url: Optional[str] = None

    graduation_year: int

    class Settings:
        name = "alumni_profiles"

class Mentorship(Document):
    tenant_id: str
    mentor_id: str
    mentee_id: str

    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True

    class Settings:
        name = "mentorships"

class Donation(Document):
    tenant_id: str
    donor_id: str

    amount: float
    donation_date: datetime
    purpose: str

    receipt_url: Optional[str] = None

    class Settings:
        name = "donations"
