"""
Admissions Workflow API Routes
Items 35-40: WASSCE verification, application states, admissions officer endpoints

Endpoints cover:
- WASSCE verification workflow (Items 35-37)
- Application state transitions (Item 39)
- Admissions officer dashboard & decision-making (Item 40)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.presentation.dependencies import get_current_user, require_roles
from app.presentation.schemas.responses import StandardResponse

from app.application.admissions.wassce_verification import (
    WAESSSEVerificationService,
    VerificationRequest,
    VerificationResponse,
)

from app.application.admissions.application_state_machine import (
    ApplicationStateService,
    StatusTransitionRequest,
    StatusTransitionResponse,
    ApplicationStatus,
)

from app.application.admissions.admissions_officer_service import (
    AdmissionsOfficerService,
    AdmissionsDecision,
    AdmissionsDecisionRequest,
)

router = APIRouter(prefix="/api/v1/admissions", tags=["Admissions Workflow"])


# ==================== ITEM 35-37: WASSCE VERIFICATION ====================

@router.post("/wassce/submit", response_model=StandardResponse)
async def submit_wassce(
    application_id: str,
    examination_type: str,
    examination_year: int,
    index_number: str,
    candidate_name: str,
    subjects: List[dict],
    result_document_path: Optional[str] = None,
    current_user = Depends(get_current_user),
):
    """
    Applicant submits WASSCE results.
    
    Items 35-37: Creates verification record in PENDING_VERIFICATION status.
    Officer will review and verify manually.
    
    Args:
        application_id: Application ID
        examination_type: "WASSCE", "SSSCE", etc.
        examination_year: 2025, 2024
        index_number: WAEC index number
        candidate_name: Name on result
        subjects: List of {subject, grade}
        result_document_path: Path to uploaded PDF
    """
    try:
        service = WAESSSEVerificationService()
        record = await service.submit_wassce(
            application_id=application_id,
            applicant_id=current_user.id,
            tenant_id=current_user.tenant_id,
            examination_type=examination_type,
            examination_year=examination_year,
            index_number=index_number,
            candidate_name=candidate_name,
            subjects=subjects,
            result_document_path=result_document_path,
        )
        
        return StandardResponse(
            status="success",
            message="WASSCE results submitted for verification",
            data={
                "application_id": application_id,
                "verification_status": "pending_verification",
                "submitted_at": record.submitted_at,
                "subjects_count": len(subjects),
                "next_steps": ["Officer will review your WASSCE results", "You will be notified once verified"],
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/wassce/pending", response_model=StandardResponse)
async def get_pending_wassce_verifications(
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["admissions_officer", "super_admin"])),
):
    """
    Get applications awaiting WASSCE verification.
    
    Items 35-37: Officer queue of pending verifications.
    """
    try:
        service = WAESSSEVerificationService()
        pending = await service.get_pending_verifications(
            tenant_id=current_user.tenant_id,
            limit=50,
        )
        
        return StandardResponse(
            status="success",
            message=f"{len(pending)} applications awaiting WASSCE verification",
            data={
                "count": len(pending),
                "pending_applications": [
                    {
                        "application_id": p.application_id,
                        "applicant_id": p.applicant_id,
                        "submitted_at": p.submitted_at,
                        "examination_year": p.submitted_wassce.examination_year,
                        "index_number": p.submitted_wassce.index_number,
                        "candidate_name": p.submitted_wassce.candidate_name,
                        "subjects_count": len(p.submitted_wassce.subjects),
                        "result_document": p.submitted_wassce.result_document_path,
                    }
                    for p in pending
                ]
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/wassce/verify/{application_id}", response_model=StandardResponse)
async def verify_wassce(
    application_id: str,
    verified_subjects: List[str],
    rejected_subjects: Optional[List[str]] = None,
    inconsistencies: Optional[List[str]] = None,
    verification_notes: Optional[str] = None,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["admissions_officer", "super_admin"])),
):
    """
    Officer verifies WASSCE results.
    
    Items 35-37: Mark subjects as verified, status → VERIFIED.
    """
    try:
        service = WAESSSEVerificationService()
        response = await service.verify_wassce(
            application_id=application_id,
            verified_by=current_user.email,
            subjects_verified=verified_subjects,
            subjects_rejected=rejected_subjects or [],
            inconsistencies=inconsistencies or [],
            verification_notes=verification_notes,
        )
        
        return StandardResponse(
            status="success",
            message="WASSCE results verified",
            data=response.dict()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/wassce/reject/{application_id}", response_model=StandardResponse)
async def reject_wassce(
    application_id: str,
    rejection_reason: str,
    rejected_subjects: List[str],
    rejection_notes: Optional[str] = None,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["admissions_officer", "super_admin"])),
):
    """
    Officer rejects WASSCE results.
    
    Items 35-37: Status → REJECTED. Application cannot proceed.
    """
    try:
        service = WAESSSEVerificationService()
        response = await service.reject_wassce(
            application_id=application_id,
            rejected_by=current_user.email,
            rejection_reason=rejection_reason,
            subjects_rejected=rejected_subjects,
            rejection_notes=rejection_notes,
        )
        
        return StandardResponse(
            status="success",
            message="WASSCE results rejected",
            data=response.dict()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/wassce/request-correction/{application_id}", response_model=StandardResponse)
async def request_wassce_correction(
    application_id: str,
    subjects_requiring_correction: List[str],
    correction_deadline_days: int = 7,
    correction_notes: Optional[str] = None,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["admissions_officer", "super_admin"])),
):
    """
    Officer requests applicant to correct WASSCE data.
    
    Items 35-37: Status → REQUIRES_CORRECTION. Applicant has deadline.
    """
    try:
        service = WAESSSEVerificationService()
        response = await service.request_correction(
            application_id=application_id,
            officer_email=current_user.email,
            subjects_requiring_correction=subjects_requiring_correction,
            correction_deadline_days=correction_deadline_days,
            correction_notes=correction_notes,
        )
        
        return StandardResponse(
            status="success",
            message="Correction request sent to applicant",
            data=response.dict()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ==================== ITEM 39: APPLICATION STATE TRANSITIONS ====================

@router.post("/application/{application_id}/transition", response_model=StandardResponse)
async def transition_application_status(
    application_id: str,
    new_status: str,
    reason: Optional[str] = None,
    notes: Optional[str] = None,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["admissions_officer", "registrar", "super_admin"])),
):
    """
    Transition application to new status.
    
    Item 39: Moves through workflow (DRAFT → SUBMITTED → ... → ENROLLED).
    Validates transitions, records audit trail.
    """
    try:
        service = ApplicationStateService()
        response = await service.transition_status(
            application_id=application_id,
            new_status=new_status,
            changed_by=current_user.email,
            reason=reason,
            notes=notes,
        )
        
        return StandardResponse(
            status="success",
            message=f"Application transitioned to {new_status}",
            data=response.dict()
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


@router.get("/application/{application_id}/status", response_model=StandardResponse)
async def get_application_status(
    application_id: str,
    current_user = Depends(get_current_user),
):
    """
    Get current status of application.
    
    Item 39: Returns current state and full transition history.
    """
    try:
        service = ApplicationStateService()
        state = await service.get_application_state(application_id)
        
        if not state:
            raise ValueError("Application not found")
        
        return StandardResponse(
            status="success",
            data={
                "application_id": state.application_id,
                "current_status": state.current_status,
                "status_since": state.status_since,
                "status_history": [t.dict() for t in state.status_history],
                "submitted_at": state.submitted_at,
                "payment_verified_at": state.payment_verified_at,
                "wassce_verified_at": state.wassce_verified_at,
                "eligibility_checked_at": state.eligibility_checked_at,
                "offer_accepted_at": state.offer_accepted_at,
                "enrolled_at": state.enrolled_at,
                "admission_decision": state.admission_decision,
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/applications-by-status/{status}", response_model=StandardResponse)
async def get_applications_by_status(
    status: str,
    limit: int = 20,
    offset: int = 0,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["admissions_officer", "registrar", "super_admin"])),
):
    """
    Get all applications in specific status.
    
    Item 39: Filter applications by workflow status.
    """
    try:
        service = ApplicationStateService()
        applications = await service.get_applications_by_status(
            tenant_id=current_user.tenant_id,
            status=status,
            limit=limit,
            offset=offset,
        )
        
        return StandardResponse(
            status="success",
            message=f"{len(applications)} applications in {status} status",
            data={
                "status": status,
                "count": len(applications),
                "applications": [
                    {
                        "application_id": app.application_id,
                        "applicant_id": app.applicant_id,
                        "status_since": app.status_since,
                        "submitted_at": app.submitted_at,
                    }
                    for app in applications
                ]
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== ITEM 40: ADMISSIONS OFFICER DASHBOARD ====================

@router.get("/officer/dashboard", response_model=StandardResponse)
async def get_admissions_officer_dashboard(
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["admissions_officer"])),
):
    """
    Get admissions officer dashboard.
    
    Item 40: Shows metrics, pending applications queue, applications by status.
    """
    try:
        service = AdmissionsOfficerService()
        dashboard = await service.get_dashboard_data(
            tenant_id=current_user.tenant_id,
            officer_id=current_user.id,
        )
        
        return StandardResponse(
            status="success",
            message="Admissions dashboard data retrieved",
            data={
                "pending_applications": dashboard.pending_applications,
                "awaiting_wassce_verification": dashboard.applications_awaiting_wassce_verification,
                "awaiting_eligibility_check": dashboard.applications_awaiting_eligibility_check,
                "awaiting_review": dashboard.applications_awaiting_review,
                "decisions_made_today": dashboard.decisions_made_today,
                "offers_sent_this_month": dashboard.offers_sent_this_month,
                "application_queue": [q.dict() for q in dashboard.application_queue],
                "statistics": dashboard.application_stats,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/application/{application_id}/review", response_model=StandardResponse)
async def get_application_for_review(
    application_id: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["admissions_officer"])),
):
    """
    Get complete application for officer review.
    
    Item 40: Fetches all related data (form, documents, WASSCE, eligibility, history).
    """
    try:
        service = AdmissionsOfficerService()
        app_data = await service.get_application_for_review(
            application_id=application_id,
            tenant_id=current_user.tenant_id,
        )
        
        return StandardResponse(
            status="success",
            message="Application details retrieved",
            data=app_data
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/application/{application_id}/decision", response_model=StandardResponse)
async def make_admission_decision(
    application_id: str,
    decision: str,  # "admitted", "rejected", "waitlisted", "conditionally_admitted"
    decision_notes: str,
    rejection_reason: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    waitlist_position: Optional[int] = None,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["admissions_officer", "super_admin"])),
):
    """
    Make final admission decision.
    
    Item 40: Admits, rejects, waitlists, or conditionally admits applicant.
    Triggers offer generation if admitted.
    """
    try:
        service = AdmissionsOfficerService()
        result = await service.make_admission_decision(
            tenant_id=current_user.tenant_id,
            application_id=application_id,
            decision=AdmissionsDecision(decision),
            officer_email=current_user.email,
            decision_notes=decision_notes,
            rejection_reason=rejection_reason,
            conditions=conditions,
            waitlist_position=waitlist_position,
        )
        
        return StandardResponse(
            status="success",
            message=f"Admission decision recorded: {decision}",
            data=result
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


@router.get("/applications/requiring-decision", response_model=StandardResponse)
async def get_applications_requiring_decision(
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["admissions_officer"])),
):
    """
    Get applications ready for final admission decision.
    
    Item 40: Queue of applications that passed all review stages.
    """
    try:
        service = AdmissionsOfficerService()
        ready_for_decision = await service.get_applications_requiring_decision(
            tenant_id=current_user.tenant_id,
        )
        
        return StandardResponse(
            status="success",
            message=f"{len(ready_for_decision)} applications ready for decision",
            data={
                "count": len(ready_for_decision),
                "applications": [q.dict() for q in ready_for_decision]
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
