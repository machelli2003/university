from typing import Dict, Optional
from datetime import datetime
from app.infrastructure.database.repositories.applicant_repository import (
    ApplicantRepository, ApplicantResultRepository
)
from app.domain.admissions.waec_service import ManualResultsEntryService
from app.infrastructure.models.applicant import ApplicationStatusEnum

class SubmitManualResultsUseCase:
    """Applicant submits results manually (before WAEC API integration)"""

    def __init__(
        self,
        applicant_repo: ApplicantRepository,
        result_repo: ApplicantResultRepository,
        manual_service: ManualResultsEntryService
    ):
        self.applicant_repo = applicant_repo
        self.result_repo = result_repo
        self.manual_service = manual_service

    async def execute(
        self,
        tenant_id: str,
        applicant_id: str,
        results: Dict[str, str],
        uploaded_by: str
    ):
        applicant = await self.applicant_repo.get_by_id(applicant_id)
        if not applicant:
            raise ValueError("Applicant not found")

        for subject, grade in results.items():
            entry = await self.manual_service.create_result_entry(
                applicant_id=applicant_id,
                subject=subject,
                grade=grade,
                uploaded_by=uploaded_by,
            )
            await self.result_repo.create({
                "tenant_id": tenant_id,
                "applicant_id": applicant_id,
                "subject": entry["subject"],
                "grade": entry["grade"],
                "uploaded_by": entry["uploaded_by"],
                "uploaded_at": entry["uploaded_at"],
            })

        await self.applicant_repo.update(applicant_id, {
            "results": results,
            "status": ApplicationStatusEnum.RESULTS_UPLOADED,
            "updated_at": datetime.utcnow(),
        })

        return await self.applicant_repo.get_by_id(applicant_id)


class ApproveResultsUseCase:
    """Admin/Admissions Officer approves manually uploaded results"""

    def __init__(
        self,
        applicant_repo: ApplicantRepository,
        result_repo: ApplicantResultRepository
    ):
        self.applicant_repo = applicant_repo
        self.result_repo = result_repo

    async def execute(
        self,
        applicant_id: str,
        approved_by: str,
        aggregate: Optional[int] = None
    ):
        applicant = await self.applicant_repo.get_by_id(applicant_id)
        if not applicant:
            raise ValueError("Applicant not found")

        if applicant.status != "results_uploaded":
            raise ValueError(f"Cannot approve results in status: {applicant.status}")

        if aggregate is None:
            aggregate = self._calculate_aggregate(applicant.results)

        results = await self.result_repo.get_by_applicant(applicant_id)
        for result in results:
            approved_by_field = getattr(result, "approved_by", None) if not isinstance(result, dict) else result.get("approved_by")
            result_id = str(result.id) if not isinstance(result, dict) else result.get("id")
            if not approved_by_field:
                await self.result_repo.update(result_id, {
                    "approved_by": approved_by,
                    "approved_at": datetime.utcnow(),
                })

        updated = await self.applicant_repo.update(applicant_id, {
            "aggregate": aggregate,
            "results_approved_by": approved_by,
            "results_approved_at": datetime.utcnow(),
            "status": "results_approved",
            "updated_at": datetime.utcnow(),
        })

        return updated

    async def reject(
        self,
        applicant_id: str,
        rejected_by: str,
        reason: str
    ):
        updated = await self.applicant_repo.update(applicant_id, {
            "status": "submitted",
            "eligibility_reason": f"Results rejected: {reason}",
            "updated_at": datetime.utcnow(),
        })

        return updated

    def _calculate_aggregate(self, results: dict) -> int:
        grade_scores = {
            "A1": 1, "A": 1, "B2": 2, "B3": 3, "C4": 4,
            "C5": 5, "C6": 6, "D7": 7, "D8": 8, "E": 9, "F": 9
        }

        scores = sorted([grade_scores.get(g, 9) for g in results.values()])
        best_six = scores[:6] if len(scores) >= 6 else scores

        return sum(best_six)


class GetPendingVerificationsUseCase:
    """Get all applicants awaiting results approval"""

    def __init__(self, applicant_repo: ApplicantRepository):
        self.applicant_repo = applicant_repo

    async def execute(self, tenant_id: str):
        return await self.applicant_repo.get_pending_verification(tenant_id)
