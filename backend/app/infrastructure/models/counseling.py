from beanie import Document
from pydantic import Field
from datetime import datetime

class CounselingMessage(Document):
    tenant_id: str
    student_id: str
    subject: str
    message: str
    response: str | None = None
    responder_id: str | None = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: datetime | None = None

    class Settings:
        name = "counseling_messages"
