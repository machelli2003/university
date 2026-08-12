import pytest
from app.application.academic.register_courses import RegisterCoursesUseCase
from app.infrastructure.models.student import Student
from app.infrastructure.models.academic import Course

@pytest.mark.asyncio
async def test_register_courses_invalid_student():
    # Use a fake repository that returns None for student lookup
    class FakeStudentRepo:
        async def get_by_id(self, student_id):
            return None

    class FakeCourseRepo:
        async def get_by_id(self, course_id):
            return None

    use_case = RegisterCoursesUseCase(FakeCourseRepo(), FakeStudentRepo())

    with pytest.raises(ValueError, match="Student not found"):
        await use_case.execute("default", "fake-student", [], "2025/2026", "1")
