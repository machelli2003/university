from app.infrastructure.models.accommodation import Hall, Room, Accommodation, MaintenanceRequest
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional

class HallRepository(BaseRepository[Hall]):
    def __init__(self):
        super().__init__(Hall)

    async def get_all_for_tenant(self, tenant_id: str) -> List[Hall]:
        return await self.model.find({
            "tenant_id": tenant_id
        }).to_list(None)

class RoomRepository(BaseRepository[Room]):
    def __init__(self):
        super().__init__(Room)

    async def get_by_hall(self, hall_id: str) -> List[Room]:
        return await self.model.find({
            "hall_id": hall_id
        }).to_list(None)

    async def get_available_rooms(self, hall_id: str) -> List[Room]:
        return await self.model.find({
            "hall_id": hall_id,
            "occupied": {"$lt": "capacity"}
        }).to_list(None)

class AccommodationRepository(BaseRepository[Accommodation]):
    def __init__(self):
        super().__init__(Accommodation)

    async def get_by_student(self, tenant_id: str, student_id: str) -> Optional[Accommodation]:
        return await self.model.find_one({
            "tenant_id": tenant_id,
            "student_id": student_id,
            "is_active": True
        })

    async def get_by_room(self, room_id: str) -> List[Accommodation]:
        return await self.model.find({
            "room_id": room_id,
            "is_active": True
        }).to_list(None)

class MaintenanceRequestRepository(BaseRepository[MaintenanceRequest]):
    def __init__(self):
        super().__init__(MaintenanceRequest)

    async def get_by_hall(self, hall_id: str) -> List[MaintenanceRequest]:
        return await self.model.find({
            "hall_id": hall_id
        }).to_list(None)

    async def get_pending_requests(self, tenant_id: str) -> List[MaintenanceRequest]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "status": "pending"
        }).to_list(None)
