from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class StudentProfile(BaseModel):
    id: str
    student_id: str
    first_name: str
    last_name: str
    email: str
    programme_id: Optional[str] = None
    faculty_id: Optional[str] = None
    department_id: Optional[str] = None
    fee_balance: float = 0.0
    cgpa: Optional[float] = 0.0
    current_gpa: Optional[float] = 0.0
    level: Optional[str] = None        # e.g. "Level 200"
    academic_year: Optional[str] = None  # e.g. "2025/2026"
    status: Optional[str] = None


class CourseItem(BaseModel):
    course_id: str
    code: str
    name: str
    credit_hours: int = 3
    lecturer_id: Optional[str] = None
    grade: Optional[str] = None


class TimetableSlot(BaseModel):
    day: str
    time: str
    course: str       # course code
    course_name: str
    room: Optional[str] = None
    lecturer: Optional[str] = None


class TranscriptItem(BaseModel):
    academic_year: str
    semester: str
    courses: List[dict]
    cgpa: Optional[float] = None
    created_at: Optional[datetime] = None


class StudentStatusUpdate(BaseModel):
    status: str


class StudentDashboardResponse(BaseModel):
    profile: StudentProfile
    courses: List[CourseItem] = []
    timetable: List[TimetableSlot] = []
    transcripts: List[TranscriptItem] = []
    outstanding_fees: float = 0.0
    payments: List[dict] = []


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
