from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class AuditLog(Document):
    tenant_id: Optional[str] = None
    event_type: str
    entity_type: str
    entity_id: Optional[str] = None
    action: str
    performed_by: Optional[str] = None
    details: dict = {}
    ip_address: Optional[str] = None
    request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "audit_logs"
