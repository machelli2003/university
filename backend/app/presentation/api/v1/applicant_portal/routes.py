"""
Applicant Portal Routes
Section 33-34: UNIVERSITY APPLICATION URL & APPLICANT PORTAL

Routes for applicant portal accessible via app.universityplatform.com/apply/{school_code}
Tenant resolution via school_code is mandatory.
Applicant can only access their own application.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from app.presentation.api.v1.admissions.schemas import ApplicantResponse
from app.dependencies import (
    get_current_user, get_applicant_repo, get_tenant_repo,
    get_university_application_repo, get_audit_repo, get_user_repo
)
from app.infrastructure.models.user import User
from app.domain.onboarding.tenant_resolution_service import TenantResolutionService


router = APIRouter()


# ==================== SCHEMAS FOR APPLICANT PORTAL ====================

class ApplicantPortalPublicInfoResponse(BaseModel):
    """Public university information shown on applicant portal landing page."""
    display_name: str
    legal_name: str
    school_code: str
    logo_url: Optional[str] = None
    primary_color: str = "#1E40AF"
    secondary_color: str = "#60A5FA"
    website: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class ApplicantPersonalInfoRequest(BaseModel):
    """Update personal information in applicant portal."""
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    nationality: str = "Ghana"


class ApplicantDashboardResponse(BaseModel):
    """Applicant dashboard with application overview."""
    applicant_id: str
    full_name: str
    application_status: str
    overall_progress: int  # 0-100%
    sections_completed: int
    total_sections: int
    current_step: str
    can_submit: bool
    submission_deadline: Optional[str] = None
    has_application: bool


# ==================== DEPENDENCY FOR TENANT RESOLUTION ====================

async def get_tenant_resolution_service(
    tenant_repo=Depends(get_tenant_repo),
    university_application_repo=Depends(get_university_application_repo),
):
    """Get tenant resolution service."""
    return TenantResolutionService(tenant_repo, university_application_repo)


async def require_school_code(school_code: str = Path(..., min_length=2)):
    """Validate and extract school_code from path."""
    return school_code.lower()


# ==================== PUBLIC ENDPOINTS (No Auth Required) ====================

@router.get("/apply/{school_code}", response_model=ApplicantPortalPublicInfoResponse)
async def get_applicant_portal_info(
    school_code: str = Depends(require_school_code),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
):
    """
    Get public university information for applicant portal landing page.
    No authentication required.
    Resolves tenant by school_code.
    
    Returns university branding, contact info for the applicant portal.
    """
    try:
        return await tenant_resolution_service.get_university_info_for_applicant_portal(school_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )


@router.post("/apply/{school_code}/register", response_model=dict)
async def register_applicant(
    school_code: str = Depends(require_school_code),
    request: BaseModel = None,  # Will accept generic registration request
    user_repo=Depends(get_user_repo),
    applicant_repo=Depends(get_applicant_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
    audit_repo=Depends(get_audit_repo),
):
    """
    Register new applicant in the system.
    Creates user account and applicant profile.
    No prior authentication required.
    
    Tenant is resolved via school_code.
    """
    try:
        tenant_info = await tenant_resolution_service.resolve_tenant_by_school_code(school_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    
    # Registration logic would go here
    # For now, return success message
    return {
        "status": "success",
        "message": "Registration initiated",
        "school_code": school_code,
        "tenant_id": tenant_info["tenant_id"],
    }


@router.post("/apply/{school_code}/login", response_model=dict)
async def login_applicant(
    school_code: str = Depends(require_school_code),
    credentials: BaseModel = None,
    tenant_resolution_service=Depends(get_tenant_resolution_service),
):
    """
    Login applicant to access their portal.
    Tenant is resolved via school_code.
    Returns JWT token for authenticated requests.
    """
    try:
        tenant_info = await tenant_resolution_service.resolve_tenant_by_school_code(school_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    
    # Login logic would go here
    # For now, return success message
    return {
        "status": "success",
        "message": "Login successful",
        "school_code": school_code,
        "tenant_id": tenant_info["tenant_id"],
        "token": "jwt_token_would_go_here",
    }


# ==================== AUTHENTICATED APPLICANT ENDPOINTS ====================

@router.get("/apply/{school_code}/dashboard", response_model=ApplicantDashboardResponse)
async def get_applicant_dashboard(
    school_code: str = Depends(require_school_code),
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
):
    """
    Get applicant dashboard with application overview.
    Requires authentication.
    Applicant can only see their own dashboard.
    """
    # Resolve tenant
    try:
        tenant_info = await tenant_resolution_service.resolve_tenant_by_school_code(school_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    
    # Verify user is in this tenant
    if str(current_user.tenant_id) != tenant_info["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this university portal"
        )
    
    # Get applicant record
    applicant = await applicant_repo.find_one({
        "tenant_id": tenant_info["tenant_id"],
        "user_id": str(current_user.id),
    })
    
    if not applicant:
        return ApplicantDashboardResponse(
            applicant_id="",
            full_name=f"{current_user.first_name} {current_user.last_name}",
            application_status="not_started",
            overall_progress=0,
            sections_completed=0,
            total_sections=10,  # Adjust based on form sections
            current_step="personal_information",
            can_submit=False,
            has_application=False,
        )
    
    return ApplicantDashboardResponse(
        applicant_id=str(applicant.id),
        full_name=f"{applicant.first_name} {applicant.last_name}",
        application_status=applicant.status.value,
        overall_progress=50,  # Calculate based on completed sections
        sections_completed=5,  # Calculate based on form
        total_sections=10,
        current_step=applicant.status.value,
        can_submit=applicant.status.value in ["results_uploaded", "results_approved"],
        has_application=True,
    )


@router.put("/apply/{school_code}/personal", response_model=dict)
async def update_applicant_personal_info(
    school_code: str = Depends(require_school_code),
    request: ApplicantPersonalInfoRequest = None,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
    audit_repo=Depends(get_audit_repo),
):
    """
    Update personal information in applicant portal.
    Applicant can only update their own information.
    """
    try:
        tenant_info = await tenant_resolution_service.resolve_tenant_by_school_code(school_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    
    if str(current_user.tenant_id) != tenant_info["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    
    applicant = await applicant_repo.find_one({
        "tenant_id": tenant_info["tenant_id"],
        "user_id": str(current_user.id),
    })
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Update applicant personal information
    if request:
        applicant.first_name = request.first_name
        applicant.last_name = request.last_name
        applicant.phone = request.phone
        applicant.date_of_birth = request.date_of_birth
        applicant.gender = request.gender
        applicant.address = request.address
        applicant.city = request.city
        applicant.region = request.region
        applicant.nationality = request.nationality
        
        applicant = await applicant_repo.update(str(applicant.id), applicant)
        
        await audit_repo.create({
            "tenant_id": tenant_info["tenant_id"],
            "event_type": "applicant_personal_info_updated",
            "entity_type": "applicant",
            "entity_id": str(applicant.id),
            "action": "update_personal_info",
            "performed_by": str(current_user.id),
            "details": {"first_name": applicant.first_name, "last_name": applicant.last_name},
        })
    
    return {
        "status": "success",
        "message": "Personal information updated",
        "applicant_id": str(applicant.id),
    }


@router.get("/apply/{school_code}/application", response_model=ApplicantResponse)
async def get_applicant_application(
    school_code: str = Depends(require_school_code),
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
):
    """
    Get applicant's current application.
    Applicant can only see their own application.
    """
    try:
        tenant_info = await tenant_resolution_service.resolve_tenant_by_school_code(school_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    
    if str(current_user.tenant_id) != tenant_info["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    
    applicant = await applicant_repo.find_one({
        "tenant_id": tenant_info["tenant_id"],
        "user_id": str(current_user.id),
    })
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found. Please create an application first."
        )
    
    return ApplicantResponse(
        id=str(applicant.id),
        first_name=applicant.first_name,
        last_name=applicant.last_name,
        phone=applicant.phone,
        status=applicant.status.value,
        index_number=applicant.index_number,
        exam_year=applicant.exam_year,
        results=applicant.results,
        aggregate=applicant.aggregate,
        is_eligible=applicant.is_eligible,
        merit_score=applicant.merit_score,
        merit_rank=applicant.merit_rank,
        allocated_programme_id=applicant.allocated_programme_id,
        student_id=applicant.student_id,
        created_at=applicant.created_at,
    )


@router.get("/apply/{school_code}/status", response_model=dict)
async def get_application_status(
    school_code: str = Depends(require_school_code),
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
):
    """
    Get application status and progress.
    """
    try:
        tenant_info = await tenant_resolution_service.resolve_tenant_by_school_code(school_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    
    if str(current_user.tenant_id) != tenant_info["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    
    applicant = await applicant_repo.find_one({
        "tenant_id": tenant_info["tenant_id"],
        "user_id": str(current_user.id),
    })
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return {
        "status": applicant.status.value,
        "eligible": applicant.is_eligible,
        "merit_score": applicant.merit_score,
        "merit_rank": applicant.merit_rank,
        "allocated_programme": applicant.allocated_programme_id,
        "offer_status": "accepted" if applicant.offer_accepted else "pending",
        "student_id": applicant.student_id,
        "last_updated": applicant.updated_at.isoformat() if applicant.updated_at else None,
    }


# ==================== WASSCE VERIFICATION ENDPOINTS (Sections 35-37) ====================

class SubmitWASSCEResultsRequest(BaseModel):
    """Applicant submits WASSCE results for verification."""
    examination_type: str  # e.g., "WASSCE"
    examination_year: int
    index_number: str
    subjects: dict  # {"English": "B2", "Mathematics": "A1"}


@router.post("/apply/{school_code}/wassce/submit")
async def submit_wassce_results(
    school_code: str = Depends(require_school_code),
    request: SubmitWASSCEResultsRequest = None,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
    audit_repo=Depends(get_audit_repo),
):
    """
    Applicant submits WASSCE results.
    Section 35: Manual Verification Entry
    
    Applicant provides exam details and grades.
    Results stored with PENDING_VERIFICATION status for manual review.
    """
    try:
        tenant_info = await tenant_resolution_service.resolve_tenant_by_school_code(school_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    
    if str(current_user.tenant_id) != tenant_info["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    
    applicant = await applicant_repo.find_one({
        "user_id": str(current_user.id),
        "tenant_id": tenant_info["tenant_id"],
    })
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    from app.infrastructure.models.applicant import VerificationStatusEnum
    from datetime import datetime
    
    # Update applicant with WASSCE details
    applicant.exam_type = request.examination_type
    applicant.exam_year = request.examination_year
    applicant.index_number = request.index_number
    applicant.results = request.subjects
    applicant.verification_status = VerificationStatusEnum.PENDING_VERIFICATION
    applicant.updated_at = datetime.utcnow()
    
    applicant = await applicant_repo.update(str(applicant.id), applicant)
    
    await audit_repo.create({
        "tenant_id": tenant_info["tenant_id"],
        "event_type": "wassce_results_submitted",
        "entity_type": "applicant",
        "entity_id": str(applicant.id),
        "action": "submit_wassce_results",
        "performed_by": str(current_user.id),
        "details": {
            "exam_type": request.examination_type,
            "exam_year": request.examination_year,
            "index_number": request.index_number,
            "subjects_count": len(request.subjects),
        },
    })
    
    return {
        "status": "success",
        "message": "WASSCE results submitted for verification",
        "applicant_id": str(applicant.id),
        "verification_status": "pending_verification",
    }


@router.get("/apply/{school_code}/wassce/status")
async def get_wassce_verification_status(
    school_code: str = Depends(require_school_code),
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
):
    """
    Get WASSCE verification status and results.
    Shows verification decision if available.
    """
    try:
        tenant_info = await tenant_resolution_service.resolve_tenant_by_school_code(school_code)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    
    if str(current_user.tenant_id) != tenant_info["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    
    applicant = await applicant_repo.find_one({
        "user_id": str(current_user.id),
        "tenant_id": tenant_info["tenant_id"],
    })
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    from app.infrastructure.models.applicant import VerificationStatusEnum
    
    return {
        "applicant_id": str(applicant.id),
        "verification_status": applicant.verification_status.value if applicant.verification_status else VerificationStatusEnum.PENDING_VERIFICATION.value,
        "verified_by": applicant.verified_by,
        "verified_at": applicant.verified_at.isoformat() if applicant.verified_at else None,
        "verification_notes": applicant.verification_notes,
        "exam_type": applicant.exam_type,
        "exam_year": applicant.exam_year,
        "index_number": applicant.index_number,
        "results": applicant.results or {},
    }
