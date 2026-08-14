from app.infrastructure.models.finance import ApplicationFee
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import Optional, List


class ApplicationFeeRepository(BaseRepository[ApplicationFee]):
    def __init__(self):
        super().__init__(ApplicationFee)

    async def get_for_tenant(self, tenant_id: str) -> Optional[ApplicationFee]:
        return await self.model.find_one({"tenant_id": tenant_id, "is_active": True})

    async def deactivate(self, fee_id: str):
        return await self.update(fee_id, {"is_active": False})
