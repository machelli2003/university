from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class AllocationResult:
    applicant_id: str
    allocated_programme_id: Optional[str]
    choice_order: Optional[int]
    allocation_status: str
    fallback_programme: Optional[str] = None

class AllocationEngine:
    """Allocate programmes to applicants based on choices and merit"""

    def __init__(self):
        pass

    async def allocate_programmes(
        self,
        eligible_ranked_applicants: List[dict],
        programme_capacities: Dict[str, dict],
        applicant_choices: Dict[str, list]
    ) -> List[AllocationResult]:
        allocations = []
        programme_usage = {prog_id: 0 for prog_id in programme_capacities.keys()}
        waitlist = []

        for applicant in eligible_ranked_applicants:
            app_id = applicant.get("applicant_id")
            choices = applicant_choices.get(app_id, [])

            allocated = False

            for choice_order, choice in enumerate(choices, 1):
                programme_id = choice.get("programme_id")
                capacity_info = programme_capacities.get(programme_id, {})
                planned = capacity_info.get("planned_capacity", 0)
                reserved = capacity_info.get("reserved_capacity", 0)

                available = planned - reserved - programme_usage.get(programme_id, 0)

                if available > 0:
                    programme_usage[programme_id] += 1
                    allocations.append(AllocationResult(
                        applicant_id=app_id,
                        allocated_programme_id=programme_id,
                        choice_order=choice_order,
                        allocation_status="allocated"
                    ))
                    allocated = True
                    break

            if not allocated:
                first_choice = choices[0] if choices else None
                waitlist.append({
                    "applicant_id": app_id,
                    "first_choice": first_choice.get("programme_id") if first_choice else None,
                    "merit_rank": applicant.get("merit_rank")
                })

                allocations.append(AllocationResult(
                    applicant_id=app_id,
                    allocated_programme_id=None,
                    choice_order=None,
                    allocation_status="waitlisted",
                    fallback_programme=first_choice.get("programme_id") if first_choice else None
                ))

        return allocations

    async def get_cross_programme_recommendations(
        self,
        applicant: dict,
        all_programmes: List[dict],
        failed_choices: List[str]
    ) -> List[dict]:
        recommendations = []
        applicant_aggregate = applicant.get("aggregate", 9)

        for programme in all_programmes:
            if programme["id"] in failed_choices:
                continue

            aggregate_threshold = programme.get("aggregate_threshold")
            if aggregate_threshold and applicant_aggregate > aggregate_threshold:
                continue

            similarity = self._calculate_programme_similarity(
                failed_choices[0],
                programme,
                all_programmes
            )

            if similarity >= 0.6:
                recommendations.append({
                    "programme_id": programme["id"],
                    "programme_name": programme["name"],
                    "similarity_score": similarity,
                    "reason": f"Similar to {failed_choices[0]}"
                })

        recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
        return recommendations[:3]

    def _calculate_programme_similarity(
        self,
        choice_prog_id: str,
        candidate_prog: dict,
        all_programmes: List[dict]
    ) -> float:
        return 0.75
