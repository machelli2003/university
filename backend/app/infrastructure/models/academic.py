from beanie import Document, Indexed
from pydantic import Field
from typing import Optional, List
from datetime import datetime

class Faculty(Document):
    tenant_id: str
    name: str
    code: str
    description: Optional[str] = None
    dean_id: Optional[str] = None

    class Settings:
        name = "faculties"

class Department(Document):
    tenant_id: str
    faculty_id: str
    name: str
    code: str
    description: Optional[str] = None
    head_id: Optional[str] = None

    class Settings:
        name = "departments"

class Program(Document):
    tenant_id: str
    department_id: str
    faculty_id: str
    name: str
    code: str
    description: Optional[str] = None
    duration_years: int = 4

    required_subjects: List[str] = []
    minimum_grades: dict = {}
    aggregate_threshold: Optional[int] = None

    accreditation_status: str = "accredited"
    accreditation_body: Optional[str] = None
    accreditation_expiry: Optional[datetime] = None

    capacity_planned: int = 100
    capacity_current: int = 100
    capacity_reserved: int = 0

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "programs"
        indexes = [
            [("tenant_id", 1), ("code", 1)],
            [("department_id", 1)],
        ]

class Curriculum(Document):
    tenant_id: str
    program_id: str
    version: str
    effective_date: datetime
    end_date: Optional[datetime] = None

    courses_by_level: dict = {}

    class Settings:
        name = "curriculums"

class Course(Document):
    tenant_id: str
    code: Indexed(str)
    name: str
    description: Optional[str] = None
    credit_hours: int

    course_type: str = "core"

    prerequisites: List[str] = []
    corequisites: List[str] = []
    antirequisites: List[str] = []

    lecturer_id: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "courses"

class Accreditation(Document):
    tenant_id: str
    program_id: str
    body: str
    status: str
    issue_date: datetime
    expiry_date: datetime

    class Settings:
        name = "accreditations"


class Registration(Document):
    tenant_id: str
    student_id: str
    course_ids: List[str]
    academic_year: str
    semester: str
    total_credits: int
    status: str = "registered"

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "registrations"
        indexes = [
            [("tenant_id", 1), ("student_id", 1)],
            [("tenant_id", 1), ("academic_year", 1), ("semester", 1)],
        ]


class AcademicCalendar(Document):
    tenant_id: str
    academic_year: str
    semester: str
    registration_open: Optional[datetime] = None
    registration_close: Optional[datetime] = None
    exam_period_start: Optional[datetime] = None
    exam_period_end: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "academic_calendars"
        indexes = [
            [("tenant_id", 1), ("academic_year", 1), ("semester", 1)],
        ]
