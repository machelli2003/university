"""
Application State Machine
Item 39: Complete applicant application lifecycle

States:
DRAFT → SUBMITTED → PAYMENT_PENDING → PAYMENT_VERIFIED → DOCUMENT_REVIEW
→ ELIGIBILITY_CHECK → UNDER_REVIEW → DEPARTMENT_REVIEW → FACULTY_REVIEW
→ COMMITTEE_REVIEW → MANUAL_REVIEW → ADMITTED | CONDITIONALLY_ADMITTED
| WAITLISTED | REJECTED → OFFER_ACCEPTED → ENROLLMENT_PENDING → ENROLLED
| WITHDRAWN

Not every university uses every state.
Configuration determines workflow.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ApplicationStatus(str, Enum):
    """Application status in workflow."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_VERIFIED = "payment_verified"
    DOCUMENT_REVIEW = "document_review"
    WASSCE_VERIFICATION = "wassce_verification"
    ELIGIBILITY_CHECK = "eligibility_check"
    UNDER_REVIEW = "under_review"
    DEPARTMENT_REVIEW = "department_review"
    FACULTY_REVIEW = "faculty_review"
    COMMITTEE_REVIEW = "committee_review"
    MANUAL_REVIEW = "manual_review"
    ADMITTED = "admitted"
    CONDITIONALLY_ADMITTED = "conditionally_admitted"
    WAITLISTED = "waitlisted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    OFFER_ACCEPTED = "offer_accepted"
    ENROLLMENT_PENDING = "enrollment_pending"
    ENROLLED = "enrolled"


class ApplicationStatusTransition(BaseModel):
    """Record of status change."""
    from_status: str
    to_status: str
    changed_by: Optional[str] = None  # Officer email or system
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    reason: Optional[str] = None
    notes: Optional[str] = None


class ApplicationWorkflowState(Document):
    """
    Application workflow state tracking.
    
    Maintains current status and complete transition history.
    """
    
    tenant_id: Indexed(str)
    application_id: Indexed(str, unique=True)
    applicant_id: Indexed(str)
    
    # Current state
    current_status: Indexed(str)
    status_since: datetime
    
    # Progression
    status_history: List[ApplicationStatusTransition] = []
    
    # Timestamps for each stage
    submitted_at: Optional[datetime] = None
    payment_verified_at: Optional[datetime] = None
    wassce_verified_at: Optional[datetime] = None
    eligibility_checked_at: Optional[datetime] = None
    offered_at: Optional[datetime] = None
    offer_accepted_at: Optional[datetime] = None
    enrolled_at: Optional[datetime] = None
    
    # Decision information
    admission_decision: Optional[str] = None  # admitted, conditionally_admitted, rejected, waitlisted
    admission_decision_date: Optional[datetime] = None
    admission_decision_by: Optional[str] = None
    
    # Rejection/waitlist details
    rejection_reason: Optional[str] = None
    waitlist_position: Optional[int] = None
    conditional_requirements: List[str] = []  # For conditionally admitted
    
    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "application_workflow_states"
        indexes = [
            [("tenant_id", 1)],
            [("application_id", 1)],
            [("applicant_id", 1)],
            [("current_status", 1)],
            [("status_since", 1)],
        ]


class StatusTransitionRequest(BaseModel):
    """Request to transition application status."""
    application_id: str
    new_status: str
    changed_by: str  # Officer email
    reason: Optional[str] = None
    notes: Optional[str] = None
    
    # Optional data for specific transitions
    rejection_reason: Optional[str] = None
    conditional_requirements: Optional[List[str]] = None


class StatusTransitionResponse(BaseModel):
    """Response from status transition."""
    application_id: str
    old_status: str
    new_status: str
    transitioned_at: datetime
    message: str


# ==================== WORKFLOW DEFINITIONS ====================

WORKFLOW_TEMPLATES = {
    "standard": [
        # Applicant actions
        ApplicationStatus.DRAFT,
        ApplicationStatus.SUBMITTED,
        
        # Payment required
        ApplicationStatus.PAYMENT_PENDING,
        ApplicationStatus.PAYMENT_VERIFIED,
        
        # Documentation
        ApplicationStatus.DOCUMENT_REVIEW,
        ApplicationStatus.WASSCE_VERIFICATION,
        
        # Academic review
        ApplicationStatus.ELIGIBILITY_CHECK,
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.MANUAL_REVIEW,
        
        # Decision
        ApplicationStatus.ADMITTED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WAITLISTED,
        
        # Offer & enrollment
        ApplicationStatus.OFFER_ACCEPTED,
        ApplicationStatus.ENROLLMENT_PENDING,
        ApplicationStatus.ENROLLED,
    ],
    
    "departmental_review": [
        ApplicationStatus.DRAFT,
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.PAYMENT_VERIFIED,
        ApplicationStatus.DOCUMENT_REVIEW,
        ApplicationStatus.WASSCE_VERIFICATION,
        ApplicationStatus.ELIGIBILITY_CHECK,
        
        # Additional department/faculty review
        ApplicationStatus.DEPARTMENT_REVIEW,
        ApplicationStatus.FACULTY_REVIEW,
        ApplicationStatus.COMMITTEE_REVIEW,
        
        ApplicationStatus.ADMITTED,
        ApplicationStatus.CONDITIONALLY_ADMITTED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WAITLISTED,
        ApplicationStatus.OFFER_ACCEPTED,
        ApplicationStatus.ENROLLMENT_PENDING,
        ApplicationStatus.ENROLLED,
    ],
    
    "simple": [
        ApplicationStatus.DRAFT,
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.ADMITTED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.OFFER_ACCEPTED,
        ApplicationStatus.ENROLLED,
    ],
}


# ==================== SERVICE ====================

class ApplicationStateService:
    """Manage application state transitions."""
    
    async def create_application_state(
        self,
        tenant_id: str,
        application_id: str,
        applicant_id: str,
    ) -> ApplicationWorkflowState:
        """
        Initialize application workflow in DRAFT status.
        
        Called when application created.
        """
        
        state = ApplicationWorkflowState(
            tenant_id=tenant_id,
            application_id=application_id,
            applicant_id=applicant_id,
            current_status=ApplicationStatus.DRAFT.value,
            status_since=datetime.utcnow(),
            status_history=[],
        )
        
        await state.insert()
        
        logger.info(f"📝 Application {application_id} created in DRAFT status")
        
        return state
    
    async def get_application_state(
        self,
        application_id: str,
    ) -> Optional[ApplicationWorkflowState]:
        """Get current state of application."""
        
        return await ApplicationWorkflowState.find_one(
            ApplicationWorkflowState.application_id == application_id
        )
    
    async def transition_status(
        self,
        application_id: str,
        new_status: str,
        changed_by: str,
        reason: Optional[str] = None,
        notes: Optional[str] = None,
        rejection_reason: Optional[str] = None,
        conditional_requirements: Optional[List[str]] = None,
    ) -> StatusTransitionResponse:
        """
        Transition application to new status.
        
        Validates transition is allowed.
        Records history.
        Updates timestamps for key milestones.
        
        Args:
            application_id: Application ID
            new_status: Target status
            changed_by: Officer making change
            reason: Reason for transition
            notes: Additional notes
            rejection_reason: If rejecting
            conditional_requirements: If conditionally admitted
        
        Returns:
            StatusTransitionResponse
        
        Raises:
            ValueError: If transition invalid
        """
        
        state = await self.get_application_state(application_id)
        if not state:
            raise ValueError(f"Application not found: {application_id}")
        
        old_status = state.current_status
        
        # Validate transition allowed
        if not self._is_valid_transition(old_status, new_status):
            raise ValueError(
                f"Invalid transition: {old_status} → {new_status}"
            )
        
        # Update state
        state.current_status = new_status
        state.status_since = datetime.utcnow()
        state.updated_at = datetime.utcnow()
        
        # Record transition
        transition = ApplicationStatusTransition(
            from_status=old_status,
            to_status=new_status,
            changed_by=changed_by,
            changed_at=datetime.utcnow(),
            reason=reason,
            notes=notes,
        )
        state.status_history.append(transition)
        
        # Update milestone timestamps
        if new_status == ApplicationStatus.SUBMITTED.value:
            state.submitted_at = datetime.utcnow()
        elif new_status == ApplicationStatus.PAYMENT_VERIFIED.value:
            state.payment_verified_at = datetime.utcnow()
        elif new_status == ApplicationStatus.WASSCE_VERIFICATION.value:
            state.wassce_verified_at = datetime.utcnow()
        elif new_status == ApplicationStatus.ELIGIBILITY_CHECK.value:
            state.eligibility_checked_at = datetime.utcnow()
        elif new_status in [
            ApplicationStatus.ADMITTED.value,
            ApplicationStatus.CONDITIONALLY_ADMITTED.value,
            ApplicationStatus.REJECTED.value,
            ApplicationStatus.WAITLISTED.value,
        ]:
            state.admission_decision = new_status
            state.admission_decision_date = datetime.utcnow()
            state.admission_decision_by = changed_by
            
            if rejection_reason:
                state.rejection_reason = rejection_reason
            if conditional_requirements:
                state.conditional_requirements = conditional_requirements
        elif new_status == ApplicationStatus.OFFER_ACCEPTED.value:
            state.offer_accepted_at = datetime.utcnow()
        elif new_status == ApplicationStatus.ENROLLED.value:
            state.enrolled_at = datetime.utcnow()
        
        await state.save()
        
        logger.info(
            f"🔄 Application {application_id} transitioned: "
            f"{old_status} → {new_status} by {changed_by}"
        )
        
        return StatusTransitionResponse(
            application_id=application_id,
            old_status=old_status,
            new_status=new_status,
            transitioned_at=state.status_since,
            message=f"Application status updated to {new_status}",
        )
    
    def _is_valid_transition(self, from_status: str, to_status: str) -> bool:
        """Check if transition is allowed."""
        
        # Transitions from DRAFT
        if from_status == ApplicationStatus.DRAFT.value:
            return to_status in [
                ApplicationStatus.SUBMITTED.value,
                ApplicationStatus.WITHDRAWN.value,
            ]
        
        # Transitions from SUBMITTED
        if from_status == ApplicationStatus.SUBMITTED.value:
            return to_status in [
                ApplicationStatus.PAYMENT_PENDING.value,
                ApplicationStatus.WITHDRAWN.value,
            ]
        
        # Transitions from PAYMENT_PENDING
        if from_status == ApplicationStatus.PAYMENT_PENDING.value:
            return to_status in [
                ApplicationStatus.PAYMENT_VERIFIED.value,
                ApplicationStatus.WITHDRAWN.value,
            ]
        
        # Transitions from PAYMENT_VERIFIED
        if from_status == ApplicationStatus.PAYMENT_VERIFIED.value:
            return to_status in [
                ApplicationStatus.DOCUMENT_REVIEW.value,
                ApplicationStatus.WASSCE_VERIFICATION.value,
                ApplicationStatus.WITHDRAWN.value,
            ]
        
        # Transitions through review stages
        review_chain = [
            ApplicationStatus.DOCUMENT_REVIEW.value,
            ApplicationStatus.WASSCE_VERIFICATION.value,
            ApplicationStatus.ELIGIBILITY_CHECK.value,
            ApplicationStatus.UNDER_REVIEW.value,
            ApplicationStatus.DEPARTMENT_REVIEW.value,
            ApplicationStatus.FACULTY_REVIEW.value,
            ApplicationStatus.COMMITTEE_REVIEW.value,
            ApplicationStatus.MANUAL_REVIEW.value,
        ]
        
        if from_status in review_chain:
            return to_status in [
                review_chain[review_chain.index(from_status) + 1] if from_status in review_chain and review_chain.index(from_status) + 1 < len(review_chain) else None,
                ApplicationStatus.REJECTED.value,
                ApplicationStatus.WITHDRAWN.value,
                ApplicationStatus.UNDER_REVIEW.value,  # Can loop back
                ApplicationStatus.MANUAL_REVIEW.value,
            ] and to_status is not None
        
        # Transitions from decision states
        if from_status in [
            ApplicationStatus.ADMITTED.value,
            ApplicationStatus.CONDITIONALLY_ADMITTED.value,
        ]:
            return to_status in [
                ApplicationStatus.OFFER_ACCEPTED.value,
                ApplicationStatus.WITHDRAWN.value,
            ]
        
        if from_status == ApplicationStatus.WAITLISTED.value:
            return to_status in [
                ApplicationStatus.ADMITTED.value,  # Promoted from waitlist
                ApplicationStatus.REJECTED.value,
                ApplicationStatus.WITHDRAWN.value,
            ]
        
        if from_status == ApplicationStatus.REJECTED.value:
            return to_status in [
                ApplicationStatus.WITHDRAWN.value,
                # Appeal could reopen but require explicit permission
            ]
        
        # Transitions from OFFER_ACCEPTED
        if from_status == ApplicationStatus.OFFER_ACCEPTED.value:
            return to_status in [
                ApplicationStatus.ENROLLMENT_PENDING.value,
                ApplicationStatus.WITHDRAWN.value,
            ]
        
        # Transitions from ENROLLMENT_PENDING
        if from_status == ApplicationStatus.ENROLLMENT_PENDING.value:
            return to_status in [
                ApplicationStatus.ENROLLED.value,
                ApplicationStatus.WITHDRAWN.value,
            ]
        
        # ENROLLED and WITHDRAWN are terminal states
        if from_status in [
            ApplicationStatus.ENROLLED.value,
            ApplicationStatus.WITHDRAWN.value,
        ]:
            return False
        
        return False
    
    async def get_applications_by_status(
        self,
        tenant_id: str,
        status: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ApplicationWorkflowState]:
        """Get all applications in specific status."""
        
        return await ApplicationWorkflowState.find(
            ApplicationWorkflowState.tenant_id == tenant_id,
            ApplicationWorkflowState.current_status == status,
        ).sort([("status_since", -1)]).skip(offset).limit(limit).to_list()
    
    async def get_status_history(
        self,
        application_id: str,
    ) -> List[ApplicationStatusTransition]:
        """Get complete status change history."""
        
        state = await self.get_application_state(application_id)
        if not state:
            return []
        
        return state.status_history
    
    async def count_by_status(
        self,
        tenant_id: str,
    ) -> Dict[str, int]:
        """Get count of applications in each status."""
        
        counts = {}
        for status in ApplicationStatus:
            count = await ApplicationWorkflowState.find(
                ApplicationWorkflowState.tenant_id == tenant_id,
                ApplicationWorkflowState.current_status == status.value,
            ).count()
            counts[status.value] = count
        
        return counts
