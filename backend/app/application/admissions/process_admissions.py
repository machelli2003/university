from typing import List, Dict
from app.application.admissions.evaluate_eligibility import EvaluateEligibilityUseCase
from app.application.admissions.rank_applicants import RankApplicantsUseCase
from app.application.admissions.allocate_programmes import AllocateProgrammesUseCase
from app.application.admissions.publish_offers import PublishOffersUseCase
from app.infrastructure.database.repositories.applicant_repository import ApplicantRepository
from app.infrastructure.database.repositories.course_repository import ProgramRepository
from app.domain.admissions.eligibility_engine import EligibilityEngine
from app.domain.admissions.merit_ranking import MeritRankingEngine
from app.domain.admissions.allocation_engine import AllocationEngine

class ProcessAdmissionsPipelineUseCase:
    def __init__(
        self,
        applicant_repo: ApplicantRepository,
        program_repo: ProgramRepository,
        eligibility_engine: EligibilityEngine,
        ranking_engine: MeritRankingEngine,
        allocation_engine: AllocationEngine,
    ):
        self.applicant_repo = applicant_repo
        self.program_repo = program_repo
        self.eligibility_engine = eligibility_engine
        self.ranking_engine = ranking_engine
        self.allocation_engine = allocation_engine

    async def execute(self, tenant_id: str) -> Dict[str, int]:
        eligibility_use_case = EvaluateEligibilityUseCase(
            self.applicant_repo, self.program_repo, self.eligibility_engine
        )
        ranking_use_case = RankApplicantsUseCase(
            self.applicant_repo, self.program_repo, self.ranking_engine
        )
        allocation_use_case = AllocateProgrammesUseCase(
            self.applicant_repo, self.program_repo, self.allocation_engine
        )
        publish_use_case = PublishOffersUseCase(self.applicant_repo)

        eligibility_summary = await eligibility_use_case.bulk_evaluate(tenant_id)

        programmes = await self.program_repo.get_all(tenant_id=tenant_id)
        ranked_count = 0
        for programme in programmes:
            try:
                ranked = await ranking_use_case.execute(tenant_id, str(programme.id))
                ranked_count += len(ranked)
            except Exception:
                continue

        allocation_summary = await allocation_use_case.execute(tenant_id)
        publish_summary = await publish_use_case.execute(tenant_id)

        return {
            "eligible": eligibility_summary.get("eligible", 0),
            "ineligible": eligibility_summary.get("ineligible", 0),
            "ranked": ranked_count,
            "allocated": allocation_summary.get("allocated", 0),
            "waitlisted": allocation_summary.get("waitlisted", 0),
            "offers_published": publish_summary.get("published_offers", 0),
        }
