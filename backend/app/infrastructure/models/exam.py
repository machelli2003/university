from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AssessmentTypeEnum(str, Enum):
    CONTINUOUS = "continuous"
    PRACTICAL = "practical"
    MID_SEMESTER = "mid_semester"
    FINAL_EXAM = "final_exam"

class GradeStatusEnum(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    APPEALED = "appealed"

class Assessment(Document):
    tenant_id: str
    course_id: str
    student_id: str

    assessment_type: AssessmentTypeEnum
    score: float
    max_score: float = 100.0

    submitted_date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "assessments"

class Grade(Document):
    tenant_id: str
    student_id: str
    course_id: str
    academic_year: str
    semester: str

    continuous_assessment: Optional[float] = None
    practical_score: Optional[float] = None
    mid_semester_score: Optional[float] = None
    final_exam_score: Optional[float] = None

    total_score: float = 0.0
    letter_grade: Optional[str] = None
    gpa_points: Optional[float] = None

    status: GradeStatusEnum = GradeStatusEnum.SUBMITTED
    submitted_by: str
    submitted_date: datetime
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None

    remarks: Optional[str] = None

    class Settings:
        name = "grades"
        indexes = [
            [("student_id", 1), ("academic_year", 1), ("semester", 1)],
        ]

class Transcript(Document):
    tenant_id: str
    student_id: str

    academic_year: str
    semester: str

    gpa: float
    cgpa: float

    courses_taken: List[dict] = []

    generated_date: datetime = Field(default_factory=datetime.utcnow)
    signed: bool = False
    signed_by: Optional[str] = None

    qr_code: Optional[str] = None

    class Settings:
        name = "transcripts"

class GradeAppeal(Document):
    tenant_id: str
    student_id: str
    grade_id: str

    reason: str
    status: str = "pending"
    resolution: Optional[str] = None

    appeal_date: datetime = Field(default_factory=datetime.utcnow)
    reviewed_by: Optional[str] = None
    review_date: Optional[datetime] = None

    class Settings:
        name = "grade_appeals"
