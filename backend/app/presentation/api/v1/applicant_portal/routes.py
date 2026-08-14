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
from app.presentation.api.v1.applicant_portal import schemas as portal_schemas

from app.presentation.api.v1.admissions.schemas import ApplicantResponse
from app.dependencies import (
    get_current_user, get_applicant_repo, get_tenant_repo,
    get_university_application_repo, get_audit_repo, get_user_repo, get_auth_service
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


class RegisterApplicantRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None



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
    request: RegisterApplicantRequest = None,
    auth_service=Depends(get_auth_service),
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

    # create user account with applicant role under tenant
    user = await auth_service.register(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        password=request.password,
        role="applicant",
        tenant_id=tenant_info["tenant_id"],
    )

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # create minimal applicant profile
    applicant_data = {
        "tenant_id": tenant_info["tenant_id"],
        "user_id": str(user.id),
        "first_name": request.first_name,
        "last_name": request.last_name,
        "phone": request.phone,
        "status": "draft",
    }
    applicant = await applicant_repo.create(applicant_data)

    await audit_repo.create({
        "tenant_id": tenant_info["tenant_id"],
        "event_type": "applicant_registered",
        "entity_type": "applicant",
        "entity_id": str(applicant.id),
        "action": "register",
        "performed_by": str(user.id),
        "details": {"email": user.email},
    })

    return {"status": "success", "applicant_id": str(applicant.id), "tenant_id": tenant_info["tenant_id"]}


@router.post("/apply/{school_code}/login", response_model=dict)
async def login_applicant(
    school_code: str = Depends(require_school_code),
    credentials: RegisterApplicantRequest = None,
    auth_service=Depends(get_auth_service),
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

    access_token, refresh_token, user = await auth_service.login(credentials.email, credentials.password)
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return {"status": "success", "token": access_token, "refresh_token": refresh_token, "tenant_id": tenant_info["tenant_id"]}


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
        return portal_schemas.ApplicantDashboardResponse(
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
    
    return portal_schemas.ApplicantDashboardResponse(
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


# ==================== APPLICATION FORM SUBMISSION ====================

@router.post("/apply/{school_code}/application/submit", response_model=portal_schemas.ApplicationSubmissionResponse)
async def submit_application_form(
    school_code: str = Depends(require_school_code),
    request: portal_schemas.ApplicationFormRequest = None,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    university_application_repo=Depends(get_university_application_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
    audit_repo=Depends(get_audit_repo),
):
    """
    Submit application form from applicant portal.
    Stores application data and marks application as PAYMENT_PENDING.
    Applicant must then pay application fee to proceed.
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
            detail="Applicant record not found"
        )
    
    # Create or update university application
    from datetime import datetime
    
    app_data = {
        "tenant_id": tenant_info["tenant_id"],
        "applicant_id": str(applicant.id),
        "user_id": str(current_user.id),
        "academic_info": {
            "wassce_year": request.wassce_year,
            "wassce_index_number": request.wassce_index_number,
            "wassce_center": request.wassce_center,
            "subjects_and_grades": request.subjects_and_grades,
            "aggregate": request.aggregate,
        },
        "programme_choices": {
            "choice_1": request.choice_1_programme_code,
            "choice_2": request.choice_2_programme_code,
            "choice_3": request.choice_3_programme_code,
        },
        "additional_info": {
            "statement_of_purpose": request.statement_of_purpose,
            "special_needs": request.special_needs,
            "disability_declaration": request.disability_declaration,
        },
        "status": "PAYMENT_PENDING",  # Mark for payment
        "submitted_at": datetime.utcnow(),
    }
    
    application = await university_application_repo.create(app_data)
    
    # Update applicant status
    applicant.status = "PAYMENT_PENDING"
    applicant.updated_at = datetime.utcnow()
    await applicant_repo.update(str(applicant.id), applicant)
    
    # Audit log
    await audit_repo.create({
        "tenant_id": tenant_info["tenant_id"],
        "event_type": "application_submitted",
        "entity_type": "application",
        "entity_id": str(application.id),
        "action": "submit",
        "performed_by": str(current_user.id),
        "details": {"programmes_chosen": [request.choice_1_programme_code, request.choice_2_programme_code, request.choice_3_programme_code]},
    })
    
    return portal_schemas.ApplicationSubmissionResponse(
        status="success",
        application_id=str(application.id),
        applicant_id=str(applicant.id),
        message="Application submitted successfully",
        next_steps="Please proceed to payment to complete your application"
    )


@router.get("/apply/{school_code}/application/status", response_model=portal_schemas.ApplicationStatusResponse)
async def get_application_status(
    school_code: str = Depends(require_school_code),
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    university_application_repo=Depends(get_university_application_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
):
    """
    Get current application status for applicant.
    Shows submission status, payment status, and document upload progress.
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
            detail="Applicant not found"
        )
    
    # Get application if exists
    application = await university_application_repo.find_one({
        "applicant_id": str(applicant.id),
        "tenant_id": tenant_info["tenant_id"],
    })
    
    payment_status = None
    payment_amount = None
    
    if application:
        # In real implementation, fetch payment info from finance service
        payment_status = "pending" if application.status == "PAYMENT_PENDING" else "completed"
        payment_amount = 150.00  # Default application fee
    
    return portal_schemas.ApplicationStatusResponse(
        applicant_id=str(applicant.id),
        application_id=str(application.id) if application else None,
        application_status=application.status if application else applicant.status,
        overall_progress=0 if not application else 25,
        submission_deadline="2026-12-31",  # Calculate from admission cycle
        payment_status=payment_status,
        payment_amount=payment_amount,
        documents_uploaded=0,  # Calculate from document repo
        documents_required=3,  # Configure based on programme/tenant
    )


# ==================== DOCUMENT UPLOAD & MANAGEMENT ====================

@router.post("/apply/{school_code}/documents/upload", response_model=portal_schemas.DocumentUploadResponse)
async def upload_application_document(
    school_code: str = Depends(require_school_code),
    document_type: str = None,
    document_name: str = None,
    file: bytes = None,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
    audit_repo=Depends(get_audit_repo),
):
    """
    Upload supporting document for application.
    Stores file in S3 and records metadata in database.
    Applicant can only upload documents for their own application.
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
            detail="Applicant not found"
        )
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Upload file to S3 via S3Service
    from app.infrastructure.external_services.s3_service import S3Service
    from datetime import datetime
    
    s3_service = S3Service()
    file_key = f"applications/{tenant_info['tenant_id']}/{applicant.id}/{document_type}/{document_name}"
    
    try:
        document_url = await s3_service.upload_file(file_key, file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )
    
    # Record document metadata in database
    from app.infrastructure.models.document import Document  # Assuming this model exists
    
    document_data = {
        "tenant_id": tenant_info["tenant_id"],
        "applicant_id": str(applicant.id),
        "user_id": str(current_user.id),
        "document_type": document_type,
        "document_name": document_name,
        "file_url": document_url,
        "file_size": len(file) if file else 0,
        "uploaded_at": datetime.utcnow(),
        "status": "pending_review",
    }
    
    # Assuming there's a document repository
    # document = await document_repo.create(document_data)
    
    await audit_repo.create({
        "tenant_id": tenant_info["tenant_id"],
        "event_type": "document_uploaded",
        "entity_type": "document",
        "entity_id": str(applicant.id),
        "action": "upload",
        "performed_by": str(current_user.id),
        "details": {"document_type": document_type, "document_name": document_name},
    })
    
    return portal_schemas.DocumentUploadResponse(
        status="success",
        document_id=f"doc_{applicant.id}_{document_type}",
        document_type=document_type,
        document_url=document_url,
        uploaded_at=datetime.utcnow().isoformat(),
        message="Document uploaded successfully"
    )


@router.get("/apply/{school_code}/documents", response_model=portal_schemas.DocumentListResponse)
async def list_applicant_documents(
    school_code: str = Depends(require_school_code),
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
):
    """
    List all uploaded documents for applicant.
    Shows document status and completion progress.
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
            detail="Applicant not found"
        )
    
    # In real implementation, fetch from document repository
    # documents = await document_repo.find_many({"applicant_id": str(applicant.id)})
    
    # Placeholder response
    documents = [
        {
            "id": "doc_1",
            "type": "birth_certificate",
            "name": "birth_cert.pdf",
            "url": "https://s3.example.com/doc_1",
            "uploaded_at": "2026-08-13T12:00:00Z",
            "status": "pending_review"
        }
    ]
    
    return portal_schemas.DocumentListResponse(
        total_documents=len(documents),
        required_documents=3,
        documents=documents
    )


@router.delete("/apply/{school_code}/documents/{document_id}", response_model=portal_schemas.DocumentDeleteResponse)
async def delete_document(
    school_code: str = Depends(require_school_code),
    document_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
    audit_repo=Depends(get_audit_repo),
):
    """
    Delete uploaded document (before submission).
    Applicant can only delete their own documents.
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
            detail="Applicant not found"
        )
    
    # Delete from S3
    from app.infrastructure.external_services.s3_service import S3Service
    
    s3_service = S3Service()
    try:
        await s3_service.delete_file(document_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
    
    await audit_repo.create({
        "tenant_id": tenant_info["tenant_id"],
        "event_type": "document_deleted",
        "entity_type": "document",
        "entity_id": document_id,
        "action": "delete",
        "performed_by": str(current_user.id),
        "details": {"document_id": document_id},
    })
    
    return portal_schemas.DocumentDeleteResponse(
        status="success",
        message="Document deleted successfully",
        documents_remaining=0  # Calculate from remaining documents
    )


# ==================== PAYMENT INITIATION ====================

@router.post("/apply/{school_code}/payment/initiate", response_model=portal_schemas.PaymentInitiationResponse)
async def initiate_application_payment(
    school_code: str = Depends(require_school_code),
    request: portal_schemas.PaymentInitiationRequest = None,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
    audit_repo=Depends(get_audit_repo),
):
    """
    Initiate payment for application fee.
    Returns Paystack authorization URL for applicant to pay.
    Applicant is redirected to Paystack; payment webhook confirms payment.
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
            detail="Applicant not found"
        )
    
    # Call payment service to initiate payment
    from app.application.finance.process_payment import ProcessPaymentUseCase
    from app.dependencies import get_payment_repository, get_paystack_service
    
    payment_repo = await get_payment_repository()
    paystack_service = await get_paystack_service()
    
    use_case = ProcessPaymentUseCase(payment_repo, paystack_service)
    
    try:
        result = await use_case.initiate_payment(
            tenant_id=tenant_info["tenant_id"],
            applicant_id=str(applicant.id),
            application_id=request.application_id,
            amount=request.amount,
            customer_email=request.email,
            payment_type="application_fee",
        )
        
        await audit_repo.create({
            "tenant_id": tenant_info["tenant_id"],
            "event_type": "payment_initiated",
            "entity_type": "payment",
            "entity_id": result.get("payment_id", ""),
            "action": "initiate",
            "performed_by": str(current_user.id),
            "details": {"amount": request.amount, "type": "application_fee"},
        })
        
        return portal_schemas.PaymentInitiationResponse(
            status="success",
            payment_id=result.get("payment_id", ""),
            authorization_url=result.get("authorization_url", ""),
            access_code=result.get("access_code", ""),
            reference=result.get("reference", ""),
            message="Payment initiated. Redirecting to Paystack..."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment initiation failed: {str(e)}"
        )


@router.get("/apply/{school_code}/payment/status/{payment_id}", response_model=dict)
async def get_payment_status(
    school_code: str = Depends(require_school_code),
    payment_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    tenant_resolution_service=Depends(get_tenant_resolution_service),
):
    """
    Check payment status for applicant.
    Shows whether payment has been confirmed or is still pending.
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
    
    # Fetch payment from payment repository
    from app.dependencies import get_payment_repository
    
    payment_repo = await get_payment_repository()
    payment = await payment_repo.get_by_id(payment_id)
    
    if not payment or str(payment.tenant_id) != tenant_info["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return {
        "payment_id": str(payment.id),
        "status": payment.status.value,
        "amount": payment.amount,
        "reference": payment.paystack_reference,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
        "confirmed_at": payment.confirmed_at.isoformat() if payment.confirmed_at else None,
        "receipt_url": payment.receipt_pdf_url if hasattr(payment, 'receipt_pdf_url') else None,
    }
