from datetime import datetime
from app.infrastructure.database.repositories.applicant_repository import ApplicantRepository

class PublishOffersUseCase:
    def __init__(self, applicant_repo: ApplicantRepository):
        self.applicant_repo = applicant_repo

    async def execute(self, tenant_id: str) -> dict:
        applicants = await self.applicant_repo.get_by_status(tenant_id, "allocated")

        published_count = 0
        for applicant in applicants:
            await self.applicant_repo.update(str(applicant.id), {
                "status": "offered",
                "updated_at": datetime.utcnow(),
            })
            published_count += 1

        return {"published_offers": published_count}

    async def accept_offer(self, applicant_id: str) -> dict:
        applicant = await self.applicant_repo.get_by_id(applicant_id)
        if not applicant:
            raise ValueError("Applicant not found")

        if applicant.status != "offered":
            raise ValueError("No active offer to accept")

        await self.applicant_repo.update(applicant_id, {
            "status": "accepted",
            "offer_accepted": True,
            "offer_accepted_at": datetime.utcnow(),
        })

        return {"applicant_id": applicant_id, "status": "accepted"}

    async def reject_offer(self, applicant_id: str, reason: str = None) -> dict:
        await self.applicant_repo.update(applicant_id, {
            "status": "rejected",
            "eligibility_reason": reason,
        })

        return {"applicant_id": applicant_id, "status": "rejected"}
