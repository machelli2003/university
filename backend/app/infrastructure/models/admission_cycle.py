from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class AdmissionCycle(Document):
    tenant_id: str
    name: str
    open_date: Optional[datetime] = None
    closing_date: Optional[datetime] = None
    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "admission_cycles"
