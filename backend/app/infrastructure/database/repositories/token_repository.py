from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.models.token import BlacklistedToken


class TokenRepository(BaseRepository[BlacklistedToken]):
    def __init__(self):
        super().__init__(BlacklistedToken)

    async def is_blacklisted(self, token: str) -> bool:
        return await self.model.find_one({"token": token}) is not None

    async def blacklist(self, token: str, reason: str = None):
        await self.create({"token": token, "reason": reason})
