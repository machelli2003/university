"""
University Setup Submission
Item 30: Admin submits setup for super admin review

Process:
1. University admin clicks "Submit for Approval"
2. System validates all required items complete
3. Status changes to AWAITING_SUPER_ADMIN_APPROVAL
4. Super admin receives notification
5. Super admin reviews, approves, rejects, or requests changes
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class UniversityApplicationStatus(str, Enum):
    """Status of university application."""
    PENDING = "pending"  # Creating account
    SETUP_IN_PROGRESS = "setup_in_progress"  # Admin setting up
    AWAITING_SUPER_ADMIN_APPROVAL = "awaiting_super_admin_approval"  # Ready for review
    APPROVED = "approved"  # Super admin approved
    PROVISIONING = "provisioning"  # Setting up infrastructure
    ACTIVE = "active"  # Ready for use
    REJECTED = "rejected"  # Super admin rejected
    CHANGES_REQUESTED = "changes_requested"  # Super admin wants changes


class UniversitySetupSubmission(BaseModel):
    """University setup submission to super admin."""
    tenant_id: str
    submitted_by: str  # Admin email
    submitted_at: datetime
    submission_details: Dict[str, Any]
    setup_checklist_status: Dict[str, bool]  # item_id -> completed
    notes_from_admin: Optional[str] = None
    
    # Super admin review
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_status: Optional[str] = None  # approved, rejected, changes_requested
    review_notes: Optional[str] = None
    change_requests: List[str] = []


class UniversityApplicationDocument(Document):
    """
    University application record.
    
    Tracks entire lifecycle of university from registration through activation.
    """
    
    tenant_id: Indexed(str, unique=True)
    
    # Basic Info
    name: str
    code: str
    email: EmailStr
    phone: str
    location: str
    country: str
    
    # Account Admin
    admin_email: EmailStr
    admin_name: str
    admin_phone: str
    
    # Status tracking
    status: UniversityApplicationStatus = UniversityApplicationStatus.PENDING
    
    # Setup Phase
    setup_started_at: Optional[datetime] = None
    setup_completed_at: Optional[datetime] = None
    
    # Submission
    submitted_at: Optional[datetime] = None
    submitted_by: Optional[str] = None
    submission_notes: Optional[str] = None
    setup_checklist_at_submission: Dict[str, bool] = {}
    
    # Super Admin Review
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    change_requests: List[str] = []
    
    # Approval
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approval_terms_accepted: bool = False
    approval_terms_accepted_at: Optional[datetime] = None
    
    # Provisioning
    provisioning_started_at: Optional[datetime] = None
    provisioning_completed_at: Optional[datetime] = None
    provisioning_notes: Optional[str] = None
    
    # Activation
    activated_at: Optional[datetime] = None
    activated_by: Optional[str] = None
    
    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "university_applications"
        indexes = [
            [("tenant_id", 1)],
            [("status", 1)],
            [("submitted_at", 1)],
            [("reviewed_at", 1)],
        ]


# ==================== SCHEMAS ====================

class SubmitSetupRequest(BaseModel):
    """Admin submits setup for review."""
    submission_notes: Optional[str] = None
    checklist_status: Dict[str, bool]  # item_id -> completed


class SubmitSetupResponse(BaseModel):
    """Response after submission."""
    tenant_id: str
    status: str
    submitted_at: datetime
    message: str
    next_steps: List[str]


class UniversityApplicationResponse(BaseModel):
    """Full university application response."""
    tenant_id: str
    name: str
    status: str
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    approved_at: Optional[datetime]
    activated_at: Optional[datetime]
    review_notes: Optional[str]
    change_requests: List[str]
    completion_percentage: int


# ==================== SERVICE ====================

class UniversitySetupSubmissionService:
    """Handle university setup submission."""
    
    async def submit_for_review(
        self,
        tenant_id: str,
        admin_email: str,
        submission_notes: Optional[str] = None,
        checklist_status: Optional[Dict[str, bool]] = None,
    ) -> SubmitSetupResponse:
        """
        Admin submits setup for super admin review.
        
        Validates all required items are complete before submission.
        
        Args:
            tenant_id: University
            admin_email: Admin submitting
            submission_notes: Optional notes
            checklist_status: Completion status of all items
        
        Returns:
            SubmitSetupResponse with status and next steps
        
        Raises:
            ValueError: If required items not complete
        """
        
        # Fetch application
        app = await UniversityApplicationDocument.find_one(
            UniversityApplicationDocument.tenant_id == tenant_id
        )
        if not app:
            raise ValueError(f"University application not found: {tenant_id}")
        
        # Validate required items complete
        if checklist_status:
            required_items = [
                "basic_info", "academic_structure", "programmes",
                "application_forms", "admissions_requirements",
                "grading_system", "graduation_config", "course_catalogue",
                "finance_settings"
            ]
            
            incomplete = [item for item in required_items if not checklist_status.get(item)]
            if incomplete:
                raise ValueError(
                    f"Cannot submit: incomplete items: {', '.join(incomplete)}"
                )
        
        # Update application
        app.status = UniversityApplicationStatus.AWAITING_SUPER_ADMIN_APPROVAL
        app.submitted_at = datetime.utcnow()
        app.submitted_by = admin_email
        app.submission_notes = submission_notes
        app.setup_checklist_at_submission = checklist_status or {}
        app.updated_at = datetime.utcnow()
        
        await app.save()
        
        logger.info(
            f"✅ {app.name} ({tenant_id}) submitted for super admin review "
            f"by {admin_email}"
        )
        
        # TODO: Send notification to super admin
        
        return SubmitSetupResponse(
            tenant_id=tenant_id,
            status=app.status.value,
            submitted_at=app.submitted_at,
            message="Setup submitted successfully. Super admin will review and contact you.",
            next_steps=[
                "Monitor email for super admin feedback",
                "Address any requested changes",
                "Wait for approval notification",
            ],
        )
    
    async def request_changes(
        self,
        tenant_id: str,
        reviewer_email: str,
        change_requests: List[str],
        review_notes: Optional[str] = None,
    ) -> UniversityApplicationResponse:
        """
        Super admin requests changes to setup.
        
        Status reverts to SETUP_IN_PROGRESS.
        """
        
        app = await UniversityApplicationDocument.find_one(
            UniversityApplicationDocument.tenant_id == tenant_id
        )
        if not app:
            raise ValueError(f"University application not found: {tenant_id}")
        
        app.status = UniversityApplicationStatus.CHANGES_REQUESTED
        app.reviewed_at = datetime.utcnow()
        app.reviewed_by = reviewer_email
        app.review_notes = review_notes
        app.change_requests = change_requests
        app.updated_at = datetime.utcnow()
        
        await app.save()
        
        logger.info(
            f"🔄 Super admin {reviewer_email} requested changes for {tenant_id}. "
            f"Changes: {change_requests}"
        )
        
        # TODO: Send notification to university admin with change requests
        
        return UniversityApplicationResponse(
            tenant_id=tenant_id,
            name=app.name,
            status=app.status.value,
            submitted_at=app.submitted_at,
            reviewed_at=app.reviewed_at,
            approved_at=None,
            activated_at=None,
            review_notes=app.review_notes,
            change_requests=app.change_requests,
            completion_percentage=0,  # TODO: Calculate
        )
    
    async def get_submission_for_review(
        self,
        tenant_id: str,
    ) -> UniversityApplicationResponse:
        """Get submission details for super admin review."""
        
        app = await UniversityApplicationDocument.find_one(
            UniversityApplicationDocument.tenant_id == tenant_id
        )
        if not app:
            raise ValueError(f"University application not found: {tenant_id}")
        
        return UniversityApplicationResponse(
            tenant_id=app.tenant_id,
            name=app.name,
            status=app.status.value,
            submitted_at=app.submitted_at,
            reviewed_at=app.reviewed_at,
            approved_at=app.approved_at,
            activated_at=app.activated_at,
            review_notes=app.review_notes,
            change_requests=app.change_requests,
            completion_percentage=int(
                (sum(app.setup_checklist_at_submission.values()) / 
                 len(app.setup_checklist_at_submission) * 100)
                if app.setup_checklist_at_submission else 0
            ),
        )
    
    async def get_application(
        self,
        tenant_id: str,
    ) -> Optional[UniversityApplicationDocument]:
        """Fetch full application document."""
        return await UniversityApplicationDocument.find_one(
            UniversityApplicationDocument.tenant_id == tenant_id
        )
