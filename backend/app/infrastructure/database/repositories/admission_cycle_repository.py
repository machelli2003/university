from app.infrastructure.models.admission_cycle import AdmissionCycle
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import Optional
from datetime import datetime


class AdmissionCycleRepository(BaseRepository[AdmissionCycle]):
    def __init__(self):
        super().__init__(AdmissionCycle)

    async def get_active_cycle(self, tenant_id: str) -> Optional[AdmissionCycle]:
        now = datetime.utcnow()
        # prefer explicitly active cycle
        cycle = await self.model.find_one({"tenant_id": tenant_id, "is_active": True})
        if cycle:
            return cycle

        # fallback: find cycle where now between open_date and closing_date
        cycle = await self.model.find_one({
            "tenant_id": tenant_id,
            "open_date": {"$lte": now},
            "closing_date": {"$gte": now},
        })
        return cycle
