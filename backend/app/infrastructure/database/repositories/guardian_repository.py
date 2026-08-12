from typing import List, Optional
from app.infrastructure.models.guardian import Guardian
from app.infrastructure.database.repositories.base_repository import BaseRepository

class GuardianRepository(BaseRepository[Guardian]):
    def __init__(self):
        super().__init__(Guardian)

    async def add_student(self, tenant_id: str, user_id: str, student_id: str) -> Guardian:
        g = await self.model.find_one({"tenant_id": tenant_id, "user_id": user_id})
        if not g:
            g = Guardian(tenant_id=tenant_id, user_id=user_id, student_ids=[student_id])
            await g.insert()
            return g
        if student_id not in g.student_ids:
            g.student_ids.append(student_id)
            await g.update({"$set": {"student_ids": g.student_ids}})
        return g

    async def get_students(self, tenant_id: str, user_id: str) -> List[str]:
        g = await self.model.find_one({"tenant_id": tenant_id, "user_id": user_id})
        return g.student_ids if g else []
