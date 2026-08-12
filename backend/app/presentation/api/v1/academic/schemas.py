from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CreateFacultyRequest(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class CreateDepartmentRequest(BaseModel):
    faculty_id: str
    name: str
    code: str

class CreateProgramRequest(BaseModel):
    department_id: str
    faculty_id: str
    name: str
    code: str
    duration_years: int = 4
    required_subjects: List[str] = []
    minimum_grades: dict = {}
    aggregate_threshold: Optional[int] = None
    capacity_planned: int = 100

class CreateCourseRequest(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    credit_hours: int
    course_type: str = "core"
    prerequisites: List[str] = []
    lecturer_id: Optional[str] = None

class RegisterCoursesRequest(BaseModel):
    student_id: str
    course_ids: List[str]
    academic_year: str
    semester: str

class CourseResponse(BaseModel):
    id: str
    code: str
    name: str
    credit_hours: int
    course_type: str

class ProgramResponse(BaseModel):
    id: str
    name: str
    code: str
    duration_years: int
    capacity_planned: int
    capacity_current: int


class CreateAcademicCalendarRequest(BaseModel):
    academic_year: str
    semester: str
    registration_open: Optional[datetime] = None
    registration_close: Optional[datetime] = None
    exam_period_start: Optional[datetime] = None
    exam_period_end: Optional[datetime] = None


class UpdateAcademicCalendarRequest(BaseModel):
    registration_open: Optional[datetime] = None
    registration_close: Optional[datetime] = None
    exam_period_start: Optional[datetime] = None
    exam_period_end: Optional[datetime] = None
