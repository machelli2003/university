from app.infrastructure.models.user import User
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import Optional, List

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    @staticmethod
    def normalize_email(email: str) -> str:
        return (email or "").strip().lower()

    async def get_by_email(self, email: str) -> Optional[User]:
        normalized = self.normalize_email(email)
        return await self.model.find_one({"email": normalized})

    async def get_by_tenant_and_role(self, tenant_id: str, role: str) -> List[User]:
        return await self.model.find({"tenant_id": tenant_id, "role": role}).to_list(None)

    async def exists_by_email(self, email: str) -> bool:
        normalized = self.normalize_email(email)
        return await self.model.find_one({"email": normalized}) is not None

    async def get_users(self, tenant_id: Optional[str] = None, include_inactive: bool = False) -> List[User]:
        query = {}
        if not include_inactive:
            query["is_active"] = True
        if tenant_id is not None:
            query["tenant_id"] = tenant_id
        return await self.model.find(query).to_list(None)

    async def get_active_users(self, tenant_id: Optional[str] = None) -> List[User]:
        return await self.get_users(tenant_id, include_inactive=False)

    async def increment_login_attempts(self, user_id: str):
        user = await self.get_by_id(user_id)
        if user:
            await self.update(user_id, {"login_attempts": user.login_attempts + 1})

    async def reset_login_attempts(self, user_id: str):
        await self.update(user_id, {"login_attempts": 0})
