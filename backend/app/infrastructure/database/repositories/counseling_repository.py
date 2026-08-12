from typing import List, Optional
from app.infrastructure.models.counseling import CounselingMessage
from app.infrastructure.database.repositories.base_repository import BaseRepository

class CounselingRepository(BaseRepository[CounselingMessage]):
    def __init__(self):
        super().__init__(CounselingMessage)

    async def get_pending_for_tenant(self, tenant_id: str) -> List[CounselingMessage]:
        return await self.model.find({"tenant_id": tenant_id, "status": "pending"}).to_list(None)

    async def get_for_student(self, tenant_id: str, student_id: str) -> List[CounselingMessage]:
        return await self.model.find({"tenant_id": tenant_id, "student_id": student_id}).to_list(None)
