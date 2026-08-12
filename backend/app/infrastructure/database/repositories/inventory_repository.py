from app.infrastructure.models.inventory import Asset, Inventory, MaintenanceSchedule
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List

class AssetRepository(BaseRepository[Asset]):
    def __init__(self):
        super().__init__(Asset)

    async def get_by_type(self, tenant_id: str, asset_type: str) -> List[Asset]:
        return await self.model.find({"tenant_id": tenant_id, "asset_type": asset_type}).to_list(None)

    async def get_assigned_to(self, assigned_to: str) -> List[Asset]:
        return await self.model.find({"assigned_to": assigned_to}).to_list(None)

class InventoryRepository(BaseRepository[Inventory]):
    def __init__(self):
        super().__init__(Inventory)

    async def get_low_stock(self, tenant_id: str) -> List[Inventory]:
        items = await self.model.find({"tenant_id": tenant_id}).to_list(None)
        return [i for i in items if i.quantity <= i.reorder_level]

class MaintenanceScheduleRepository(BaseRepository[MaintenanceSchedule]):
    def __init__(self):
        super().__init__(MaintenanceSchedule)

    async def get_by_asset(self, asset_id: str) -> List[MaintenanceSchedule]:
        return await self.model.find({"asset_id": asset_id}).to_list(None)

    async def get_upcoming(self, tenant_id: str) -> List[MaintenanceSchedule]:
        return await self.model.find({"tenant_id": tenant_id, "status": "scheduled"}).to_list(None)
