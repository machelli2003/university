from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class CapacityStatus:
    programme_id: str
    planned_capacity: int
    current_capacity: int
    reserved_capacity: int
    available_slots: int
    occupancy_rate: float
    reserved_rate: float
    waitlist_count: int

class CapacityManager:
    """Manage programme capacity and waitlists"""

    def __init__(self):
        pass

    async def get_capacity_status(
        self,
        programme_id: str,
        current_allocated: int,
        reserved: int,
        waitlist_count: int
    ) -> CapacityStatus:
        planned = 100

        available = planned - reserved - current_allocated
        occupancy_rate = (current_allocated / planned) * 100 if planned > 0 else 0
        reserved_rate = (reserved / planned) * 100 if planned > 0 else 0

        return CapacityStatus(
            programme_id=programme_id,
            planned_capacity=planned,
            current_capacity=current_allocated,
            reserved_capacity=reserved,
            available_slots=max(0, available),
            occupancy_rate=occupancy_rate,
            reserved_rate=reserved_rate,
            waitlist_count=waitlist_count
        )

    async def adjust_capacity(
        self,
        programme_id: str,
        new_planned_capacity: int,
        authorized_by: str
    ) -> Dict[str, any]:
        return {
            "programme_id": programme_id,
            "new_capacity": new_planned_capacity,
            "authorized_by": authorized_by,
            "timestamp": "datetime.utcnow()",
            "status": "approved"
        }

    async def check_capacity_available(
        self,
        programme_id: str,
        current_allocated: int,
        reserved: int,
        planned: int
    ) -> bool:
        return current_allocated + reserved < planned

    async def promote_from_waitlist(
        self,
        programme_id: str,
        waitlist: List[dict],
        slots_available: int
    ) -> List[dict]:
        promoted = []

        sorted_waitlist = sorted(
            waitlist,
            key=lambda x: x.get("merit_rank", float("inf"))
        )

        for i, applicant in enumerate(sorted_waitlist[:slots_available]):
            promoted.append({
                "applicant_id": applicant["applicant_id"],
                "promotion_order": i + 1,
                "previous_rank": applicant.get("merit_rank"),
                "status": "promoted_from_waitlist"
            })

        return promoted
