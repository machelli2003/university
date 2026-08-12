from app.infrastructure.models.audit import AuditLog
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import Optional, List

class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self):
        super().__init__(AuditLog)

    async def get_by_entity(self, entity_type: str, entity_id: str) -> List[AuditLog]:
        return await self.model.find({"entity_type": entity_type, "entity_id": entity_id}).to_list(None)

    async def get_by_event(self, event_type: str) -> List[AuditLog]:
        return await self.model.find({"event_type": event_type}).to_list(None)
