"""
Admissions Officer Backend Service
Item 40: Admissions workflow coordination

Admissions officer responsibilities:
1. Review applications in queue
2. Verify WASSCE results (manual)
3. Check applicant eligibility
4. Review complete application
5. Make admission decision (admit, reject, waitlist, conditional)
6. Generate offers
7. Track applicant status

Unified service orchestrating:
- Application state transitions
- WASSCE verification
- Eligibility checking
- Decision making
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ApplicationQueueItem(BaseModel):
    """Application in admissions queue."""
    application_id: str
    applicant_id: str
    applicant_name: str
    programme_applied: str
    submitted_at: datetime
    current_status: str
    days_in_status: int
    priority: str  # high, medium, low
    requires_attention: bool


class AdmissionsDecision(str, Enum):
    """Admission decision."""
    ADMITTED = "admitted"
    CONDITIONALLY_ADMITTED = "conditionally_admitted"
    REJECTED = "rejected"
    WAITLISTED = "waitlisted"


class AdmissionsDecisionRequest(BaseModel):
    """Request to make admission decision."""
    application_id: str
    decision: AdmissionsDecision
    decision_by: str  # Officer email
    decision_notes: str
    
    # If rejected
    rejection_reason: Optional[str] = None
    
    # If conditionally admitted
    conditions: Optional[List[str]] = None
    
    # If waitlisted
    waitlist_position: Optional[int] = None


class AdmissionOfficerDashboardData(BaseModel):
    """Dashboard data for admissions officer."""
    pending_applications: int
    applications_awaiting_wassce_verification: int
    applications_awaiting_eligibility_check: int
    applications_awaiting_review: int
    decisions_made_today: int
    offers_sent_this_month: int
    
    # Queue
    application_queue: List[ApplicationQueueItem]
    
    # Statistics
    application_stats: Dict[str, int]  # status -> count


# ==================== SERVICE ====================

class AdmissionsOfficerService:
    """
    Admissions officer workflow service.
    
    Coordinates application review from submission through decision.
    """
    
    async def get_dashboard_data(
        self,
        tenant_id: str,
        officer_id: str,
    ) -> AdmissionOfficerDashboardData:
        """Get admissions dashboard for officer."""
        
        from app.application.admissions.application_state_machine import (
            ApplicationWorkflowState, ApplicationStatus
        )
        
        # Count applications by status
        stats = {}
        for status in ApplicationStatus:
            count = await ApplicationWorkflowState.find(
                ApplicationWorkflowState.tenant_id == tenant_id,
                ApplicationWorkflowState.current_status == status.value,
            ).count()
            if count > 0:
                stats[status.value] = count
        
        # Get pending applications
        pending = await ApplicationWorkflowState.find(
            ApplicationWorkflowState.tenant_id == tenant_id,
            ApplicationWorkflowState.current_status == ApplicationStatus.SUBMITTED.value,
        ).sort([("status_since", 1)]).limit(20).to_list()
        
        queue_items = []
        for app in pending:
            days_in_status = (datetime.utcnow() - app.status_since).days
            
            # Priority: longer in queue = higher priority
            if days_in_status > 7:
                priority = "high"
            elif days_in_status > 3:
                priority = "medium"
            else:
                priority = "low"
            
            queue_items.append(ApplicationQueueItem(
                application_id=app.application_id,
                applicant_id=app.applicant_id,
                applicant_name="Applicant",  # TODO: Get from applicant record
                programme_applied="Programme",  # TODO: Get from application
                submitted_at=app.submitted_at,
                current_status=app.current_status,
                days_in_status=days_in_status,
                priority=priority,
                requires_attention=days_in_status > 5,
            ))
        
        return AdmissionOfficerDashboardData(
            pending_applications=stats.get(ApplicationStatus.SUBMITTED.value, 0),
            applications_awaiting_wassce_verification=stats.get(ApplicationStatus.WASSCE_VERIFICATION.value, 0),
            applications_awaiting_eligibility_check=stats.get(ApplicationStatus.ELIGIBILITY_CHECK.value, 0),
            applications_awaiting_review=stats.get(ApplicationStatus.UNDER_REVIEW.value, 0),
            decisions_made_today=0,  # TODO: Count decisions today
            offers_sent_this_month=0,  # TODO: Count offers this month
            application_queue=queue_items,
            application_stats=stats,
        )
    
    async def make_admission_decision(
        self,
        tenant_id: str,
        application_id: str,
        decision: AdmissionsDecision,
        officer_email: str,
        decision_notes: str,
        rejection_reason: Optional[str] = None,
        conditions: Optional[List[str]] = None,
        waitlist_position: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make final admission decision on application.
        
        Transitions to ADMITTED, CONDITIONALLY_ADMITTED, REJECTED, or WAITLISTED.
        Triggers offer generation if admitted/conditionally admitted.
        
        Args:
            tenant_id: University
            application_id: Application ID
            decision: Admission decision
            officer_email: Officer making decision
            decision_notes: Detailed notes
            rejection_reason: If rejecting
            conditions: If conditionally admitted
            waitlist_position: If waitlisted
        
        Returns:
            Decision record
        """
        
        from app.application.admissions.application_state_machine import (
            ApplicationStateService, ApplicationStatus
        )
        
        state_service = ApplicationStateService()
        
        # Map decision to status
        status_map = {
            AdmissionsDecision.ADMITTED: ApplicationStatus.ADMITTED,
            AdmissionsDecision.CONDITIONALLY_ADMITTED: ApplicationStatus.CONDITIONALLY_ADMITTED,
            AdmissionsDecision.REJECTED: ApplicationStatus.REJECTED,
            AdmissionsDecision.WAITLISTED: ApplicationStatus.WAITLISTED,
        }
        
        # Transition application
        response = await state_service.transition_status(
            application_id=application_id,
            new_status=status_map[decision].value,
            changed_by=officer_email,
            reason="Admissions decision",
            notes=decision_notes,
            rejection_reason=rejection_reason,
            conditional_requirements=conditions,
        )
        
        logger.info(
            f"✅ ADMISSION DECISION: {application_id} → {decision.value} "
            f"by {officer_email}\nNotes: {decision_notes}"
        )
        
        # TODO: Generate offer if admitted
        # TODO: Send notification to applicant
        # TODO: Update waiting list if applicable
        
        return {
            "application_id": application_id,
            "decision": decision.value,
            "decided_at": datetime.utcnow(),
            "decided_by": officer_email,
            "message": f"Admission decision recorded: {decision.value}",
        }
    
    async def get_application_for_review(
        self,
        application_id: str,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """
        Get complete application for officer review.
        
        Fetches all related data: applicant, documents, WASSCE, eligibility, etc.
        """
        
        from app.application.admissions.application_state_machine import (
            ApplicationStateService
        )
        from app.application.admissions.wassce_verification import (
            WAESSSEVerificationService
        )
        
        # Get application state
        state_service = ApplicationStateService()
        state = await state_service.get_application_state(application_id)
        
        if not state:
            raise ValueError(f"Application not found: {application_id}")
        
        # Get WASSCE verification
        wassce_service = WAESSSEVerificationService()
        wassce = await wassce_service.get_verification_record(application_id)
        
        # TODO: Get applicant details
        # TODO: Get filled application form
        # TODO: Get uploaded documents
        # TODO: Get eligibility check
        # TODO: Get any previous reviews
        
        return {
            "application_id": application_id,
            "applicant_id": state.applicant_id,
            "current_status": state.current_status,
            "submitted_at": state.submitted_at,
            "status_history": [t.dict() for t in state.status_history],
            "wassce_verification": wassce.dict() if wassce else None,
            # TODO: Add more details
        }
    
    async def send_application_to_department(
        self,
        application_id: str,
        department_id: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send application to department for further review."""
        
        from app.application.admissions.application_state_machine import (
            ApplicationStateService, ApplicationStatus
        )
        
        state_service = ApplicationStateService()
        
        await state_service.transition_status(
            application_id=application_id,
            new_status=ApplicationStatus.DEPARTMENT_REVIEW.value,
            changed_by="system",
            reason="Sent to department for review",
            notes=notes,
        )
        
        logger.info(
            f"📤 Application {application_id} sent to department {department_id} for review"
        )
        
        return {
            "application_id": application_id,
            "status": "sent_to_department",
            "department_id": department_id,
            "message": "Application forwarded to department for review",
        }
    
    async def get_applications_by_programme(
        self,
        tenant_id: str,
        programme_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all applications for specific programme."""
        
        # TODO: Query applications filtered by programme
        # Return: application_id, applicant_name, status, submitted_at
        
        return []
    
    async def get_applications_requiring_decision(
        self,
        tenant_id: str,
    ) -> List[ApplicationQueueItem]:
        """Get applications ready for admission decision."""
        
        from app.application.admissions.application_state_machine import (
            ApplicationWorkflowState, ApplicationStatus
        )
        
        # Get applications that have passed all review stages
        ready_for_decision = await ApplicationWorkflowState.find(
            ApplicationWorkflowState.tenant_id == tenant_id,
            ApplicationWorkflowState.current_status == ApplicationStatus.MANUAL_REVIEW.value,
        ).sort([("status_since", 1)]).limit(50).to_list()
        
        items = []
        for app in ready_for_decision:
            days_in_status = (datetime.utcnow() - app.status_since).days
            items.append(ApplicationQueueItem(
                application_id=app.application_id,
                applicant_id=app.applicant_id,
                applicant_name="Applicant",  # TODO
                programme_applied="Programme",  # TODO
                submitted_at=app.submitted_at,
                current_status=app.current_status,
                days_in_status=days_in_status,
                priority="high" if days_in_status > 7 else "medium",
                requires_attention=True,
            ))
        
        return items
