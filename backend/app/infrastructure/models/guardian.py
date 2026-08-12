from beanie import Document
from pydantic import Field
from typing import List, Optional
from datetime import datetime

class Guardian(Document):
    tenant_id: str
    user_id: Optional[str] = None
    name: Optional[str] = None
    contact: Optional[str] = None
    student_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "guardians"
