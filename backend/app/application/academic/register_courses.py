from datetime import datetime
from typing import List, Optional
from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.infrastructure.database.repositories.student_repository import StudentRepository
from app.infrastructure.database.repositories.registration_repository import RegistrationRepository

class RegisterCoursesUseCase:
    def __init__(
        self,
        course_repo: CourseRepository,
        student_repo: StudentRepository,
        registration_repo: Optional[RegistrationRepository] = None,
    ):
        self.course_repo = course_repo
        self.student_repo = student_repo
        self.registration_repo = registration_repo

    async def execute(
        self,
        tenant_id: str,
        student_id: str,
        course_ids: List[str],
        academic_year: str,
        semester: str,
    ) -> dict:
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found")

        if student.status not in ["active", "registered"]:
            raise ValueError(f"Cannot register courses. Student status: {student.status}")

        if student.status in ["suspended", "deferred"]:
            raise ValueError("Student is currently suspended or deferred")

        registered_courses = []
        total_credits = 0

        for course_id in course_ids:
            course = await self.course_repo.get_by_id(course_id)
            if not course:
                continue

            if course.prerequisites:
                # Basic prerequisite validation can be added here.
                pass

            registered_courses.append(course_id)
            total_credits += course.credit_hours

        MIN_CREDITS = 12
        MAX_CREDITS = 24

        if total_credits < MIN_CREDITS:
            raise ValueError(f"Total credits ({total_credits}) below minimum ({MIN_CREDITS})")

        if total_credits > MAX_CREDITS:
            raise ValueError(f"Total credits ({total_credits}) exceeds maximum ({MAX_CREDITS})")

        student = await self.student_repo.update(student_id, {
            "registered_courses": registered_courses,
            "updated_at": datetime.utcnow(),
        })

        if self.registration_repo is not None:
            await self.registration_repo.create({
                "tenant_id": tenant_id,
                "student_id": student_id,
                "course_ids": registered_courses,
                "academic_year": academic_year,
                "semester": semester,
                "total_credits": total_credits,
                "status": "registered",
            })

        return {
            "student_id": student_id,
            "registered_courses": registered_courses,
            "total_credits": total_credits,
            "academic_year": academic_year,
            "semester": semester,
            "status": "registered",
        }
