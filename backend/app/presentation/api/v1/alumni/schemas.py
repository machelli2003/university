from pydantic import BaseModel
from typing import Optional

class CreateAlumniProfileRequest(BaseModel):
    student_id: str
    graduation_year: int
    current_occupation: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None

class RequestMentorshipRequest(BaseModel):
    mentor_id: str

class MakeDonationRequest(BaseModel):
    amount: float
    purpose: str
