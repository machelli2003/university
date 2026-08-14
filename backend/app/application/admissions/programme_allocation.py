"""
Programme Allocation Service
Items 19-31: Allocate admitted applicants to programmes

Handles:
- Matching applicants to their programme choices
- Respecting programme capacities
- Managing waiting lists
- Processing appeals
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AllocationResult:
    """Result of programme allocation."""
    applicant_id: str
    allocated_programme_id: Optional[str]
    status: str  # "allocated", "waitlisted", "rejected"
    primary_choice: str
    second_choice: Optional[str]
    third_choice: Optional[str]
    allocation_rank: Optional[int]
    reason: str


class ProgrammeAllocationService:
    """
    Match admitted applicants to available programmes.
    
    Respects:
    - Applicant's programme preferences
    - Programme capacities
    - Admission quotas
    - Merit ranking
    """
    
    async def allocate_applicants(
        self,
        admitted_applicants: List[Dict[str, Any]],
        programme_capacities: Dict[str, int],
        force_first_choice: bool = True,
    ) -> List[AllocationResult]:
        """
        Allocate admitted applicants to programmes.
        
        Algorithm:
        1. Process applicants in merit order (best first)
        2. Try to assign to first choice
        3. If full, try second choice
        4. If all full, waitlist
        
        Args:
            admitted_applicants: Sorted list of admitted applicants
            programme_capacities: Available seats per programme
            force_first_choice: If True, only allocate first choice (stricter)
        
        Returns:
            List of allocation results
        """
        allocations = []
        programme_remaining = dict(programme_capacities)  # Copy
        programme_allocated = {}  # Track allocated per programme
        
        for prog_id in programme_capacities:
            programme_allocated[prog_id] = []
        
        for applicant in admitted_applicants:
            # Get programme preferences
            first_choice = applicant.get("programme_choices", {}).get("first")
            second_choice = applicant.get("programme_choices", {}).get("second")
            third_choice = applicant.get("programme_choices", {}).get("third")
            
            allocated_to = None
            status = "rejected"
            reason = "No available programmes"
            
            # Try first choice
            if first_choice and programme_remaining.get(first_choice, 0) > 0:
                allocated_to = first_choice
                status = "allocated"
                reason = "Allocated to first choice"
                programme_remaining[first_choice] -= 1
                programme_allocated[first_choice].append(applicant["id"])
            
            # Try second choice (if first not taken and not forced first)
            elif not force_first_choice and second_choice and programme_remaining.get(second_choice, 0) > 0:
                allocated_to = second_choice
                status = "allocated"
                reason = "Allocated to second choice (first choice full)"
                programme_remaining[second_choice] -= 1
                programme_allocated[second_choice].append(applicant["id"])
            
            # Try third choice
            elif not force_first_choice and third_choice and programme_remaining.get(third_choice, 0) > 0:
                allocated_to = third_choice
                status = "allocated"
                reason = "Allocated to third choice"
                programme_remaining[third_choice] -= 1
                programme_allocated[third_choice].append(applicant["id"])
            
            # Waitlist for first choice
            elif first_choice:
                status = "waitlisted"
                reason = "Waitlisted for first choice (programme full)"
            
            allocation = AllocationResult(
                applicant_id=applicant["id"],
                allocated_programme_id=allocated_to,
                status=status,
                primary_choice=first_choice or "none",
                second_choice=second_choice,
                third_choice=third_choice,
                allocation_rank=len(programme_allocated.get(allocated_to or "", [])),
                reason=reason,
            )
            allocations.append(allocation)
        
        # Log summary
        allocated_count = sum(1 for a in allocations if a.status == "allocated")
        waitlisted_count = sum(1 for a in allocations if a.status == "waitlisted")
        logger.info(f"✅ Allocation complete: {allocated_count} allocated, {waitlisted_count} waitlisted")
        
        return allocations
    
    async def process_waiting_list(
        self,
        programme_id: str,
        waiting_list: List[Dict[str, Any]],
        newly_available_seats: int,
    ) -> List[AllocationResult]:
        """
        Process waiting list when seats become available.
        
        When applicant rejects offer or withdraws, seat opens up.
        Waitlisted applicants are promoted.
        """
        promoted = []
        
        for i, applicant in enumerate(waiting_list[:newly_available_seats]):
            allocation = AllocationResult(
                applicant_id=applicant["id"],
                allocated_programme_id=programme_id,
                status="allocated",
                primary_choice=programme_id,
                second_choice=None,
                third_choice=None,
                allocation_rank=None,
                reason="Promoted from waiting list",
            )
            promoted.append(allocation)
        
        logger.info(f"✅ Promoted {len(promoted)} applicants from waiting list for programme {programme_id}")
        return promoted
    
    async def handle_rejection(
        self,
        applicant_id: str,
        programme_id: str,
        rejection_reason: str,
    ) -> Dict[str, Any]:
        """
        Handle applicant rejection (didn't accept offer).
        
        Makes seat available for waitlisted applicants.
        """
        return {
            "applicant_id": applicant_id,
            "programme_id": programme_id,
            "rejection_reason": rejection_reason,
            "seat_released": True,
            "released_at": datetime.utcnow(),
        }


class WaitlistManagementService:
    """Manage waiting lists for oversubscribed programmes."""
    
    async def add_to_waitlist(
        self,
        applicant_id: str,
        programme_id: str,
        choice_order: int,  # 1st, 2nd, 3rd choice
    ) -> Dict[str, Any]:
        """Add applicant to programme waiting list."""
        
        waitlist_entry = {
            "applicant_id": applicant_id,
            "programme_id": programme_id,
            "choice_order": choice_order,
            "added_date": datetime.utcnow(),
            "position": None,  # Will be assigned
            "status": "waiting",
        }
        
        # TODO: Save to MongoDB WaitingList collection
        logger.info(f"➕ Added {applicant_id} to waitlist for programme {programme_id}")
        return waitlist_entry
    
    async def get_waitlist(
        self,
        programme_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get waiting list for programme (in priority order)."""
        # TODO: Query MongoDB WaitingList
        # Order by: choice_order (1st choice first), then added_date
        return []
    
    async def promote_from_waitlist(
        self,
        programme_id: str,
        count: int,
    ) -> List[Dict[str, Any]]:
        """Promote top waitlisted applicants."""
        waitlist = await self.get_waitlist(programme_id, limit=count)
        promoted = waitlist[:count]
        
        for entry in promoted:
            # Update status to promoted
            # TODO: Save to MongoDB
            logger.info(f"⬆️ Promoted {entry['applicant_id']} from waitlist")
        
        return promoted
