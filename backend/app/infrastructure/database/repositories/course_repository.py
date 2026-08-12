from app.infrastructure.models.academic import Course, Program, Faculty, Department
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional

class CourseRepository(BaseRepository[Course]):
    def __init__(self):
        super().__init__(Course)

    async def get_by_code(self, tenant_id: str, code: str) -> Optional[Course]:
        return await self.model.find_one({
            "tenant_id": tenant_id,
            "code": code
        })

    async def get_by_lecturer(self, lecturer_id: str) -> List[Course]:
        return await self.model.find({
            "lecturer_id": lecturer_id
        }).to_list(None)

    async def get_with_prerequisites(self, course_id: str) -> List[Course]:
        course = await self.get_by_id(course_id)
        if not course:
            return []
        return await self.model.find({
            "_id": {"$in": course.prerequisites}
        }).to_list(None)

class ProgramRepository(BaseRepository[Program]):
    def __init__(self):
        super().__init__(Program)

    async def get_by_code(self, tenant_id: str, code: str) -> Optional[Program]:
        return await self.model.find_one({
            "tenant_id": tenant_id,
            "code": code
        })

    async def get_by_department(self, department_id: str) -> List[Program]:
        return await self.model.find({
            "department_id": department_id
        }).to_list(None)

    async def get_accredited(self, tenant_id: str) -> List[Program]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "accreditation_status": "accredited"
        }).to_list(None)

class FacultyRepository(BaseRepository[Faculty]):
    def __init__(self):
        super().__init__(Faculty)

    async def get_by_code(self, tenant_id: str, code: str) -> Optional[Faculty]:
        return await self.model.find_one({
            "tenant_id": tenant_id,
            "code": code
        })

class DepartmentRepository(BaseRepository[Department]):
    def __init__(self):
        super().__init__(Department)

    async def get_by_faculty(self, faculty_id: str) -> List[Department]:
        return await self.model.find({
            "faculty_id": faculty_id
        }).to_list(None)
