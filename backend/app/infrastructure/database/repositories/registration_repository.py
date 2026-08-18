from app.infrastructure.models.academic import Registration
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional

class RegistrationRepository(BaseRepository[Registration]):
    def __init__(self):
        super().__init__(Registration)

    async def get_by_student(self, tenant_id: str, student_id: str) -> List[Registration]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "student_id": student_id
        }).sort([("academic_year", -1)]).to_list(None)

    async def get_by_period(self, tenant_id: str, academic_year: str, semester: str) -> List[Registration]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "academic_year": academic_year,
            "semester": semester
        }).to_list(None)

    async def get_all_for_tenant(self, tenant_id: str) -> List[Registration]:
        return await self.model.find({
            "tenant_id": tenant_id
        }).to_list(None)

    async def get_by_course(self, tenant_id: str, course_id: str) -> List[Registration]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "course_ids": course_id
        }).to_list(None)
