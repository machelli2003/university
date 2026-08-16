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


class TimeSlot(BaseModel):
    day: str
    start_time: str
    end_time: str
    room: str
    lecturer: Optional[str] = None


class TimetableEntry(BaseModel):
    course_id: str
    course_code: str
    course_name: str
    credits: int
    schedule: List[TimeSlot]


class StudentTimetable(BaseModel):
    academic_year: str
    semester: str
    courses: List[TimetableEntry]


class CourseResult(BaseModel):
    course_id: str
    course_code: str
    course_name: str
    credits: int
    score: float
    grade: str
    gpa_points: float


class StudentResults(BaseModel):
    academic_year: str
    semester: str
    courses: List[CourseResult]
    gpa: float
    cgpa: float


class AcademicStanding(BaseModel):
    status: str  # "good_standing", "academic_probation", "suspension"
    current_cgpa: float
    current_gpa: float
    total_credits_earned: int
    total_courses_attempted: int
    courses_passed: int
    courses_failed: int
    last_updated: datetime
