"""
University Setup & Activation API Routes
Items 28-33: Graduation config, setup checklist, submission, review, activation, school code routing

Routes organized by role:
- Admin routes: POST /api/v1/admin/setup/... (university admin)
- Super admin routes: GET /api/v1/admin/setup/... (super admin only)
- Public routes: GET /api/v1/apply/{school_code}/... (applicants)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from datetime import datetime

from app.dependencies import require_roles, get_current_user
from app.domain.models.user import User

# Import services
from app.application.admin.graduation_configuration import (
    GraduationConfigurationService,
    CreateGraduationConfigRequest,
    GraduationConfigResponse,
)
from app.application.admin.setup_checklist import (
    UniversitySetupChecklistService,
    SetupChecklistResponse,
)
from app.application.admin.setup_submission import (
    UniversitySetupSubmissionService,
    SubmitSetupRequest,
    SubmitSetupResponse,
    UniversityApplicationResponse,
)
from app.application.admin.super_admin_review import (
    SuperAdminReviewService,
    UniversityApprovalRequest,
    UniversityApprovalResponse,
    UniversityReviewSummary,
)
from app.application.admin.university_activation import (
    UniversityActivationService,
    UniversityActivationRequest,
    UniversityActivationResponse,
    ActivationStatusResponse,
)
from app.application.admin.school_code_routing import (
    SchoolCodeResolutionService,
    ResolveSchoolCodeRequest,
    ResolveSchoolCodeResponse,
    SchoolCodeResponse,
)

# ==================== ROUTERS ====================

admin_setup_router = APIRouter(
    prefix="/api/v1/admin/setup",
    tags=["admin-setup"],
)

public_portal_router = APIRouter(
    prefix="/api/v1/apply",
    tags=["public-portal"],
)


# ==================== GRADUATION CONFIGURATION (Item 28) ====================

@admin_setup_router.post(
    "/graduation/configure",
    response_model=GraduationConfigResponse,
    summary="Configure graduation requirements",
    description="Item 28: University admin configures graduation requirements (credits, GPA, clearances)",
)
async def configure_graduation(
    request: CreateGraduationConfigRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["university_admin", "super_admin"])),
):
    """
    Configure graduation requirements for university.
    
    Only university_admin for own tenant or super_admin can configure.
    """
    tenant_id = current_user.tenant_id
    
    service = GraduationConfigurationService()
    config = await service.configure_graduation(
        tenant_id=tenant_id,
        minimum_credits=request.minimum_credits_required,
        minimum_cgpa=request.minimum_cgpa,
        minimum_level_gpa=request.minimum_level_gpa,
        outstanding_fees=request.outstanding_fees_allowed,
        payment_plan_allowed=request.payment_plan_allowed,
        clearance_modules=request.clearance_modules,
        academic_standing=request.academic_standing_required,
        allow_probation=request.allow_graduation_on_probation,
        commencement_required=request.commencement_required_to_graduate,
        configured_by=current_user.email,
    )
    
    return GraduationConfigResponse(
        tenant_id=config.tenant_id,
        minimum_credits_required=config.minimum_credits_required,
        minimum_cgpa=config.minimum_cgpa,
        minimum_level_gpa=config.minimum_level_gpa,
        clearance_modules=[
            {
                "module": c.module_name,
                "description": c.description,
                "is_mandatory": c.is_mandatory,
            }
            for c in config.clearance_modules
        ],
        academic_standing_required=config.academic_standing_required,
        is_configured=config.is_configured,
        configured_at=config.configured_at,
    )


@admin_setup_router.get(
    "/graduation/config",
    response_model=GraduationConfigResponse,
    summary="Get graduation configuration",
)
async def get_graduation_config(
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["university_admin", "super_admin"])),
):
    """Get current graduation configuration."""
    tenant_id = current_user.tenant_id
    
    service = GraduationConfigurationService()
    config = await service.get_configuration(tenant_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Graduation configuration not found",
        )
    
    return GraduationConfigResponse(
        tenant_id=config.tenant_id,
        minimum_credits_required=config.minimum_credits_required,
        minimum_cgpa=config.minimum_cgpa,
        minimum_level_gpa=config.minimum_level_gpa,
        clearance_modules=[
            {
                "module": c.module_name,
                "description": c.description,
                "is_mandatory": c.is_mandatory,
            }
            for c in config.clearance_modules
        ],
        academic_standing_required=config.academic_standing_required,
        is_configured=config.is_configured,
        configured_at=config.configured_at,
    )


# ==================== SETUP CHECKLIST (Item 29) ====================

@admin_setup_router.get(
    "/checklist",
    response_model=SetupChecklistResponse,
    summary="Get setup completeness checklist",
    description="Item 29: Show what's been configured and what still needs setup",
)
async def get_setup_checklist(
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["university_admin", "super_admin"])),
):
    """
    Get checklist of setup items.
    
    Shows completion status of all required and optional configuration items.
    """
    tenant_id = current_user.tenant_id
    
    service = UniversitySetupChecklistService()
    checklist = await service.get_checklist(tenant_id)
    
    return checklist


# ==================== SETUP SUBMISSION (Item 30) ====================

@admin_setup_router.post(
    "/submit",
    response_model=SubmitSetupResponse,
    summary="Submit setup for super admin review",
    description="Item 30: University admin submits setup for super admin approval",
)
async def submit_setup(
    request: SubmitSetupRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["university_admin"])),
):
    """
    Submit university setup for super admin review.
    
    Validates all required items are complete before submission.
    """
    tenant_id = current_user.tenant_id
    
    service = UniversitySetupSubmissionService()
    
    try:
        response = await service.submit_for_review(
            tenant_id=tenant_id,
            admin_email=current_user.email,
            submission_notes=request.submission_notes,
            checklist_status=request.checklist_status,
        )
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@admin_setup_router.get(
    "/submission",
    response_model=UniversityApplicationResponse,
    summary="Get current submission status",
)
async def get_submission(
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["university_admin", "super_admin"])),
):
    """Get current submission and review status."""
    tenant_id = current_user.tenant_id
    
    service = UniversitySetupSubmissionService()
    response = await service.get_submission_for_review(tenant_id)
    
    return response


# ==================== SUPER ADMIN REVIEW (Item 31) ====================

@admin_setup_router.get(
    "/pending",
    response_model=List[UniversityReviewSummary],
    summary="Get pending universities for review",
    description="Item 31: Super admin views list of universities awaiting approval",
)
async def get_pending_universities(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["super_admin"])),
):
    """
    Get universities awaiting super admin review.
    
    Super admin only endpoint.
    """
    service = SuperAdminReviewService()
    universities = await service.get_pending_universities(limit=limit, offset=offset)
    return universities


@admin_setup_router.get(
    "/{tenant_id}/review",
    summary="Get review details for university",
    description="Item 31: Super admin reviews complete configuration",
)
async def get_review_details(
    tenant_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["super_admin"])),
):
    """Get full configuration details for super admin review."""
    
    service = SuperAdminReviewService()
    
    try:
        details = await service.get_review_details(tenant_id)
        return details
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@admin_setup_router.post(
    "/{tenant_id}/approve",
    response_model=UniversityApprovalResponse,
    summary="Approve university setup",
    description="Item 31: Super admin approves, triggering provisioning",
)
async def approve_university(
    tenant_id: str,
    request: UniversityApprovalRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["super_admin"])),
):
    """
    Super admin approves university setup.
    
    Triggers automatic provisioning (Item 32).
    """
    
    if request.decision != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /approve endpoint for approvals",
        )
    
    service = SuperAdminReviewService()
    
    try:
        response = await service.approve_university(
            tenant_id=tenant_id,
            reviewer_email=current_user.email,
            approval_notes=request.approval_notes,
            conditions=request.conditions,
        )
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@admin_setup_router.post(
    "/{tenant_id}/reject",
    response_model=UniversityApprovalResponse,
    summary="Reject university setup",
    description="Item 31: Super admin rejects application",
)
async def reject_university(
    tenant_id: str,
    request: UniversityApprovalRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["super_admin"])),
):
    """Super admin rejects university application."""
    
    service = SuperAdminReviewService()
    
    try:
        response = await service.reject_university(
            tenant_id=tenant_id,
            reviewer_email=current_user.email,
            rejection_reason=request.rejection_reason or "Not specified",
            rejection_details=request.approval_notes,
        )
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@admin_setup_router.post(
    "/{tenant_id}/request-changes",
    response_model=UniversityApprovalResponse,
    summary="Request changes to setup",
    description="Item 31: Super admin requests changes",
)
async def request_changes(
    tenant_id: str,
    request: UniversityApprovalRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["super_admin"])),
):
    """Super admin requests changes to university setup."""
    
    service = SuperAdminReviewService()
    
    try:
        response = await service.request_changes(
            tenant_id=tenant_id,
            reviewer_email=current_user.email,
            change_requests=request.change_requests or [],
            review_notes=request.approval_notes,
        )
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==================== UNIVERSITY ACTIVATION (Item 32) ====================

@admin_setup_router.post(
    "/activate",
    response_model=UniversityActivationResponse,
    summary="Activate university",
    description="Item 32: Automatically provision and activate university after super admin approval",
)
async def activate_university(
    request: UniversityActivationRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["super_admin"])),
):
    """
    Activate university (automatic after approval or manual trigger).
    
    Handles provisioning:
    - Creates database indices
    - Sets up default admin
    - Initializes configuration
    - Sets up audit logging
    - Optionally creates sample data
    
    Status transitions: APPROVED -> PROVISIONING -> ACTIVE
    """
    tenant_id = current_user.tenant_id
    
    service = UniversityActivationService()
    
    try:
        response = await service.provision_university(
            tenant_id=tenant_id,
            initiated_by=current_user.email,
            include_sample_data=request.activate_sample_data,
        )
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@admin_setup_router.get(
    "/activation-status",
    response_model=ActivationStatusResponse,
    summary="Get activation status",
    description="Item 32: Check provisioning progress",
)
async def get_activation_status(
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["university_admin", "super_admin"])),
):
    """Get current activation and provisioning status."""
    tenant_id = current_user.tenant_id
    
    service = UniversityActivationService()
    
    try:
        status_response = await service.get_activation_status(tenant_id)
        return status_response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==================== SCHOOL CODE ROUTING (Item 33) ====================

@public_portal_router.get(
    "/{school_code}/info",
    response_model=ResolveSchoolCodeResponse,
    summary="Resolve school code to university",
    description="Item 33: Applicant enters school code to access application portal",
)
async def resolve_school_code(school_code: str):
    """
    Resolve school code to university.
    
    Called when applicant visits /apply/{school_code}
    Returns university info and application form details.
    
    Public endpoint - no authentication required.
    """
    service = SchoolCodeResolutionService()
    
    try:
        response = await service.resolve_school_code(school_code)
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@admin_setup_router.post(
    "/school-code/register",
    response_model=SchoolCodeResponse,
    summary="Register school code",
    description="Item 33: Register school code during university activation",
)
async def register_school_code(
    school_code: str,
    custom_domain: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["university_admin", "super_admin"])),
):
    """
    Register school code for university.
    
    Called during activation to enable /apply/{code} routing.
    """
    tenant_id = current_user.tenant_id
    
    service = SchoolCodeResolutionService()
    
    try:
        # Get university name from application document
        from app.application.admin.setup_submission import UniversityApplicationDocument
        
        app = await UniversityApplicationDocument.find_one(
            UniversityApplicationDocument.tenant_id == tenant_id
        )
        if not app:
            raise ValueError("University not found")
        
        response = await service.register_school_code(
            tenant_id=tenant_id,
            school_code=school_code,
            university_name=app.name,
            custom_domain=custom_domain,
        )
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@admin_setup_router.post(
    "/school-code/{school_code}/enable",
    response_model=SchoolCodeResponse,
    summary="Enable applications for school code",
)
async def enable_applications(
    school_code: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["university_admin", "super_admin"])),
):
    """Enable application acceptance for school code."""
    
    service = SchoolCodeResolutionService()
    
    try:
        response = await service.enable_applications(school_code)
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@admin_setup_router.post(
    "/school-code/{school_code}/disable",
    response_model=SchoolCodeResponse,
    summary="Disable applications for school code",
)
async def disable_applications(
    school_code: str,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    _=Depends(require_roles(["university_admin", "super_admin"])),
):
    """Disable application acceptance for school code."""
    
    service = SchoolCodeResolutionService()
    
    try:
        response = await service.disable_applications(school_code, reason)
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@admin_setup_router.get(
    "/school-code/{school_code}",
    response_model=SchoolCodeResponse,
    summary="Get school code details",
)
async def get_school_code(
    school_code: str,
):
    """Get school code details (public endpoint)."""
    
    service = SchoolCodeResolutionService()
    
    try:
        response = await service.get_school_code(school_code)
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==================== ROUTER EXPORTS ====================

def get_setup_routers() -> List[APIRouter]:
    """Get all setup and activation routers."""
    return [admin_setup_router, public_portal_router]
