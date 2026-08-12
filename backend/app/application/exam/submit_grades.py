from datetime import datetime
from typing import Optional
from app.infrastructure.database.repositories.grade_repository import GradeRepository
from app.domain.exam.grade_calculator import GradeCalculator
from app.infrastructure.models.exam import GradeStatusEnum

class SubmitGradesUseCase:
    def __init__(self, grade_repo: GradeRepository, grade_calculator: GradeCalculator):
        self.grade_repo = grade_repo
        self.grade_calculator = grade_calculator

    async def execute(
        self,
        tenant_id: str,
        student_id: str,
        course_id: str,
        academic_year: str,
        semester: str,
        continuous_assessment: float,
        practical_score: Optional[float],
        mid_semester_score: Optional[float],
        final_exam_score: float,
        submitted_by: str,
    ) -> dict:
        total_score = (continuous_assessment * 0.3) + (final_exam_score * 0.7)
        if practical_score:
            total_score = (continuous_assessment * 0.2) + (practical_score * 0.2) + (final_exam_score * 0.6)

        letter_grade = await self.grade_calculator.calculate_letter_grade(total_score)
        gpa_points = self.grade_calculator.GRADE_POINTS.get(letter_grade, 0.0)

        grade_data = {
            "tenant_id": tenant_id,
            "student_id": student_id,
            "course_id": course_id,
            "academic_year": academic_year,
            "semester": semester,
            "continuous_assessment": continuous_assessment,
            "practical_score": practical_score,
            "mid_semester_score": mid_semester_score,
            "final_exam_score": final_exam_score,
            "total_score": total_score,
            "letter_grade": letter_grade,
            "gpa_points": gpa_points,
            "status": GradeStatusEnum.SUBMITTED,
            "submitted_by": submitted_by,
            "submitted_date": datetime.utcnow(),
        }

        grade = await self.grade_repo.create(grade_data)

        return {
            "grade_id": str(grade.id),
            "total_score": total_score,
            "letter_grade": letter_grade,
            "status": "submitted",
        }


class ApproveGradesUseCase:
    """HOD/Dean/Registrar approval chain"""

    def __init__(self, grade_repo: GradeRepository):
        self.grade_repo = grade_repo

    async def approve(self, grade_id: str, approved_by: str) -> dict:
        updated = await self.grade_repo.update(grade_id, {
            "status": GradeStatusEnum.APPROVED,
            "approved_by": approved_by,
            "approved_date": datetime.utcnow(),
        })

        return {"grade_id": grade_id, "status": "approved"}

    async def get_pending_approvals(self, tenant_id: str) -> list:
        return await self.grade_repo.get_pending_approval(tenant_id)
