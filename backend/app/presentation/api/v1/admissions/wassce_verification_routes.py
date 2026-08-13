"""
WASSCE Verification Routes
Sections 35-37: WASSCE Manual Verification Workflow

Applicant Portal:
- Submit WASSCE results
- Upload evidence documents
- Track verification status

Admissions Officer Portal:
- View pending verifications
- Verify results manually
- Reject or request corrections
- Record verification decision
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Dict, Optional
from pydantic import BaseModel

from app.dependencies import (
    get_current_user, get_applicant_repo, get_audit_repo, require_roles
)
from app.infrastructure.models.user import User
from app.domain.admissions.result_verification_service import (
    ManualVerificationService, VerificationStatusEnum
)

router = APIRouter()


# ==================== SCHEMAS ====================

class SubmitWASSCEResultsRequest(BaseModel):
    """Applicant submits WASSCE results."""
    examination_type: str  # e.g., "WASSCE"
    examination_year: int  # e.g., 2025
    index_number: str  # Student's exam index number
    subjects: Dict[str, str]  # {"subject_name": "grade"} e.g., {"English": "B2", "Mathematics": "A1"}


class VerifyWASSCEResultsRequest(BaseModel):
    """Officer verifies applicant's WASSCE results."""
    verified: bool  # True = approve, False = reject
    verification_notes: Optional[str] = None


class RequestWASSCECorrectionRequest(BaseModel):
    """Officer requests applicant to correct WASSCE results."""
    reason: str


class WASSCEVerificationStatusResponse(BaseModel):
    """Current WASSCE verification status for applicant."""
    applicant_id: str
    verification_status: str  # PENDING_VERIFICATION, VERIFIED, REJECTED, REQUIRES_CORRECTION
    verified_by: Optional[str] = None
    verified_at: Optional[str] = None
    verification_notes: Optional[str] = None
    exam_type: Optional[str] = None
    exam_year: Optional[int] = None
    index_number: Optional[str] = None
    results: Dict[str, str] = {}


class PendingVerificationListItem(BaseModel):
    """List item for pending WASSCE verifications."""
    applicant_id: str
    first_name: str
    last_name: str
    email: str
    index_number: str
    exam_year: int
    submitted_at: str
    verification_status: str


# ==================== APPLICANT PORTAL ENDPOINTS ====================

@router.post("/apply/{school_code}/wassce/submit")
async def submit_wassce_results(
    school_code: str,
    request: SubmitWASSCEResultsRequest,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    Applicant submits WASSCE results for verification.
    Section 35: WASSCE Manual Entry
    
    Applicant provides:
    - Examination type
    - Examination year
    - Index number
    - Subject grades
    
    Results are stored with PENDING_VERIFICATION status.
    """
    applicant = await applicant_repo.find_one({
        "user_id": str(current_user.id),
        "tenant_id": current_user.tenant_id,
    })
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Update applicant with WASSCE details
    applicant.exam_type = request.examination_type
    applicant.exam_year = request.examination_year
    applicant.index_number = request.index_number
    applicant.results = request.subjects
    applicant.verification_status = VerificationStatusEnum.PENDING_VERIFICATION
    
    applicant = await applicant_repo.update(str(applicant.id), applicant)
    
    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
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
        "verification_status": VerificationStatusEnum.PENDING_VERIFICATION.value,
    }


@router.get("/apply/{school_code}/wassce/status", response_model=WASSCEVerificationStatusResponse)
async def get_wassce_verification_status(
    school_code: str,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
):
    """
    Get current WASSCE verification status for applicant.
    Includes submitted results and verification decision if available.
    """
    applicant = await applicant_repo.find_one({
        "user_id": str(current_user.id),
        "tenant_id": current_user.tenant_id,
    })
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return WASSCEVerificationStatusResponse(
        applicant_id=str(applicant.id),
        verification_status=applicant.verification_status.value if applicant.verification_status else VerificationStatusEnum.PENDING_VERIFICATION.value,
        verified_by=applicant.verified_by,
        verified_at=applicant.verified_at.isoformat() if applicant.verified_at else None,
        verification_notes=applicant.verification_notes,
        exam_type=applicant.exam_type,
        exam_year=applicant.exam_year,
        index_number=applicant.index_number,
        results=applicant.results or {},
    )


# ==================== ADMISSIONS OFFICER ENDPOINTS ====================

@router.get("/admissions/wassce/pending", response_model=list)
async def get_pending_wassce_verifications(
    current_user: User = Depends(require_roles("admissions_officer")),
    applicant_repo=Depends(get_applicant_repo),
):
    """
    Get list of applicants with WASSCE results pending verification.
    Section 36: Admissions Officer Workflow
    """
    pending_applicants = await applicant_repo.find({
        "tenant_id": current_user.tenant_id,
        "verification_status": VerificationStatusEnum.PENDING_VERIFICATION.value,
    })
    
    result = []
    for applicant in pending_applicants:
        result.append(PendingVerificationListItem(
            applicant_id=str(applicant.id),
            first_name=applicant.first_name,
            last_name=applicant.last_name,
            email=getattr(applicant, "email", "N/A"),
            index_number=applicant.index_number or "N/A",
            exam_year=applicant.exam_year or 0,
            submitted_at=applicant.updated_at.isoformat() if applicant.updated_at else "",
            verification_status=applicant.verification_status.value if applicant.verification_status else VerificationStatusEnum.PENDING_VERIFICATION.value,
        ))
    
    return result


@router.get("/admissions/wassce/{applicant_id}/details")
async def get_wassce_verification_details(
    applicant_id: str = Path(...),
    current_user: User = Depends(require_roles("admissions_officer")),
    applicant_repo=Depends(get_applicant_repo),
):
    """
    Get full details of WASSCE results for verification.
    Officer can review submitted evidence and make decision.
    Section 37: Officer Verification UI
    """
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )
    
    # Verify access to this tenant
    if str(applicant.tenant_id) != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    
    return {
        "applicant_id": str(applicant.id),
        "full_name": f"{applicant.first_name} {applicant.last_name}",
        "index_number": applicant.index_number,
        "examination_type": applicant.exam_type,
        "examination_year": applicant.exam_year,
        "submitted_results": applicant.results or {},
        "current_verification_status": applicant.verification_status.value if applicant.verification_status else VerificationStatusEnum.PENDING_VERIFICATION.value,
        "previous_verification_notes": applicant.verification_notes,
        "documents": applicant.documents or [],
    }


@router.post("/admissions/wassce/{applicant_id}/verify")
async def verify_wassce_results(
    applicant_id: str = Path(...),
    request: VerifyWASSCEResultsRequest = None,
    current_user: User = Depends(require_roles("admissions_officer")),
    applicant_repo=Depends(get_applicant_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    Officer verifies WASSCE results.
    Section 36: Manual Verification Workflow
    
    Officer reviews submitted evidence and marks as:
    - VERIFIED: Results accepted
    - REJECTED: Results rejected
    """
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )
    
    if str(applicant.tenant_id) != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    
    verification_service = ManualVerificationService(applicant_repo)
    
    if request.verified:
        result = await verification_service.verify_results(
            applicant_id=applicant_id,
            examination_type=applicant.exam_type,
            examination_year=applicant.exam_year,
            index_number=applicant.index_number,
            subjects=applicant.results,
            verified_by=str(current_user.id),
            verification_notes=request.verification_notes,
        )
        event_type = "wassce_results_verified"
    else:
        result = await verification_service.reject_results(
            applicant_id=applicant_id,
            reason=request.verification_notes or "Results rejected by officer",
            rejected_by=str(current_user.id),
        )
        event_type = "wassce_results_rejected"
    
    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": event_type,
        "entity_type": "applicant",
        "entity_id": applicant_id,
        "action": "verify_wassce_results",
        "performed_by": str(current_user.id),
        "details": {
            "verified": request.verified,
            "notes": request.verification_notes,
        },
    })
    
    return result


@router.post("/admissions/wassce/{applicant_id}/request-correction")
async def request_wassce_correction(
    applicant_id: str = Path(...),
    request: RequestWASSCECorrectionRequest = None,
    current_user: User = Depends(require_roles("admissions_officer")),
    applicant_repo=Depends(get_applicant_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    Officer requests applicant to correct/resubmit WASSCE results.
    Application status changes to REQUIRES_CORRECTION.
    """
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )
    
    if str(applicant.tenant_id) != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    
    verification_service = ManualVerificationService(applicant_repo)
    result = await verification_service.request_correction(
        applicant_id=applicant_id,
        correction_reason=request.reason,
        requested_by=str(current_user.id),
    )
    
    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "wassce_correction_requested",
        "entity_type": "applicant",
        "entity_id": applicant_id,
        "action": "request_wassce_correction",
        "performed_by": str(current_user.id),
        "details": {
            "reason": request.reason,
        },
    })
    
    return result
