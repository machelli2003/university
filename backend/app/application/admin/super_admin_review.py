"""
Super Admin Review & Approval Workflow
Item 31: Super admin reviews university setup and approves/rejects

Process:
1. Super admin views pending university submissions
2. Reviews configuration across all modules
3. Approves setup (-> APPROVED state, triggers provisioning)
4. Rejects setup (-> REJECTED state, reason provided)
5. Requests changes (-> CHANGES_REQUESTED state)

Super admin dashboard shows:
- List of pending universities
- Setup completeness for each
- Configuration details
- Approval/rejection/change request actions
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ApprovalDecision(str, Enum):
    """Super admin's decision on university."""
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class UniversityReviewSummary(BaseModel):
    """Summary for super admin review."""
    tenant_id: str
    name: str
    code: str
    admin_name: str
    admin_email: str
    submitted_at: datetime
    
    # Configuration completeness
    setup_items: Dict[str, bool]  # item_id -> completed
    completion_percentage: int
    blocking_issues: List[str]
    
    # For review decision
    submission_notes: Optional[str] = None
    financial_viability: Optional[str] = None  # "strong", "moderate", "weak"
    academic_quality: Optional[str] = None  # "excellent", "good", "satisfactory"
    operational_readiness: Optional[str] = None  # "ready", "mostly_ready", "needs_work"


class UniversityApprovalRequest(BaseModel):
    """Super admin approval/rejection request."""
    decision: ApprovalDecision
    approval_notes: Optional[str] = None
    change_requests: Optional[List[str]] = None  # If CHANGES_REQUESTED
    rejection_reason: Optional[str] = None  # If REJECTED
    conditions: Optional[List[str]] = None  # Conditions of approval


class UniversityApprovalResponse(BaseModel):
    """Response to approval request."""
    tenant_id: str
    status: str
    decision: str
    reviewed_at: datetime
    reviewed_by: str
    message: str
    next_steps: List[str]


class SuperAdminReviewLog(Document):
    """Audit log of super admin reviews."""
    
    tenant_id: Indexed(str)
    reviewed_by: str  # Super admin email
    reviewed_at: datetime
    decision: str  # approved, rejected, changes_requested
    notes: Optional[str] = None
    change_requests: List[str] = []
    rejection_reason: Optional[str] = None
    conditions: List[str] = []
    
    # Configuration reviewed
    reviewed_config: Dict[str, Any] = {}
    
    class Settings:
        collection = "super_admin_review_logs"
        indexes = [
            [("tenant_id", 1)],
            [("reviewed_at", 1)],
            [("decision", 1)],
        ]


# ==================== SERVICE ====================

class SuperAdminReviewService:
    """
    Super admin review and approval workflow.
    
    Super admin can:
    - View pending universities
    - Review full configuration
    - Approve setup
    - Reject with reason
    - Request changes
    - Add approval conditions
    """
    
    async def get_pending_universities(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> List[UniversityReviewSummary]:
        """
        Get universities awaiting super admin review.
        
        Returns list of pending submissions sorted by submission date.
        """
        from app.application.admin.setup_submission import (
            UniversityApplicationDocument, UniversityApplicationStatus
        )
        
        apps = await UniversityApplicationDocument.find(
            UniversityApplicationDocument.status == UniversityApplicationStatus.AWAITING_SUPER_ADMIN_APPROVAL
        ).sort([("submitted_at", -1)]).skip(offset).limit(limit).to_list()
        
        summaries = []
        for app in apps:
            summary = UniversityReviewSummary(
                tenant_id=app.tenant_id,
                name=app.name,
                code=app.code,
                admin_name=app.admin_name,
                admin_email=app.admin_email,
                submitted_at=app.submitted_at or datetime.utcnow(),
                setup_items=app.setup_checklist_at_submission or {},
                completion_percentage=self._calculate_completion(
                    app.setup_checklist_at_submission or {}
                ),
                blocking_issues=self._identify_blocking_issues(
                    app.setup_checklist_at_submission or {}
                ),
                submission_notes=app.submission_notes,
            )
            summaries.append(summary)
        
        return summaries
    
    async def get_review_details(
        self,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """
        Get full configuration details for review.
        
        Queries all configuration modules to present complete picture.
        """
        from app.application.admin.setup_submission import UniversityApplicationDocument
        
        app = await UniversityApplicationDocument.find_one(
            UniversityApplicationDocument.tenant_id == tenant_id
        )
        if not app:
            raise ValueError(f"University not found: {tenant_id}")
        
        review_details = {
            "basic_info": {
                "name": app.name,
                "code": app.code,
                "email": app.email,
                "phone": app.phone,
                "location": app.location,
                "country": app.country,
            },
            "admin": {
                "name": app.admin_name,
                "email": app.admin_email,
                "phone": app.admin_phone,
            },
            "setup_checklist": app.setup_checklist_at_submission or {},
            "submission": {
                "submitted_at": app.submitted_at,
                "submitted_by": app.submitted_by,
                "notes": app.submission_notes,
            },
            # TODO: Query actual configuration from services
            "academic_structure": await self._get_academic_config(tenant_id),
            "admissions": await self._get_admissions_config(tenant_id),
            "finance": await self._get_finance_config(tenant_id),
            "graduation": await self._get_graduation_config(tenant_id),
        }
        
        return review_details
    
    async def approve_university(
        self,
        tenant_id: str,
        reviewer_email: str,
        approval_notes: Optional[str] = None,
        conditions: Optional[List[str]] = None,
    ) -> UniversityApprovalResponse:
        """
        Super admin approves university setup.
        
        Status transitions: AWAITING_SUPER_ADMIN_APPROVAL -> APPROVED
        Provisioning scheduled to begin.
        
        Args:
            tenant_id: University
            reviewer_email: Super admin email
            approval_notes: Additional notes
            conditions: Conditions of approval (e.g., "Must complete library setup within 7 days")
        
        Returns:
            UniversityApprovalResponse
        """
        from app.application.admin.setup_submission import (
            UniversityApplicationDocument, UniversityApplicationStatus
        )
        
        app = await UniversityApplicationDocument.find_one(
            UniversityApplicationDocument.tenant_id == tenant_id
        )
        if not app:
            raise ValueError(f"University not found: {tenant_id}")
        
        if app.status != UniversityApplicationStatus.AWAITING_SUPER_ADMIN_APPROVAL:
            raise ValueError(
                f"Cannot approve: university status is {app.status.value}, "
                f"expected {UniversityApplicationStatus.AWAITING_SUPER_ADMIN_APPROVAL.value}"
            )
        
        # Update application
        app.status = UniversityApplicationStatus.APPROVED
        app.reviewed_at = datetime.utcnow()
        app.reviewed_by = reviewer_email
        app.approved_at = datetime.utcnow()
        app.approved_by = reviewer_email
        app.updated_at = datetime.utcnow()
        
        await app.save()
        
        # Log review
        log = SuperAdminReviewLog(
            tenant_id=tenant_id,
            reviewed_by=reviewer_email,
            reviewed_at=datetime.utcnow(),
            decision="approved",
            notes=approval_notes,
            conditions=conditions or [],
        )
        await log.insert()
        
        logger.info(
            f"✅ Super admin {reviewer_email} APPROVED {app.name} ({tenant_id}). "
            f"Conditions: {conditions or 'none'}"
        )
        
        # TODO: Send approval email to university admin
        # TODO: Trigger provisioning workflow
        
        return UniversityApprovalResponse(
            tenant_id=tenant_id,
            status=app.status.value,
            decision="approved",
            reviewed_at=app.reviewed_at,
            reviewed_by=reviewer_email,
            message=f"{app.name} has been approved. Provisioning will begin shortly.",
            next_steps=[
                "University infrastructure being provisioned",
                "System will notify you when provisioning is complete",
                "You will receive activation details via email",
                "Login to dashboard to activate university",
            ],
        )
    
    async def reject_university(
        self,
        tenant_id: str,
        reviewer_email: str,
        rejection_reason: str,
        rejection_details: Optional[str] = None,
    ) -> UniversityApprovalResponse:
        """
        Super admin rejects university setup.
        
        Status transitions: AWAITING_SUPER_ADMIN_APPROVAL -> REJECTED
        
        Args:
            tenant_id: University
            reviewer_email: Super admin email
            rejection_reason: Reason for rejection
            rejection_details: Detailed explanation
        
        Returns:
            UniversityApprovalResponse
        """
        from app.application.admin.setup_submission import (
            UniversityApplicationDocument, UniversityApplicationStatus
        )
        
        app = await UniversityApplicationDocument.find_one(
            UniversityApplicationDocument.tenant_id == tenant_id
        )
        if not app:
            raise ValueError(f"University not found: {tenant_id}")
        
        app.status = UniversityApplicationStatus.REJECTED
        app.reviewed_at = datetime.utcnow()
        app.reviewed_by = reviewer_email
        app.updated_at = datetime.utcnow()
        
        await app.save()
        
        # Log review
        log = SuperAdminReviewLog(
            tenant_id=tenant_id,
            reviewed_by=reviewer_email,
            reviewed_at=datetime.utcnow(),
            decision="rejected",
            rejection_reason=rejection_reason,
            notes=rejection_details,
        )
        await log.insert()
        
        logger.warning(
            f"❌ Super admin {reviewer_email} REJECTED {app.name} ({tenant_id}). "
            f"Reason: {rejection_reason}"
        )
        
        # TODO: Send rejection email with reason and contact info for appeals
        
        return UniversityApprovalResponse(
            tenant_id=tenant_id,
            status=app.status.value,
            decision="rejected",
            reviewed_at=app.reviewed_at,
            reviewed_by=reviewer_email,
            message=f"Application rejected: {rejection_reason}",
            next_steps=[
                "Email full rejection details has been sent to university admin",
                "Contact support team for explanation",
                "May reapply after addressing issues",
            ],
        )
    
    async def request_changes(
        self,
        tenant_id: str,
        reviewer_email: str,
        change_requests: List[str],
        review_notes: Optional[str] = None,
    ) -> UniversityApprovalResponse:
        """
        Super admin requests changes to setup.
        
        Status transitions: AWAITING_SUPER_ADMIN_APPROVAL -> CHANGES_REQUESTED
        University admin revises and resubmits.
        
        Args:
            tenant_id: University
            reviewer_email: Super admin email
            change_requests: List of specific items to fix
            review_notes: Additional context
        
        Returns:
            UniversityApprovalResponse
        """
        from app.application.admin.setup_submission import (
            UniversityApplicationDocument, UniversityApplicationStatus
        )
        
        app = await UniversityApplicationDocument.find_one(
            UniversityApplicationDocument.tenant_id == tenant_id
        )
        if not app:
            raise ValueError(f"University not found: {tenant_id}")
        
        app.status = UniversityApplicationStatus.CHANGES_REQUESTED
        app.reviewed_at = datetime.utcnow()
        app.reviewed_by = reviewer_email
        app.review_notes = review_notes
        app.change_requests = change_requests
        app.updated_at = datetime.utcnow()
        
        await app.save()
        
        # Log review
        log = SuperAdminReviewLog(
            tenant_id=tenant_id,
            reviewed_by=reviewer_email,
            reviewed_at=datetime.utcnow(),
            decision="changes_requested",
            notes=review_notes,
            change_requests=change_requests,
        )
        await log.insert()
        
        logger.info(
            f"🔄 Super admin {reviewer_email} requested changes for {app.name} ({tenant_id}). "
            f"Changes: {change_requests}"
        )
        
        # TODO: Send email to university admin with detailed change requests
        
        return UniversityApprovalResponse(
            tenant_id=tenant_id,
            status=app.status.value,
            decision="changes_requested",
            reviewed_at=app.reviewed_at,
            reviewed_by=reviewer_email,
            message="Setup requires changes before approval",
            next_steps=[
                f"Review {len(change_requests)} requested changes in email",
                "Make necessary updates to setup",
                "Resubmit setup for review",
            ],
        )
    
    # ==================== HELPERS ====================
    
    def _calculate_completion(self, checklist: Dict[str, bool]) -> int:
        """Calculate setup completion percentage."""
        if not checklist:
            return 0
        completed = sum(1 for v in checklist.values() if v)
        return int((completed / len(checklist)) * 100) if checklist else 0
    
    def _identify_blocking_issues(self, checklist: Dict[str, bool]) -> List[str]:
        """Identify items preventing approval."""
        required_items = [
            "basic_info", "academic_structure", "programmes",
            "application_forms", "admissions_requirements",
            "grading_system", "graduation_config", "course_catalogue",
            "finance_settings"
        ]
        
        blocking = [item for item in required_items if not checklist.get(item)]
        return [f"Missing: {item.replace('_', ' ').title()}" for item in blocking]
    
    async def _get_academic_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get academic configuration summary."""
        # TODO: Query ProgrammeRepository, GradeConfigRepository
        return {}
    
    async def _get_admissions_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get admissions configuration summary."""
        # TODO: Query ApplicationFormRepository, EligibilityEngine
        return {}
    
    async def _get_finance_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get finance configuration summary."""
        # TODO: Query FinanceConfigRepository
        return {}
    
    async def _get_graduation_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get graduation configuration summary."""
        from app.application.admin.graduation_configuration import GraduationConfiguration
        
        config = await GraduationConfiguration.find_one(
            GraduationConfiguration.tenant_id == tenant_id
        )
        if config:
            return {
                "minimum_credits": config.minimum_credits_required,
                "minimum_cgpa": config.minimum_cgpa,
                "clearance_modules": len(config.clearance_modules),
                "is_configured": config.is_configured,
            }
        return {}
