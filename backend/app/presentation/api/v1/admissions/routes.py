from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import logging

logger = logging.getLogger(__name__)
from app.presentation.api.v1.admissions.schemas import (
    CreateApplicantRequest, SubmitApplicationRequest, SubmitResultsRequest,
    WAECVerifyRequest, ApproveResultsRequest, RejectResultsRequest,
    RejectOfferRequest, ApplicantResponse, RankingResultItem,
    AllocationSummaryResponse, ProcessAdmissionsSummaryResponse,
    OverrideRequest, PromoteWaitlistRequest, ProgramCapacityResponse, WaitlistItem
)
from app.application.admissions.apply_for_admission import ApplyForAdmissionUseCase
from app.application.admissions.verify_waec_results import (
    SubmitManualResultsUseCase, ApproveResultsUseCase, GetPendingVerificationsUseCase
)
from app.application.admissions.evaluate_eligibility import EvaluateEligibilityUseCase
from app.application.admissions.rank_applicants import RankApplicantsUseCase
from app.application.admissions.allocate_programmes import AllocateProgrammesUseCase
from app.application.admissions.publish_offers import PublishOffersUseCase
from app.application.admissions.process_admissions import ProcessAdmissionsPipelineUseCase
from app.application.student.create_student_record import CreateStudentRecordUseCase
from app.dependencies import (
    get_current_user, get_applicant_repo, get_applicant_result_repo,
    get_student_repo, get_program_repo, get_eligibility_engine,
    get_ranking_engine, get_allocation_engine, get_manual_results_service,
    get_email_service, get_sms_service, get_user_repo, get_waec_service,
    get_audit_repo, require_roles
)
from app.infrastructure.models.applicant import ApplicationStatusEnum
from app.infrastructure.models.user import User

router = APIRouter()

OFFICER_ROLES = {"admissions_officer", "registrar", "university_admin", "super_admin"}


def _assert_applicant_access(applicant, current_user: User):
    if str(applicant.user_id) == str(current_user.id):
        return

    if current_user.role.value not in OFFICER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this applicant record"
        )

def _to_response(applicant) -> ApplicantResponse:
    return ApplicantResponse(
        id=str(applicant.id), first_name=applicant.first_name, last_name=applicant.last_name,
        phone=applicant.phone, status=applicant.status, index_number=applicant.index_number,
        exam_year=applicant.exam_year, results=applicant.results, aggregate=applicant.aggregate,
        is_eligible=applicant.is_eligible, merit_score=applicant.merit_score,
        merit_rank=applicant.merit_rank, allocated_programme_id=applicant.allocated_programme_id,
        student_id=applicant.student_id,
        created_at=applicant.created_at,
    )

@router.post("/apply", response_model=ApplicantResponse)
async def create_application(
    request: CreateApplicantRequest,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    audit_repo=Depends(get_audit_repo),
):
    use_case = ApplyForAdmissionUseCase(applicant_repo)
    try:
        applicant = await use_case.execute(
            tenant_id=current_user.tenant_id or "default",
            user_id=str(current_user.id),
            **request.dict()
        )
        await audit_repo.create({
            "tenant_id": current_user.tenant_id,
            "event_type": "application_created",
            "entity_type": "applicant",
            "entity_id": str(applicant.id),
            "action": "create_application",
            "performed_by": str(current_user.id),
            "details": {"first_name": applicant.first_name, "last_name": applicant.last_name},
        })
        return _to_response(applicant)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{applicant_id}/submit", response_model=ApplicantResponse)
async def submit_application(
    applicant_id: str,
    request: SubmitApplicationRequest,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    audit_repo=Depends(get_audit_repo),
):
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    _assert_applicant_access(applicant, current_user)

    use_case = ApplyForAdmissionUseCase(applicant_repo)
    applicant = await use_case.submit_application(
        applicant_id=applicant_id,
        index_number=request.index_number,
        exam_year=request.exam_year,
        exam_type=request.exam_type,
        programme_choices=[c.dict() for c in request.programme_choices],
    )
    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "application_submitted",
        "entity_type": "applicant",
        "entity_id": applicant_id,
        "action": "submit_application",
        "performed_by": str(current_user.id),
        "details": {"index_number": request.index_number, "exam_year": request.exam_year},
    })
    return _to_response(applicant)

@router.post("/{applicant_id}/waec/verify")
async def verify_waec(
    applicant_id: str,
    request: WAECVerifyRequest,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    waec_service=Depends(get_waec_service),
):
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    _assert_applicant_access(applicant, current_user)

    if not applicant.index_number or not applicant.exam_year or not applicant.exam_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Applicant must submit an index number, exam year, and exam type first"
        )

    valid, validation_message = await waec_service.validate_exam_credentials(
        applicant.index_number, applicant.exam_year, applicant.exam_type
    )
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation_message)

    verified, details, message = await waec_service.verify_results(
        applicant.index_number,
        applicant.exam_year,
        exam_type=applicant.exam_type,
        pin=request.pin,
    )

    update_data = {"updated_at": datetime.utcnow()}
    if verified:
        update_data["status"] = ApplicationStatusEnum.RESULTS_APPROVED
        if details and isinstance(details, dict):
            if details.get("results"):
                update_data["results"] = details["results"]
            if details.get("aggregate") is not None:
                update_data["aggregate"] = details["aggregate"]
    else:
        if applicant.status == ApplicationStatusEnum.SUBMITTED:
            update_data["status"] = ApplicationStatusEnum.AWAITING_RESULTS
        elif applicant.status == ApplicationStatusEnum.DRAFT:
            update_data["status"] = ApplicationStatusEnum.AWAITING_RESULTS

    await applicant_repo.update(applicant_id, update_data)

    return {"verified": verified, "details": details, "message": message}

@router.post("/{applicant_id}/results/submit", response_model=ApplicantResponse)
async def submit_results(
    applicant_id: str,
    request: SubmitResultsRequest,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    result_repo=Depends(get_applicant_result_repo),
    audit_repo=Depends(get_audit_repo),
    manual_service=Depends(get_manual_results_service),
):
    """Applicant manually submits results (before WAEC API integration)"""
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    _assert_applicant_access(applicant, current_user)

    use_case = SubmitManualResultsUseCase(applicant_repo, result_repo, manual_service)
    applicant = await use_case.execute(
        tenant_id=current_user.tenant_id or "default",
        applicant_id=applicant_id,
        results=request.results,
        uploaded_by=str(current_user.id),
    )
    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "results_submitted",
        "entity_type": "applicant",
        "entity_id": applicant_id,
        "action": "submit_results",
        "performed_by": str(current_user.id),
        "details": {"uploaded_by": str(current_user.id)},
    })
    return _to_response(applicant)

@router.get("/results/pending", response_model=List[ApplicantResponse])
async def get_pending_results(
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
):
    """Admin: Get all applicants awaiting results approval"""
    use_case = GetPendingVerificationsUseCase(applicant_repo)
    applicants = await use_case.execute(current_user.tenant_id or "default")
    return [_to_response(a) for a in applicants]

@router.post("/{applicant_id}/results/approve", response_model=ApplicantResponse)
async def approve_results(
    applicant_id: str,
    request: ApproveResultsRequest,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    result_repo=Depends(get_applicant_result_repo),
    email_service=Depends(get_email_service),
    sms_service=Depends(get_sms_service),
    user_repo=Depends(get_user_repo),
    audit_repo=Depends(get_audit_repo),
):
    """Admin: Approve manually submitted results"""
    use_case = ApproveResultsUseCase(applicant_repo, result_repo)
    try:
        applicant = await use_case.execute(
            applicant_id=applicant_id,
            approved_by=str(current_user.id),
            aggregate=request.aggregate,
        )

        user = await user_repo.get_by_id(applicant.user_id)
        if user and user.email:
            await email_service.send_results_approved(user.email, f"{applicant.first_name} {applicant.last_name}")
        if applicant.phone:
            await sms_service.send_sms(applicant.phone, "Your submitted results have been approved by admissions.")

        await audit_repo.create({
            "tenant_id": current_user.tenant_id,
            "event_type": "results_approved",
            "entity_type": "applicant",
            "entity_id": str(applicant.id),
            "action": "approve_results",
            "performed_by": str(current_user.id),
            "details": {
                "aggregate": applicant.aggregate,
                "status": applicant.status,
            },
        })

        return _to_response(applicant)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{applicant_id}/results/reject", response_model=ApplicantResponse)
async def reject_results(
    applicant_id: str,
    request: RejectResultsRequest,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    result_repo=Depends(get_applicant_result_repo),
    audit_repo=Depends(get_audit_repo),
):
    """Admin: Reject results, applicant must resubmit"""
    use_case = ApproveResultsUseCase(applicant_repo, result_repo)
    applicant = await use_case.reject(
        applicant_id=applicant_id,
        rejected_by=str(current_user.id),
        reason=request.reason,
    )
    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "results_rejected",
        "entity_type": "applicant",
        "entity_id": applicant_id,
        "action": "reject_results",
        "performed_by": str(current_user.id),
        "details": {"reason": request.reason},
    })
    return _to_response(applicant)

@router.post("/{applicant_id}/eligibility/evaluate")
async def evaluate_eligibility(
    applicant_id: str,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    program_repo=Depends(get_program_repo),
    eligibility_engine=Depends(get_eligibility_engine),
):
    use_case = EvaluateEligibilityUseCase(applicant_repo, program_repo, eligibility_engine)
    try:
        return await use_case.execute(applicant_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/eligibility/bulk-evaluate")
async def bulk_evaluate_eligibility(
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    program_repo=Depends(get_program_repo),
    eligibility_engine=Depends(get_eligibility_engine),
):
    use_case = EvaluateEligibilityUseCase(applicant_repo, program_repo, eligibility_engine)
    return await use_case.bulk_evaluate(current_user.tenant_id or "default")

@router.post("/programmes/{programme_id}/rank", response_model=List[RankingResultItem])
async def rank_applicants(
    programme_id: str,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    program_repo=Depends(get_program_repo),
    ranking_engine=Depends(get_ranking_engine),
):
    use_case = RankApplicantsUseCase(applicant_repo, program_repo, ranking_engine)
    try:
        ranked = await use_case.execute(current_user.tenant_id or "default", programme_id)
        return [RankingResultItem(**r) for r in ranked]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/allocate", response_model=AllocationSummaryResponse)
async def allocate_programmes(
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    program_repo=Depends(get_program_repo),
    allocation_engine=Depends(get_allocation_engine),
    audit_repo=Depends(get_audit_repo),
):
    use_case = AllocateProgrammesUseCase(applicant_repo, program_repo, allocation_engine)
    result = await use_case.execute(current_user.tenant_id or "default")
    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "programmes_allocated",
        "entity_type": "allocation",
        "entity_id": None,
        "action": "allocate_programmes",
        "performed_by": str(current_user.id),
        "details": result,
    })
    return AllocationSummaryResponse(**result)

@router.post("/offers/publish")
async def publish_offers(
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    audit_repo=Depends(get_audit_repo),
):
    use_case = PublishOffersUseCase(applicant_repo)
    res = await use_case.execute(current_user.tenant_id or "default")
    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "offers_published",
        "entity_type": "offer",
        "entity_id": None,
        "action": "publish_offers",
        "performed_by": str(current_user.id),
        "details": res,
    })
    return res

@router.post("/process", response_model=ProcessAdmissionsSummaryResponse)
async def process_admissions(
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    program_repo=Depends(get_program_repo),
    eligibility_engine=Depends(get_eligibility_engine),
    ranking_engine=Depends(get_ranking_engine),
    allocation_engine=Depends(get_allocation_engine),
    audit_repo=Depends(get_audit_repo),
):
    use_case = ProcessAdmissionsPipelineUseCase(
        applicant_repo,
        program_repo,
        eligibility_engine,
        ranking_engine,
        allocation_engine,
    )
    return await use_case.execute(current_user.tenant_id or "default")

@router.post("/{applicant_id}/offer/accept", response_model=ApplicantResponse)
async def accept_offer(
    applicant_id: str,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    student_repo=Depends(get_student_repo),
    email_service=Depends(get_email_service),
    sms_service=Depends(get_sms_service),
    user_repo=Depends(get_user_repo),
    audit_repo=Depends(get_audit_repo),
):
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    _assert_applicant_access(applicant, current_user)

    use_case = PublishOffersUseCase(applicant_repo)
    try:
        await use_case.accept_offer(applicant_id)
        applicant = await applicant_repo.get_by_id(applicant_id)

        if not applicant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")

        from app.application.student.create_student_record import CreateStudentRecordUseCase
        if not applicant.student_id:
            create_student_use_case = CreateStudentRecordUseCase(applicant_repo, student_repo)
            await create_student_use_case.execute(applicant_id=applicant_id, tenant_id=current_user.tenant_id or "default")
            applicant = await applicant_repo.get_by_id(applicant_id)

        user = await user_repo.get_by_id(applicant.user_id)
        if user and user.email:
            await email_service.send_admission_offer(user.email, f"{applicant.first_name} {applicant.last_name}", "your selected programme")
        if applicant.phone:
            await sms_service.send_sms(applicant.phone, "Your offer has been accepted and your student record is now active.")

        await audit_repo.create({
            "tenant_id": current_user.tenant_id,
            "event_type": "offer_accepted",
            "entity_type": "applicant",
            "entity_id": str(applicant.id),
            "action": "accept_offer",
            "performed_by": str(current_user.id),
            "details": {
                "student_id": applicant.student_id,
                "status": applicant.status,
            },
        })

        return _to_response(applicant)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{applicant_id}/offer/reject", response_model=ApplicantResponse)
async def reject_offer(
    applicant_id: str,
    request: RejectOfferRequest,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    audit_repo=Depends(get_audit_repo),
):
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    _assert_applicant_access(applicant, current_user)

    use_case = PublishOffersUseCase(applicant_repo)
    try:
        await use_case.reject_offer(applicant_id, reason=request.reason)
        applicant = await applicant_repo.get_by_id(applicant_id)

        await audit_repo.create({
            "tenant_id": current_user.tenant_id,
            "event_type": "offer_rejected",
            "entity_type": "applicant",
            "entity_id": str(applicant.id),
            "action": "reject_offer",
            "performed_by": str(current_user.id),
            "details": {
                "status": applicant.status,
                "reason": request.reason,
            },
        })

        return _to_response(applicant)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{applicant_id}/student/create")
async def create_student_record(
    applicant_id: str,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    student_repo=Depends(get_student_repo),
    audit_repo=Depends(get_audit_repo),
):
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    _assert_applicant_access(applicant, current_user)

    from app.application.student.create_student_record import CreateStudentRecordUseCase
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    _assert_applicant_access(applicant, current_user)

    use_case = CreateStudentRecordUseCase(applicant_repo, student_repo)
    try:
        student = await use_case.execute(applicant_id=applicant_id, tenant_id=current_user.tenant_id or "default")
        await audit_repo.create({
            "tenant_id": current_user.tenant_id,
            "event_type": "student_record_created",
            "entity_type": "student",
            "entity_id": getattr(student, 'id', None),
            "action": "create_student_record",
            "performed_by": str(current_user.id),
            "details": {"applicant_id": applicant_id},
        })
        return student
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== ITEM 61: ACCEPT OFFER & ENROLL ====================

@router.post("/{applicant_id}/offer/accept")
async def accept_offer(
    applicant_id: str,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    student_repo=Depends(get_student_repo),
    user_repo=Depends(get_user_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    Accept admission offer and convert applicant to student.
    Creates student record with generated student ID.
    Applicant can accept their own offer; officers can also process this.
    
    Item 61: Student Lifecycle
    """
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    
    # Check access: applicant or admissions officer
    if str(applicant.user_id) != str(current_user.id):
        if current_user.role.value not in OFFICER_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    from app.application.admissions.accept_offer import AcceptOfferUseCase
    from app.domain.identifiers.identifier_service import IdentifierService
    
    identifier_service = IdentifierService(applicant_repo)  # Simplified; inject properly
    use_case = AcceptOfferUseCase(
        applicant_repo=applicant_repo,
        student_repo=student_repo,
        user_repo=user_repo,
        identifier_service=identifier_service,
        audit_repo=audit_repo,
    )
    
    try:
        result = await use_case.accept_offer(
            applicant_id=applicant_id,
            tenant_id=str(current_user.tenant_id),
            user_id=str(current_user.id),
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{applicant_id}/offer/reject")
async def reject_offer(
    applicant_id: str,
    request: RejectOfferRequest = None,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
    user_repo=Depends(get_user_repo),
    audit_repo=Depends(get_audit_repo),
):
    """Reject admission offer."""
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    
    # Check access
    if str(applicant.user_id) != str(current_user.id):
        if current_user.role.value not in OFFICER_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    from app.application.admissions.accept_offer import AcceptOfferUseCase
    from app.domain.identifiers.identifier_service import IdentifierService
    
    identifier_service = IdentifierService(applicant_repo)
    use_case = AcceptOfferUseCase(
        applicant_repo=applicant_repo,
        student_repo=None,
        user_repo=user_repo,
        identifier_service=identifier_service,
        audit_repo=audit_repo,
    )
    
    try:
        result = await use_case.reject_offer(
            applicant_id=applicant_id,
            tenant_id=str(current_user.tenant_id),
            user_id=str(current_user.id),
            rejection_reason=request.reason if request else None,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{applicant_id}", response_model=ApplicantResponse)
async def get_applicant(
    applicant_id: str,
    current_user: User = Depends(get_current_user),
    applicant_repo=Depends(get_applicant_repo),
):
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    _assert_applicant_access(applicant, current_user)
    return _to_response(applicant)

@router.get("/", response_model=List[ApplicantResponse])
async def list_applicants(
    status_filter: str = None,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
):
    tenant_id = current_user.tenant_id or "default"
    if status_filter:
        applicants = await applicant_repo.get_by_status(tenant_id, status_filter)
    else:
        applicants = await applicant_repo.get_all(tenant_id=tenant_id)
    return [_to_response(a) for a in applicants]


@router.patch("/{applicant_id}/override", response_model=ApplicantResponse)
async def override_applicant(
    applicant_id: str,
    request: OverrideRequest,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    program_repo=Depends(get_program_repo),
    audit_repo=Depends(get_audit_repo),
):
    """Manual override: adjust merit score or eligibility for an applicant"""
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    _assert_applicant_access(applicant, current_user)

    update_data = {"updated_at": datetime.utcnow()}
    if request.merit_score is not None:
        update_data["merit_score"] = request.merit_score
        # invalidate existing rank so that ranking can be recomputed
        update_data["merit_rank"] = None
    if request.is_eligible is not None:
        update_data["is_eligible"] = request.is_eligible
        if request.eligibility_reason is not None:
            update_data["eligibility_reason"] = request.eligibility_reason

    updated = await applicant_repo.update(applicant_id, update_data)
    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "applicant_override",
        "entity_type": "applicant",
        "entity_id": applicant_id,
        "action": "override_applicant",
        "performed_by": str(current_user.id),
        "details": {"update": update_data},
    })

    return _to_response(updated)


@router.post("/{applicant_id}/reopen", response_model=ApplicantResponse)
async def reopen_application(
    applicant_id: str,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    audit_repo=Depends(get_audit_repo),
):
    """Reopen or reset an application that was mistakenly rejected or closed"""
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    _assert_applicant_access(applicant, current_user)

    update_data = {
        "status": ApplicationStatusEnum.SUBMITTED,
        "allocated_programme_id": None,
        "offer_letter_id": None,
        "offer_accepted": False,
        "offer_accepted_at": None,
        "updated_at": datetime.utcnow(),
    }
    updated = await applicant_repo.update(applicant_id, update_data)
    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "application_reopened",
        "entity_type": "applicant",
        "entity_id": applicant_id,
        "action": "reopen_application",
        "performed_by": str(current_user.id),
        "details": update_data,
    })
    return _to_response(updated)


@router.get("/waitlist", response_model=List[WaitlistItem])
async def get_waitlist(
    programme_id: str | None = None,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
):
    """List waitlisted applicants, optionally filtered by programme"""
    tenant_id = current_user.tenant_id or "default"
    query = {"tenant_id": tenant_id, "status": "waitlisted"}
    if programme_id:
        query["programme_choices.programme_id"] = programme_id

    docs = await applicant_repo.model.find(query).sort("merit_rank", 1).to_list(None)
    items = []
    for d in docs:
        items.append(WaitlistItem(
            id=str(d.id), first_name=d.first_name, last_name=d.last_name,
            merit_rank=d.merit_rank, allocated_programme_id=getattr(d, "allocated_programme_id", None),
            created_at=d.created_at
        ))
    return items


@router.post("/waitlist/promote")
async def promote_waitlist(
    request: PromoteWaitlistRequest,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    program_repo=Depends(get_program_repo),
    audit_repo=Depends(get_audit_repo),
):
    """Promote top waitlisted applicants into allocated status for a programme when slots are available"""
    programme_id = request.programme_id
    count = request.count or 1
    tenant_id = current_user.tenant_id or "default"

    programme = await program_repo.get_by_id(programme_id)
    if not programme or programme.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programme not found")

    available = max(0, (programme.capacity_planned or 0) - (programme.capacity_reserved or 0) - (programme.capacity_current or 0))
    promote_count = min(available, count)
    if promote_count <= 0:
        return {"promoted": 0, "available": available}

    # find waitlisted applicants who listed this programme and sort by merit_rank
    docs = await applicant_repo.model.find({
        "tenant_id": tenant_id,
        "status": "waitlisted",
        "programme_choices.programme_id": programme_id
    }).sort("merit_rank", 1).limit(promote_count).to_list(None)

    promoted = 0
    for d in docs:
        await applicant_repo.update(str(d.id), {"allocated_programme_id": programme_id, "status": "allocated", "updated_at": datetime.utcnow()})
        promoted += 1
        await audit_repo.create({
            "tenant_id": tenant_id,
            "event_type": "waitlist_promoted",
            "entity_type": "applicant",
            "entity_id": str(d.id),
            "action": "promote_waitlist",
            "performed_by": str(current_user.id),
            "details": {"programme_id": programme_id},
        })

    # update programme capacity_current
    new_capacity = (programme.capacity_current or 0) + promoted
    await program_repo.update(programme_id, {"capacity_current": new_capacity})

    return {"promoted": promoted, "available": available - promoted}


@router.get("/programmes/{programme_id}/capacity", response_model=ProgramCapacityResponse)
async def get_programme_capacity(
    programme_id: str,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    program_repo=Depends(get_program_repo),
):
    tenant_id = current_user.tenant_id or "default"
    programme = await program_repo.get_by_id(programme_id)
    if not programme or programme.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programme not found")

    planned = programme.capacity_planned or 0
    reserved = programme.capacity_reserved or 0
    current = programme.capacity_current or 0
    available = max(0, planned - reserved - current)

    return ProgramCapacityResponse(
        programme_id=programme_id,
        capacity_planned=planned,
        capacity_current=current,
        capacity_reserved=reserved,
        available=available,
    )


@router.post("/offers/notify/{applicant_id}")
async def notify_offer(
    applicant_id: str,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    program_repo=Depends(get_program_repo),
    email_service=Depends(get_email_service),
    sms_service=Depends(get_sms_service),
    user_repo=Depends(get_user_repo),
    audit_repo=Depends(get_audit_repo),
):
    applicant = await applicant_repo.get_by_id(applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    _assert_applicant_access(applicant, current_user)

    programme = None
    programme_name = ""
    if applicant.allocated_programme_id:
        programme = await program_repo.get_by_id(applicant.allocated_programme_id)
        programme_name = programme.name if programme else "your programme"

    user = await user_repo.get_by_id(applicant.user_id)
    if user and user.email:
        await email_service.send_admission_offer(user.email, f"{applicant.first_name} {applicant.last_name}", programme_name)
    if applicant.phone:
        await sms_service.send_sms(applicant.phone, "You have a new admission offer. Please check your portal.")

    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "offer_notified",
        "entity_type": "applicant",
        "entity_id": applicant_id,
        "action": "notify_offer",
        "performed_by": str(current_user.id),
        "details": {"programme": programme_name},
    })

    return _to_response(applicant)


@router.post("/applicant/{applicant_id}/issue-credentials", tags=["Permanent Credentials"])
async def issue_real_credentials(
    applicant_id: str,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    Issue permanent credentials (username + temporary password) to an applicant after OFFERED decision.
    
    Called by admissions officer when applicant is marked as OFFERED.
    The applicant will receive real credentials to use instead of PIN+Serial.
    
    Workflow:
    1. Admissions officer marks applicant as OFFERED
    2. System calls this endpoint
    3. Permanent credentials generated (username + temp password)
    4. ApplicationForm marked as expired (PIN/Serial no longer valid)
    5. Credentials sent via email to applicant
    """
    try:
        from app.infrastructure.database.repositories.application_form_repository import ApplicationFormRepository
        from app.infrastructure.services.permanent_credential_service import PermanentCredentialService
        
        # Get applicant
        applicant = await applicant_repo.get_by_id(applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # Verify applicant status is OFFERED
        if applicant.status != "offered":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Applicant status is {applicant.status}, not OFFERED. Only OFFERED applicants can receive real credentials."
            )
        
        # Get application form
        app_form_repo = ApplicationFormRepository()
        app_form = await app_form_repo.get_by_applicant_id(str(applicant.user_id))
        
        if not app_form:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No application form found for this applicant"
            )
        
        # Check if credentials already issued
        if app_form.has_real_credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Real credentials already issued for this applicant"
            )
        
        # Generate credentials
        cred_service = PermanentCredentialService()
        credentials = await cred_service.issue_credentials_for_applicant(
            application_form=app_form,
            issued_by=str(current_user.id),
        )
        
        # Update applicant with decision info
        applicant.application_decision = "OFFERED"
        applicant.decision_date = datetime.utcnow()
        await applicant_repo.save(applicant)
        
        # Audit log
        await audit_repo.create({
            "tenant_id": current_user.tenant_id,
            "event_type": "credentials_issued",
            "entity_type": "applicant",
            "entity_id": applicant_id,
            "action": "issue_real_credentials",
            "performed_by": str(current_user.id),
            "details": {
                "username": credentials["username"],
                "credential_id": credentials["credential_id"],
                "activation_deadline": credentials["activation_deadline"].isoformat(),
            },
        })
        
        # Send email with credentials
        from app.infrastructure.services.credential_email_service import CredentialEmailService
        email_service = CredentialEmailService()
        
        user = await get_user_repo().get_by_id(str(applicant.user_id))
        if user:
            await email_service.send_real_credentials(
                recipient_email=user.email,
                first_name=user.first_name or "Student",
                username=credentials["username"],
                temporary_password=credentials["temporary_password"],
                activation_deadline=credentials["activation_deadline"],
            )
        
        return {
            "success": True,
            "message": "Real credentials generated and issued",
            "credential_id": credentials["credential_id"],
            "username": credentials["username"],
            "activation_deadline": credentials["activation_deadline"],
            "must_change_password": credentials["must_change_password"],
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error issuing credentials to applicant {applicant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to issue credentials: {str(e)}"
        )


@router.post("/credentials/batch-issue", tags=["Credentials"])
async def batch_issue_credentials(
    admission_cycle_id: str,
    status_filter: str = "offered",
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    Batch issue credentials to all OFFERED applicants in a cycle.
    
    Admin endpoint for bulk credential issuance after admissions decisions.
    
    Query Parameters:
    - admission_cycle_id: The admission cycle to process
    - status_filter: Filter applicants by status (default: "offered")
    
    Returns:
        Summary of issued credentials with success/failure counts
    """
    try:
        from app.infrastructure.database.repositories.application_form_repository import ApplicationFormRepository
        from app.infrastructure.services.permanent_credential_service import PermanentCredentialService
        from app.infrastructure.services.credential_email_service import CredentialEmailService
        
        app_form_repo = ApplicationFormRepository()
        cred_service = PermanentCredentialService()
        email_service = CredentialEmailService()
        user_repo = get_user_repo()
        
        # Get all applicants with specified status in this cycle
        query = {
            "admission_cycle_id": admission_cycle_id,
            "status": status_filter,
        }
        applicants = await applicant_repo.model.find(query).to_list(None)
        
        results = {
            "total": len(applicants),
            "issued": 0,
            "already_issued": 0,
            "errors": [],
        }
        
        for applicant in applicants:
            try:
                # Get application form
                app_form = await app_form_repo.get_by_applicant_id(str(applicant.user_id))
                
                if not app_form:
                    results["errors"].append({
                        "applicant_id": str(applicant.id),
                        "reason": "No application form found"
                    })
                    continue
                
                # Check if already issued
                if app_form.has_real_credentials:
                    results["already_issued"] += 1
                    continue
                
                # Generate and issue credentials
                credentials = await cred_service.issue_credentials_for_applicant(
                    application_form=app_form,
                    issued_by=str(current_user.id),
                )
                
                # Send email
                user = await user_repo.get_by_id(str(applicant.user_id))
                if user:
                    await email_service.send_real_credentials(
                        recipient_email=user.email,
                        first_name=user.first_name or "Student",
                        username=credentials["username"],
                        temporary_password=credentials["temporary_password"],
                        activation_deadline=credentials["activation_deadline"],
                    )
                
                results["issued"] += 1
                
                # Audit log
                await audit_repo.create({
                    "tenant_id": current_user.tenant_id,
                    "event_type": "batch_credentials_issued",
                    "entity_type": "applicant",
                    "entity_id": str(applicant.id),
                    "action": "batch_issue_real_credentials",
                    "performed_by": str(current_user.id),
                    "details": {
                        "username": credentials["username"],
                        "credential_id": credentials["credential_id"],
                    },
                })
                
            except Exception as e:
                logger.error(f"Error issuing credentials to applicant {applicant.id}: {e}")
                results["errors"].append({
                    "applicant_id": str(applicant.id),
                    "reason": str(e)
                })
        
        return {
            "success": True,
            "message": f"Batch credential issuance completed",
            "admission_cycle_id": admission_cycle_id,
            "results": results,
        }
        
    except Exception as e:
        logger.error(f"Error in batch credential issuance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch issuance failed: {str(e)}"
        )


@router.get("/credentials/statistics", tags=["Credentials"])
async def get_credential_statistics(
    admission_cycle_id: str,
    current_user: User = Depends(require_roles("admissions_officer", "registrar", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
):
    """
    Get credential statistics for an admission cycle.
    
    Returns:
        Statistics on credential generation and status
    """
    try:
        from app.infrastructure.database.repositories.permanent_credential_repository import PermanentCredentialRepository
        
        cred_repo = PermanentCredentialRepository()
        
        # Get statistics
        total_applicants = await applicant_repo.model.find({
            "admission_cycle_id": admission_cycle_id,
        }).count()
        
        offered_applicants = await applicant_repo.model.find({
            "admission_cycle_id": admission_cycle_id,
            "status": "offered",
        }).count()
        
        total_credentials_issued = await cred_repo.model.find({
            "admission_cycle_id": admission_cycle_id,
        }).count()
        
        active_credentials = await cred_repo.model.find({
            "admission_cycle_id": admission_cycle_id,
            "is_active": True,
        }).count()
        
        logins_count = await cred_repo.model.find({
            "admission_cycle_id": admission_cycle_id,
            "last_login_at": {"$exists": True},
        }).count()
        
        password_changes = await cred_repo.model.find({
            "admission_cycle_id": admission_cycle_id,
            "is_temporary_password": False,
        }).count()
        
        return {
            "success": True,
            "admission_cycle_id": admission_cycle_id,
            "statistics": {
                "total_applicants": total_applicants,
                "offered_applicants": offered_applicants,
                "offer_rate_percent": (offered_applicants / max(total_applicants, 1)) * 100,
                "total_credentials_issued": total_credentials_issued,
                "credential_issuance_rate_percent": (total_credentials_issued / max(offered_applicants, 1)) * 100,
                "active_credentials": active_credentials,
                "applicants_who_logged_in": logins_count,
                "applicants_who_changed_password": password_changes,
                "activation_rate_percent": (password_changes / max(total_credentials_issued, 1)) * 100,
            },
        }
        
    except Exception as e:
        logger.error(f"Error getting credential statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )

