from app.infrastructure.models.alumni import AlumniProfile, Mentorship, Donation
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional

class AlumniProfileRepository(BaseRepository[AlumniProfile]):
    def __init__(self):
        super().__init__(AlumniProfile)

    async def get_by_student(self, student_id: str) -> Optional[AlumniProfile]:
        return await self.model.find_one({"student_id": student_id})

    async def get_by_graduation_year(self, tenant_id: str, year: int) -> List[AlumniProfile]:
        return await self.model.find({"tenant_id": tenant_id, "graduation_year": year}).to_list(None)

class MentorshipRepository(BaseRepository[Mentorship]):
    def __init__(self):
        super().__init__(Mentorship)

    async def get_by_mentee(self, mentee_id: str) -> List[Mentorship]:
        return await self.model.find({"mentee_id": mentee_id, "is_active": True}).to_list(None)

class DonationRepository(BaseRepository[Donation]):
    def __init__(self):
        super().__init__(Donation)

    async def get_by_donor(self, donor_id: str) -> List[Donation]:
        return await self.model.find({"donor_id": donor_id}).to_list(None)

    async def get_total_for_tenant(self, tenant_id: str) -> float:
        donations = await self.model.find({"tenant_id": tenant_id}).to_list(None)
        return sum(d.amount for d in donations)
