from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime

class Notification(Document):
    tenant_id: str
    recipient_id: str

    title: str
    message: str
    notification_type: str
    target_url: Optional[str] = None  # URL to navigate to when notification clicked

    is_read: bool = False
    read_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"
        indexes = [
            [("recipient_id", 1), ("is_read", 1)],
        ]

class NotificationTemplate(Document):
    tenant_id: str
    code: str
    name: str
    subject: str
    message_body: str

    variables: List[str] = []

    class Settings:
        name = "notification_templates"

class Campaign(Document):
    tenant_id: str
    name: str
    message: str

    target_role: Optional[str] = None
    target_students: List[str] = []

    scheduled_date: Optional[datetime] = None
    sent_date: Optional[datetime] = None

    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "campaigns"
