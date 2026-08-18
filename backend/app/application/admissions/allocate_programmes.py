from typing import List
from app.infrastructure.database.repositories.applicant_repository import ApplicantRepository
from app.infrastructure.database.repositories.course_repository import ProgramRepository
from app.domain.admissions.allocation_engine import AllocationEngine

class AllocateProgrammesUseCase:
    def __init__(
        self,
        applicant_repo: ApplicantRepository,
        program_repo: ProgramRepository,
        allocation_engine: AllocationEngine
    ):
        self.applicant_repo = applicant_repo
        self.program_repo = program_repo
        self.allocation_engine = allocation_engine

    async def execute(self, tenant_id: str) -> dict:
        # Fetch both eligible and ranked applicants (eligible = ready for allocation)
        query: dict = {"status": {"$in": ["eligible", "ranked"]}}
        if tenant_id and tenant_id != "default":
            query["tenant_id"] = tenant_id
        applicants = await self.applicant_repo.model.find(query).to_list(None)

        applicant_dicts = [
            {
                "applicant_id": str(a.id),
                "merit_rank": a.merit_rank,
            }
            for a in sorted(applicants, key=lambda x: x.merit_rank or 999999)
        ]

        applicant_choices = {
            str(a.id): a.programme_choices for a in applicants
        }

        programme_ids = set()
        for a in applicants:
            for choice in a.programme_choices:
                programme_ids.add(choice.get("programme_id"))

        programme_capacities = {}
        for prog_id in programme_ids:
            programme = await self.program_repo.get_by_id(prog_id)
            if programme:
                programme_capacities[prog_id] = {
                    "planned_capacity": programme.capacity_planned,
                    "reserved_capacity": programme.capacity_reserved,
                }

        allocations = await self.allocation_engine.allocate_programmes(
            applicant_dicts, programme_capacities, applicant_choices
        )

        allocated_count = 0
        waitlisted_count = 0

        for allocation in allocations:
            if allocation.allocation_status == "allocated":
                await self.applicant_repo.update(allocation.applicant_id, {
                    "allocated_programme_id": allocation.allocated_programme_id,
                    "status": "allocated",
                })
                allocated_count += 1
            else:
                await self.applicant_repo.update(allocation.applicant_id, {
                    "status": "waitlisted",
                })
                waitlisted_count += 1

        return {
            "total_processed": len(allocations),
            "allocated": allocated_count,
            "waitlisted": waitlisted_count,
        }
