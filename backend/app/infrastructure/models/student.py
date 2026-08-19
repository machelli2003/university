from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class StudentStatusEnum(str, Enum):
    APPLICANT = "applicant"
    ADMITTED = "admitted"
    REGISTERED = "registered"
    ACTIVE = "active"
    DEFERRED = "deferred"
    SUSPENDED = "suspended"
    WITHDRAWN = "withdrawn"
    GRADUATED = "graduated"
    ALUMNI = "alumni"

from pymongo import IndexModel, ASCENDING


class Student(Document):
    tenant_id: str
    user_id: str
    applicant_id: Optional[str] = None

    first_name: str
    last_name: str
    student_id: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone: str
    email: str

    programme_id: str
    faculty_id: str
    department_id: str
    entry_level: str
    entry_semester: str
    entry_year: int

    status: StudentStatusEnum = StudentStatusEnum.REGISTERED
    status_changes: List[dict] = []

    cgpa: Optional[float] = 0.0
    current_gpa: Optional[float] = 0.0
    is_on_probation: bool = False
    probation_since: Optional[datetime] = None

    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_email: Optional[str] = None

    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None

    national_id: Optional[str] = None
    birth_certificate: Optional[str] = None
    passport: Optional[str] = None
    documents: List[str] = []

    hall_id: Optional[str] = None
    room_id: Optional[str] = None
    housing_status: Optional[str] = "unassigned"  # school_hostel, outside_hostel, private_renting, unassigned
    registered_courses: List[str] = []

    fee_balance: float = 0.0
    school_fee_paid: bool = False
    hostel_fee_paid: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "students"
        indexes = [
            IndexModel([("tenant_id", ASCENDING), ("user_id", ASCENDING)], name="idx_students_tenant_user"),
            IndexModel([("tenant_id", ASCENDING), ("student_id", ASCENDING)], name="idx_students_tenant_student_id"),
            IndexModel([("status", ASCENDING)], name="idx_students_status"),
        ]
