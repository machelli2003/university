from app.infrastructure.models.health import HealthRecord, ClinicAppointment, Counseling
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional

class HealthRecordRepository(BaseRepository[HealthRecord]):
    def __init__(self):
        super().__init__(HealthRecord)

    async def get_by_student(self, tenant_id: str, student_id: str) -> Optional[HealthRecord]:
        return await self.model.find_one({"tenant_id": tenant_id, "student_id": student_id})

class ClinicAppointmentRepository(BaseRepository[ClinicAppointment]):
    def __init__(self):
        super().__init__(ClinicAppointment)

    async def get_by_student(self, tenant_id: str, student_id: str) -> List[ClinicAppointment]:
        return await self.model.find({"tenant_id": tenant_id, "student_id": student_id}).to_list(None)

    async def get_upcoming(self, tenant_id: str) -> List[ClinicAppointment]:
        from datetime import datetime
        return await self.model.find({
            "tenant_id": tenant_id,
            "status": "scheduled",
            "appointment_date": {"$gte": datetime.utcnow()}
        }).to_list(None)

class CounselingRepository(BaseRepository[Counseling]):
    def __init__(self):
        super().__init__(Counseling)

    async def get_pending(self, tenant_id: str) -> List[Counseling]:
        return await self.model.find({"tenant_id": tenant_id, "status": "pending"}).to_list(None)
