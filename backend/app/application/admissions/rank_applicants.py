from typing import List
from app.infrastructure.database.repositories.applicant_repository import ApplicantRepository
from app.infrastructure.database.repositories.course_repository import ProgramRepository
from app.domain.admissions.merit_ranking import MeritRankingEngine, RankingCriteria

class RankApplicantsUseCase:
    def __init__(
        self,
        applicant_repo: ApplicantRepository,
        program_repo: ProgramRepository,
        ranking_engine: MeritRankingEngine
    ):
        self.applicant_repo = applicant_repo
        self.program_repo = program_repo
        self.ranking_engine = ranking_engine

    async def execute(
        self,
        tenant_id: str,
        programme_id: str,
        criteria: RankingCriteria = None
    ) -> List[dict]:
        programme = await self.program_repo.get_by_id(programme_id)
        if not programme:
            raise ValueError("Programme not found")

        applicants = await self.applicant_repo.get_eligible_applicants(tenant_id)

        relevant_applicants = [
            a for a in applicants
            if any(c.get("programme_id") == programme_id for c in a.programme_choices)
        ]

        applicant_dicts = [
            {
                "id": str(a.id),
                "results": a.results,
                "aggregate": a.aggregate,
                "application_date": a.application_date,
                "metadata": {},
            }
            for a in relevant_applicants
        ]

        requirements = {
            "required_subjects": programme.required_subjects,
        }

        ranked = await self.ranking_engine.rank_applicants(
            applicant_dicts, requirements, criteria
        )

        for item in ranked:
            await self.applicant_repo.update(item["applicant_id"], {
                "merit_score": item["merit_score"],
                "merit_rank": item["merit_rank"],
                "status": "ranked",
            })

        return ranked
