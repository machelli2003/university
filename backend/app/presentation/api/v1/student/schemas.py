from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StudentProfile(BaseModel):
    id: str
    student_id: str
    first_name: str
    last_name: str
    email: str
    programme_id: str
    faculty_id: str
    department_id: str
    fee_balance: float


class TranscriptItem(BaseModel):
    academic_year: str
    semester: str
    courses: List[dict]
    cgpa: Optional[float]
    created_at: datetime


class StudentStatusUpdate(BaseModel):
    status: str


class StudentDashboardResponse(BaseModel):
    profile: StudentProfile
    transcripts: List[TranscriptItem]
    outstanding_fees: float
    payments: List[dict]
