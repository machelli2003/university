from app.infrastructure.models.hr import StaffMember, Leave, PerformanceAppraisal
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional

class StaffMemberRepository(BaseRepository[StaffMember]):
    def __init__(self):
        super().__init__(StaffMember)

    async def get_by_user_id(self, tenant_id: str, user_id: str) -> Optional[StaffMember]:
        return await self.model.find_one({"tenant_id": tenant_id, "user_id": user_id})

    async def get_by_department(self, department_id: str) -> List[StaffMember]:
        return await self.model.find({"department_id": department_id}).to_list(None)

class LeaveRepository(BaseRepository[Leave]):
    def __init__(self):
        super().__init__(Leave)

    async def get_by_staff(self, staff_id: str) -> List[Leave]:
        return await self.model.find({"staff_id": staff_id}).to_list(None)

    async def get_pending(self, tenant_id: str) -> List[Leave]:
        return await self.model.find({"tenant_id": tenant_id, "status": "pending"}).to_list(None)

class PerformanceAppraisalRepository(BaseRepository[PerformanceAppraisal]):
    def __init__(self):
        super().__init__(PerformanceAppraisal)

    async def get_by_staff(self, staff_id: str) -> List[PerformanceAppraisal]:
        return await self.model.find({"staff_id": staff_id}).to_list(None)
