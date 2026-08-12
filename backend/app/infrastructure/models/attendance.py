from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Attendance(Document):
    tenant_id: str
    student_id: str
    course_id: str

    session_date: datetime
    is_present: bool
    marked_by: str

    method: str = "manual"
    qr_code_id: Optional[str] = None

    marked_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "attendance"
        indexes = [
            [("student_id", 1), ("course_id", 1), ("session_date", 1)],
        ]
