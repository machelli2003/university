from app.infrastructure.models.student import Student
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import Optional, List

class StudentRepository(BaseRepository[Student]):
    def __init__(self):
        super().__init__(Student)

    async def get_by_user_id(self, tenant_id: str, user_id: str) -> Optional[Student]:
        return await self.model.find_one({
            "tenant_id": tenant_id,
            "user_id": user_id
        })

    async def get_by_student_id(self, tenant_id: str, student_id: str) -> Optional[Student]:
        return await self.model.find_one({
            "tenant_id": tenant_id,
            "student_id": student_id
        })

    async def get_by_programme(self, tenant_id: str, programme_id: str) -> List[Student]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "programme_id": programme_id
        }).to_list(None)

    async def get_by_registered_course(self, tenant_id: str, course_id: str) -> List[Student]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "registered_courses": course_id
        }).to_list(None)

    async def get_by_status(self, tenant_id: str, status: str) -> List[Student]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "status": status
        }).to_list(None)

    async def get_by_hall(self, hall_id: str) -> List[Student]:
        return await self.model.find({
            "hall_id": hall_id
        }).to_list(None)

    async def get_on_probation(self, tenant_id: str) -> List[Student]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "is_on_probation": True
        }).to_list(None)

    async def get_with_fee_balance(self, tenant_id: str) -> List[Student]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "fee_balance": {"$gt": 0}
        }).to_list(None)
