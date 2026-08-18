from app.infrastructure.models.communication import Notification, NotificationTemplate, Campaign
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self):
        super().__init__(Notification)

    async def get_by_recipient(self, recipient_id: str) -> List[Notification]:
        return await self.model.find({
            "recipient_id": recipient_id
        }).sort([("created_at", -1)]).to_list(None)

    async def get_unread(self, recipient_id: str) -> List[Notification]:
        return await self.model.find({
            "recipient_id": recipient_id,
            "is_read": False
        }).to_list(None)

    async def mark_as_read(self, notification_id: str):
        from datetime import datetime
        await self.update(notification_id, {
            "is_read": True,
            "read_at": datetime.utcnow()
        })

class NotificationTemplateRepository(BaseRepository[NotificationTemplate]):
    def __init__(self):
        super().__init__(NotificationTemplate)

    async def get_by_code(self, tenant_id: str, code: str) -> Optional[NotificationTemplate]:
        return await self.model.find_one({
            "tenant_id": tenant_id,
            "code": code
        })

class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self):
        super().__init__(Campaign)

    async def get_by_tenant(self, tenant_id: str) -> List[Campaign]:
        return await self.model.find({
            "tenant_id": tenant_id
        }).to_list(None)
