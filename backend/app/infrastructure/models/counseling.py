from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional

class CounselingMessage(Document):
    tenant_id: str
    student_id: str
    subject: str
    message: str
    topic: Optional[str] = None
    is_anonymous: bool = True
    requested_by: Optional[str] = None
    request_date: datetime = Field(default_factory=datetime.utcnow)
    response: Optional[str] = None
    responder_id: Optional[str] = None
    status: str = "pending"
    responded_at: Optional[datetime] = None

    class Settings:
        name = "counseling_messages"
