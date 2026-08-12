from app.infrastructure.models.academic import AcademicCalendar
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional

class AcademicCalendarRepository(BaseRepository[AcademicCalendar]):
    def __init__(self):
        super().__init__(AcademicCalendar)

    async def get_by_period(self, tenant_id: str, academic_year: str, semester: str) -> Optional[AcademicCalendar]:
        return await self.model.find_one({
            "tenant_id": tenant_id,
            "academic_year": academic_year,
            "semester": semester,
        })

    async def get_all_for_tenant(self, tenant_id: str) -> List[AcademicCalendar]:
        return await self.model.find({"tenant_id": tenant_id}).to_list(None)
