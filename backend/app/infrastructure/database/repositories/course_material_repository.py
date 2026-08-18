from app.infrastructure.models.course_material import CourseMaterial
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List

class CourseMaterialRepository(BaseRepository[CourseMaterial]):
    def __init__(self):
        super().__init__(CourseMaterial)

    async def get_by_course(self, tenant_id: str, course_id: str) -> List[CourseMaterial]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "course_id": course_id,
        }).sort([("uploaded_at", -1)]).to_list(None)
