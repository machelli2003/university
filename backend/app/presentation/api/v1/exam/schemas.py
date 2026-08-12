from pydantic import BaseModel
from typing import Optional

class SubmitGradeRequest(BaseModel):
    student_id: str
    course_id: str
    academic_year: str
    semester: str
    continuous_assessment: float
    practical_score: Optional[float] = None
    mid_semester_score: Optional[float] = None
    final_exam_score: float

class GradeResponse(BaseModel):
    grade_id: str
    total_score: float
    letter_grade: str
    status: str
