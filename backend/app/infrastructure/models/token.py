from beanie import Document
from datetime import datetime
from pydantic import Field


class BlacklistedToken(Document):
    token: str
    reason: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "blacklisted_tokens"
