from app.infrastructure.models.applicant import Applicant, ApplicantResult
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import Optional, List
from datetime import datetime

class ApplicantRepository(BaseRepository[Applicant]):
    def __init__(self):
        super().__init__(Applicant)

    async def get_by_user_id(self, tenant_id: str, user_id: str) -> Optional[Applicant]:
        return await self.model.find_one({
            "tenant_id": tenant_id,
            "user_id": user_id
        })

    async def get_by_index_number(self, tenant_id: str, index_number: str) -> Optional[Applicant]:
        return await self.model.find_one({
            "tenant_id": tenant_id,
            "index_number": index_number
        })

    async def get_by_status(self, tenant_id: str, status: str) -> List[Applicant]:
        query: dict = {"status": status}
        if tenant_id and tenant_id != "default":
            query["tenant_id"] = tenant_id
        return await self.model.find(query).to_list(None)

    async def get_pending_verification(self, tenant_id: str) -> List[Applicant]:
        query = {"status": {"$in": ["awaiting_results", "results_uploaded", "submitted", "under_review"]}}
        if tenant_id and tenant_id != "default":
            query["tenant_id"] = tenant_id
        return await self.model.find(query).to_list(None)

    async def get_eligible_applicants(self, tenant_id: str) -> List[Applicant]:
        # Trust status field — don't require is_eligible flag which may not be set
        query: dict = {"status": {"$in": ["eligible", "ranked", "results_approved"]}}
        if tenant_id and tenant_id != "default":
            query["tenant_id"] = tenant_id
        return await self.model.find(query).to_list(None)

    async def get_by_programme_choice(self, tenant_id: str, programme_id: str) -> List[Applicant]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "programme_choices.programme_id": programme_id
        }).to_list(None)

    async def get_ranked_for_programme(self, tenant_id: str, programme_id: str) -> List[Applicant]:
        results = await self.model.find({
            "tenant_id": tenant_id,
            "programme_choices.programme_id": programme_id,
            "is_eligible": True
        }).sort([("merit_rank", 1)]).to_list(None)
        return results

    async def update_eligibility(self, applicant_id: str, is_eligible: bool, reason: str):
        await self.update(applicant_id, {
            "is_eligible": is_eligible,
            "eligibility_reason": reason
        })

    async def approve_results(self, applicant_id: str, approved_by: str):
        await self.update(applicant_id, {
            "results_approved_by": approved_by,
            "results_approved_at": datetime.utcnow(),
            "status": "results_approved"
        })

class ApplicantResultRepository(BaseRepository[ApplicantResult]):
    def __init__(self):
        super().__init__(ApplicantResult)

    async def get_by_applicant(self, applicant_id: str) -> List[ApplicantResult]:
        return await self.model.find({
            "applicant_id": applicant_id
        }).to_list(None)

    async def get_pending_approval(self, tenant_id: str) -> List[ApplicantResult]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "approved_by": None
        }).to_list(None)
