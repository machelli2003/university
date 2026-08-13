from app.infrastructure.models.tenant import Tenant
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional

class TenantRepository(BaseRepository[Tenant]):
    def __init__(self):
        super().__init__(Tenant)

    async def get_active_tenants(self) -> List[Tenant]:
        return await self.model.find({"is_active": True}).to_list(None)

    async def get_all_tenants(self, include_inactive: bool = False) -> List[Tenant]:
        if include_inactive:
            return await self.model.find({}).to_list(None)
        return await self.get_active_tenants()

    async def get_by_subdomain(self, subdomain: str) -> Optional[Tenant]:
        return await self.model.find_one({"subdomain": subdomain})

    async def get_by_school_code(self, school_code: str) -> Optional[Tenant]:
        return await self.model.find_one({"school_code": school_code})

    async def exists(self, **kwargs) -> bool:
        return await self.model.find_one(kwargs) is not None
