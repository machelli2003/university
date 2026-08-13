from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CourseItem(BaseModel):
    id: str
    code: str
    title: str

class AttendanceMarkRequest(BaseModel):
    student_id: str
    course_id: str
    session_date: datetime
    is_present: bool

class AttendanceItem(BaseModel):
    student_id: str
    course_id: str
    session_date: datetime
    is_present: bool
    marked_by: str

class GradeEntry(BaseModel):
    student_id: str
    score: float
    remarks: Optional[str] = None

class GradeSubmissionRequest(BaseModel):
    grades: List[GradeEntry]
    submission_notes: Optional[str] = None
