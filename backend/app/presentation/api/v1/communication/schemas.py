from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SendNotificationRequest(BaseModel):
    recipient_id: str
    title: str
    message: str
    notification_type: str = "in_app"

class CreateCampaignRequest(BaseModel):
    name: str
    message: str
    target_role: Optional[str] = None
    target_students: List[str] = []
    scheduled_date: Optional[datetime] = None
