from typing import Optional, List
from datetime import datetime
from app.infrastructure.database.repositories.applicant_repository import ApplicantRepository
from app.infrastructure.models.applicant import Applicant, ApplicationStatusEnum

class ApplyForAdmissionUseCase:
    def __init__(self, applicant_repo: ApplicantRepository):
        self.applicant_repo = applicant_repo

    async def execute(
        self,
        tenant_id: str,
        user_id: str,
        first_name: str,
        last_name: str,
        phone: str,
        date_of_birth: Optional[datetime] = None,
        gender: Optional[str] = None,
        address: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Applicant:
        existing = await self.applicant_repo.get_by_user_id(tenant_id, user_id)
        if existing:
            raise ValueError("Application already exists for this user")

        applicant_data = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "address": address,
            "region": region,
            "status": ApplicationStatusEnum.DRAFT,
        }

        return await self.applicant_repo.create(applicant_data)

    async def submit_application(
        self,
        applicant_id: str,
        index_number: str,
        exam_year: int,
        exam_type: str,
        programme_choices: List[dict]
    ) -> Applicant:
        updated = await self.applicant_repo.update(applicant_id, {
            "index_number": index_number,
            "exam_year": exam_year,
            "exam_type": exam_type,
            "programme_choices": programme_choices,
            "status": ApplicationStatusEnum.SUBMITTED,
            "updated_at": datetime.utcnow(),
        })

        if not updated:
            raise ValueError("Applicant not found")

        return updated
