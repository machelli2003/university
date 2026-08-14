"""
University Setup & Activation API Routes
Items 28-33: Admin setup workflow through super admin approval to activation

Endpoints:
- Item 28: Graduation configuration
- Item 29: Setup checklist
- Item 30: Setup submission
- Item 31: Super admin review
- Item 32: University activation
- Item 33: School code routing
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.presentation.dependencies import get_current_user, require_roles
from app.presentation.schemas.responses import StandardResponse

# Item 28
from app.application.admin.graduation_configuration import (
    GraduationConfigurationService,
    CreateGraduationConfigRequest,
    GraduationConfigResponse,
)

# Item 29
from app.application.admin.setup_checklist import (
    UniversitySetupChecklistService,
    SetupChecklistResponse,
)

# Item 30
from app.application.admin.setup_submission import (
    UniversitySetupSubmissionService,
    SubmitSetupRequest,
    SubmitSetupResponse,
    UniversityApplicationResponse,
)

# Item 31
from app.application.admin.super_admin_review import (
    SuperAdminReviewService,
    UniversityReviewSummary,
    UniversityApprovalRequest,
    UniversityApprovalResponse,
)

# Item 32
from app.application.admin.university_activation import (
    UniversityActivationService,
    UniversityActivationRequest,
    UniversityActivationResponse,
    ActivationStatusResponse,
)

# Item 33
from app.application.admin.school_code_routing import (
    SchoolCodeResolutionService,
    ResolveSchoolCodeResponse,
    SchoolCodeResponse,
)

router = APIRouter(prefix="/api/v1/admin/setup", tags=["Setup & Activation"])


# ==================== ITEM 28: GRADUATION CONFIGURATION ====================

@router.post("/graduation/configure", response_model=StandardResponse)
async def configure_graduation(
    request: CreateGraduationConfigRequest,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["university_admin", "super_admin"])),
):
    """
    Configure graduation requirements for university.
    
    Item 28: Set minimum credits, GPA, clearance requirements.
    """
    try:
        service = GraduationConfigurationService()
        config = await service.configure_graduation(
            tenant_id=current_user.tenant_id,
            minimum_credits=request.minimum_credits_required,
            minimum_cgpa=request.minimum_cgpa,
            minimum_level_gpa=request.minimum_level_gpa,
            outstanding_fees=request.outstanding_fees_allowed,
            payment_plan_allowed=request.payment_plan_allowed,
            clearance_modules=request.clearance_modules,
            academic_standing=request.academic_standing_required,
            allow_probation=request.allow_graduation_on_probation,
            commencement_required=False,
            configured_by=current_user.email,
        )
        
        return StandardResponse(
            status="success",
            message="Graduation configuration saved",
            data={
                "minimum_credits": config.minimum_credits_required,
                "minimum_cgpa": config.minimum_cgpa,
                "clearance_modules": len(config.clearance_modules),
                "configured_at": config.configured_at,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/graduation/config", response_model=StandardResponse)
async def get_graduation_config(
    current_user = Depends(get_current_user),
):
    """Get current graduation configuration."""
    try:
        service = GraduationConfigurationService()
        config = await service.get_configuration(current_user.tenant_id)
        
        if not config:
            raise ValueError("Graduation configuration not found")
        
        return StandardResponse(
            status="success",
            data={
                "minimum_credits": config.minimum_credits_required,
                "minimum_cgpa": config.minimum_cgpa,
                "minimum_level_gpa": config.minimum_level_gpa,
                "clearance_modules": [m.dict() for m in config.clearance_modules],
                "is_configured": config.is_configured,
                "configured_at": config.configured_at,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ==================== ITEM 29: SETUP CHECKLIST ====================

@router.get("/checklist", response_model=StandardResponse)
async def get_setup_checklist(
    current_user = Depends(get_current_user),
):
    """
    Get university setup completeness checklist.
    
    Item 29: Shows 14-item checklist with completion status.
    Identifies blocking items preventing submission.
    """
    try:
        service = UniversitySetupChecklistService()
        checklist = await service.get_checklist(current_user.tenant_id)
        
        return StandardResponse(
            status="success",
            message=f"Setup {checklist.completion_percentage}% complete",
            data={
                "total_items": checklist.total_items,
                "completed_items": checklist.completed_items,
                "completion_percentage": checklist.completion_percentage,
                "can_submit": checklist.can_submit,
                "checklist": [
                    {
                        "item_id": item.item_id,
                        "category": item.category,
                        "name": item.name,
                        "description": item.description,
                        "is_completed": item.is_completed,
                        "is_required": item.is_required,
                    }
                    for item in checklist.checklist_items
                ],
                "blocking_items": checklist.blocking_items,
                "warnings": checklist.warnings,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== ITEM 30: SETUP SUBMISSION ====================

@router.post("/submit", response_model=StandardResponse)
async def submit_setup(
    request: SubmitSetupRequest,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["university_admin"])),
):
    """
    University admin submits setup for super admin review.
    
    Item 30: Validates all required items complete, queues for review.
    """
    try:
        service = UniversitySetupSubmissionService()
        response = await service.submit_for_review(
            tenant_id=current_user.tenant_id,
            admin_email=current_user.email,
            submission_notes=request.submission_notes,
            checklist_status=request.checklist_status,
        )
        
        return StandardResponse(
            status="success",
            message=response.message,
            data={
                "tenant_id": response.tenant_id,
                "status": response.status,
                "submitted_at": response.submitted_at,
                "next_steps": response.next_steps,
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/submission/{tenant_id}", response_model=StandardResponse)
async def get_submission_status(
    tenant_id: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["university_admin", "super_admin"])),
):
    """Get current submission status."""
    try:
        service = UniversitySetupSubmissionService()
        response = await service.get_submission_for_review(tenant_id)
        
        return StandardResponse(
            status="success",
            data=response.dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ==================== ITEM 31: SUPER ADMIN REVIEW ====================

@router.get("/pending-review", response_model=StandardResponse)
async def get_pending_applications(
    _ = Depends(require_roles(["super_admin"])),
):
    """
    Get list of universities awaiting super admin review.
    
    Item 31: Super admin dashboard showing pending submissions.
    """
    try:
        service = SuperAdminReviewService()
        pending = await service.get_pending_universities(limit=20, offset=0)
        
        return StandardResponse(
            status="success",
            message=f"{len(pending)} universities awaiting review",
            data={
                "count": len(pending),
                "applications": [app.dict() for app in pending],
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/review/{tenant_id}", response_model=StandardResponse)
async def start_review(
    tenant_id: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["super_admin"])),
):
    """
    Get review details for specific university application.
    
    Item 31: Super admin starts reviewing. Returns inspection checklist template.
    """
    try:
        service = SuperAdminReviewService()
        review_details = await service.start_review(
            tenant_id=tenant_id,
            reviewer_email=current_user.email,
        )
        
        return StandardResponse(
            status="success",
            message="Review started",
            data=review_details
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/review/{tenant_id}/approve", response_model=StandardResponse)
async def approve_application(
    tenant_id: str,
    approval_notes: Optional[str] = None,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["super_admin"])),
):
    """
    Super admin approves university setup.
    
    Item 31: Status -> APPROVED, triggers provisioning (Item 32).
    """
    try:
        service = SuperAdminReviewService()
        response = await service.approve_university(
            tenant_id=tenant_id,
            reviewer_email=current_user.email,
            approval_notes=approval_notes,
        )
        
        return StandardResponse(
            status="success",
            message=response.message,
            data={
                "tenant_id": response.tenant_id,
                "status": response.status,
                "decision": response.decision,
                "next_steps": response.next_steps,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/review/{tenant_id}/reject", response_model=StandardResponse)
async def reject_application(
    tenant_id: str,
    rejection_reason: str,
    rejection_details: Optional[str] = None,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["super_admin"])),
):
    """
    Super admin rejects university setup.
    
    Item 31: Status -> REJECTED.
    """
    try:
        service = SuperAdminReviewService()
        response = await service.reject_university(
            tenant_id=tenant_id,
            reviewer_email=current_user.email,
            rejection_reason=rejection_reason,
            rejection_details=rejection_details,
        )
        
        return StandardResponse(
            status="success",
            message=response.message,
            data={
                "tenant_id": response.tenant_id,
                "status": response.status,
                "decision": response.decision,
                "next_steps": response.next_steps,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/review/{tenant_id}/request-changes", response_model=StandardResponse)
async def request_changes(
    tenant_id: str,
    change_requests: List[str],
    review_notes: Optional[str] = None,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["super_admin"])),
):
    """
    Super admin requests changes to setup.
    
    Item 31: Status -> CHANGES_REQUESTED. Admin revises and resubmits.
    """
    try:
        service = SuperAdminReviewService()
        response = await service.request_changes(
            tenant_id=tenant_id,
            reviewer_email=current_user.email,
            change_requests=change_requests,
            review_notes=review_notes,
        )
        
        return StandardResponse(
            status="success",
            message=response.message,
            data={
                "tenant_id": response.tenant_id,
                "status": response.status,
                "decision": response.decision,
                "change_requests": response.change_requests,
                "next_steps": response.next_steps,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== ITEM 32: UNIVERSITY ACTIVATION ====================

@router.post("/activate", response_model=StandardResponse)
async def activate_university(
    tenant_id: Optional[str] = None,
    include_sample_data: bool = False,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["super_admin", "university_admin"])),
):
    """
    Activate approved university.
    
    Item 32: Status progression APPROVED -> PROVISIONING -> ACTIVE.
    Provisions database, admin account, configurations.
    """
    try:
        service = UniversityActivationService()
        response = await service.provision_university(
            tenant_id=tenant_id or current_user.tenant_id,
            initiated_by=current_user.email,
            include_sample_data=include_sample_data,
        )
        
        return StandardResponse(
            status="success",
            message=response.message,
            data={
                "tenant_id": response.tenant_id,
                "status": response.status,
                "activated_at": response.activated_at,
                "admin_dashboard_url": response.admin_dashboard_url,
                "support_contact": response.support_contact,
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/activation-status/{tenant_id}", response_model=StandardResponse)
async def get_activation_status(
    tenant_id: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["super_admin", "university_admin"])),
):
    """
    Get current activation status.
    
    Item 32: Shows provisioning progress and completion.
    """
    try:
        # TODO: Implement status retrieval
        return StandardResponse(
            status="success",
            message="Status retrieved",
            data={
                "tenant_id": tenant_id,
                "status": "active",
                "completion_percentage": 100,
                "checklist": [],
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== ITEM 33: SCHOOL CODE ROUTING ====================

@router.post("/school-code/register", response_model=StandardResponse)
async def register_school_code(
    school_code: str,
    custom_domain: Optional[str] = None,
    logo_url: Optional[str] = None,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["super_admin"])),
):
    """
    Register school code for university.
    
    Item 33: Called during activation. Enables /apply/{school_code} routing.
    """
    try:
        service = SchoolCodeResolutionService()
        response = await service.register_school_code(
            tenant_id=current_user.tenant_id,
            school_code=school_code,
            university_name="University Name",  # TODO: Get from UniversityApplicationDocument
            custom_domain=custom_domain,
            logo_url=logo_url,
        )
        
        return StandardResponse(
            status="success",
            message=f"School code '{response.school_code}' registered",
            data=response.dict()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/apply/{school_code}", response_model=StandardResponse)
async def resolve_school_code(
    school_code: str,
):
    """
    Resolve school code to university tenant.
    
    Item 33: PUBLIC ENDPOINT - No auth required.
    Called when applicant visits /apply/{school_code}
    Returns university-specific application form.
    """
    try:
        service = SchoolCodeResolutionService()
        response = await service.resolve_school_code(school_code)
        
        return StandardResponse(
            status="success",
            message="Application portal found",
            data=response.dict()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/school-code/{school_code}/enable", response_model=StandardResponse)
async def enable_applications(
    school_code: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["university_admin", "super_admin"])),
):
    """
    Enable application acceptance for school code.
    
    Item 33: University admin opens applications.
    """
    try:
        service = SchoolCodeResolutionService()
        response = await service.enable_applications(school_code)
        
        return StandardResponse(
            status="success",
            message=f"Applications enabled for {school_code}",
            data=response.dict()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/school-code/{school_code}/disable", response_model=StandardResponse)
async def disable_applications(
    school_code: str,
    reason: Optional[str] = None,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["university_admin", "super_admin"])),
):
    """
    Disable application acceptance for school code.
    
    Item 33: University admin closes applications.
    """
    try:
        service = SchoolCodeResolutionService()
        response = await service.disable_applications(school_code, reason)
        
        return StandardResponse(
            status="success",
            message=f"Applications disabled for {school_code}",
            data=response.dict()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
