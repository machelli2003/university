from typing import List
from app.infrastructure.database.repositories.applicant_repository import ApplicantRepository
from app.infrastructure.database.repositories.course_repository import ProgramRepository
from app.domain.admissions.eligibility_engine import EligibilityEngine

class EvaluateEligibilityUseCase:
    def __init__(
        self,
        applicant_repo: ApplicantRepository,
        program_repo: ProgramRepository,
        eligibility_engine: EligibilityEngine
    ):
        self.applicant_repo = applicant_repo
        self.program_repo = program_repo
        self.eligibility_engine = eligibility_engine

    async def execute(self, applicant_id: str):
        applicant = await self.applicant_repo.get_by_id(applicant_id)
        if not applicant:
            raise ValueError("Applicant not found")

        status_val = applicant.status.value if hasattr(applicant.status, "value") else str(applicant.status)
        if status_val not in ["results_approved", "submitted", "results_uploaded", "under_review"]:
            raise ValueError(f"Results must be approved before eligibility check (current status: {status_val})")

        eligible_programmes = []
        skipped_programmes = []

        for choice in applicant.programme_choices:
            programme_id = choice.get("programme_id")
            programme = await self.program_repo.get_by_id(programme_id)

            if not programme:
                # Programme not found in DB — treat as no restrictions (open admission)
                skipped_programmes.append(programme_id)
                eligible_programmes.append(programme_id)
                continue

            requirements = {
                "required_subjects": programme.required_subjects or [],
                "minimum_grades": programme.minimum_grades or {},
                "aggregate_threshold": programme.aggregate_threshold,
            }

            # If programme has no requirements configured at all, treat as eligible
            if not requirements["required_subjects"] and not requirements["minimum_grades"] and not requirements["aggregate_threshold"]:
                eligible_programmes.append(programme_id)
                continue

            result = await self.eligibility_engine.check_eligibility(
                applicant.results, requirements
            )

            if result.is_eligible:
                eligible_programmes.append(programme_id)

        is_eligible = len(eligible_programmes) > 0
        reason = (
            f"Eligible for {len(eligible_programmes)} programme(s)"
            if is_eligible else "Not eligible for any chosen programme"
        )

        await self.applicant_repo.update_eligibility(applicant_id, is_eligible, reason)

        new_status = "eligible" if is_eligible else "ineligible"
        await self.applicant_repo.update(applicant_id, {"status": new_status})

        return {
            "applicant_id": applicant_id,
            "is_eligible": is_eligible,
            "eligible_programmes": eligible_programmes,
            "reason": reason,
        }

    async def bulk_evaluate(self, tenant_id: str) -> dict:
        applicants = await self.applicant_repo.get_by_status(tenant_id, "results_approved")

        results = {"eligible": 0, "ineligible": 0, "errors": 0}

        for applicant in applicants:
            try:
                result = await self.execute(str(applicant.id))
                if result["is_eligible"]:
                    results["eligible"] += 1
                else:
                    results["ineligible"] += 1
            except Exception:
                results["errors"] += 1

        return results
