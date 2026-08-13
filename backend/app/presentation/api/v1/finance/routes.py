from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from typing import Any, Dict, List
from app.presentation.api.v1.finance.schemas import (
    InitiatePaymentRequest, PaymentListItem, PaymentHistoryItem, PaymentResponse,
    FeeStructureCreateRequest, FeeStructureUpdateRequest, FeeStructureResponse,
    ScholarshipRequest, ScholarshipResponse,
    BalanceResponse, ClearanceResponse,
    TenantCreateRequest, TenantUpdateRequest, TenantResponse,
    AuditSummaryResponse, AuditEventResponse, AuditListResponse,
)
from app.application.finance.process_payment import ProcessPaymentUseCase
from app.application.finance.fee_calculation import FeeCalculatorUseCase
from app.domain.finance.financial_clearance import FinancialClearanceService
from app.infrastructure.external_services.paystack_service import PaystackService
from app.infrastructure.external_services.email_service import EmailService
from app.dependencies import (
    get_current_user, get_payment_repo,
    get_tenant_repo, get_audit_repo, require_roles
)
from app.infrastructure.models.user import User
from app.infrastructure.models.finance import PaymentStatusEnum
from app.infrastructure.database.repositories.payment_repository import (
    ScholarshipRepository, FeeStructureRepository
)
from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.infrastructure.database.repositories.audit_repository import AuditRepository
from starlette.responses import StreamingResponse, FileResponse, JSONResponse
import csv
import io
import threading
import tempfile
import uuid
import os
from datetime import timezone

router = APIRouter()

def get_paystack_service() -> PaystackService:
    return PaystackService()


def build_tenant_response(tenant: Any) -> TenantResponse:
    return TenantResponse(
        id=str(tenant.id),
        name=tenant.name,
        subdomain=tenant.subdomain,
        description=tenant.description,
        logo_url=getattr(tenant, "logo_url", None),
        favicon_url=getattr(tenant, "favicon_url", None),
        admin_email=tenant.admin_email,
        admin_phone=tenant.admin_phone,
        country=tenant.country,
        timezone=tenant.timezone,
        primary_color=getattr(tenant, "primary_color", None),
        secondary_color=getattr(tenant, "secondary_color", None),
        accent_color=getattr(tenant, "accent_color", None),
        subscription_tier=tenant.subscription_tier,
        subscription_start=tenant.subscription_start,
        subscription_end=tenant.subscription_end,
        is_active=tenant.is_active,
        is_trial=tenant.is_trial,
        features=tenant.features,
    )

def get_email_service() -> EmailService:
    return EmailService()

def get_scholarship_repo() -> ScholarshipRepository:
    return ScholarshipRepository()

def get_fee_structure_repo() -> FeeStructureRepository:
    return FeeStructureRepository()

@router.post("/payments/initiate")
async def initiate_payment(
    request: InitiatePaymentRequest,
    current_user: User = Depends(get_current_user),
    payment_repo=Depends(get_payment_repo),
    paystack: PaystackService = Depends(get_paystack_service),
):
    """Initiate payment via Paystack"""

    use_case = ProcessPaymentUseCase(payment_repo)
    result = await use_case.initiate_payment(
        tenant_id=current_user.tenant_id or "default",
        **request.dict()
    )

    paystack_response = await paystack.initialize_transaction(
        email=current_user.email,
        amount=request.amount,
        reference=result["payment_reference"],
        metadata={
            "student_id": request.student_id,
            "fee_type": request.fee_type,
        }
    )

    if not paystack_response.get("status"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=paystack_response.get("message", "Payment initialization failed")
        )

    return {
        **result,
        "authorization_url": paystack_response["data"]["authorization_url"],
        "access_code": paystack_response["data"]["access_code"],
    }

@router.get("/payments/verify/{reference}")
async def verify_payment(
    reference: str,
    payment_repo=Depends(get_payment_repo),
    paystack: PaystackService = Depends(get_paystack_service),
    email_service: EmailService = Depends(get_email_service),
):
    """Verify payment status with Paystack"""

    verification = await paystack.verify_transaction(reference)

    if verification.get("verified"):
        payment = await payment_repo.get_one(payment_reference=reference)
        if payment:
            use_case = ProcessPaymentUseCase(payment_repo)
            result = await use_case.confirm_payment(str(payment.id), reference)

            await email_service.send_payment_receipt(
                to="student@example.com",
                amount=verification["amount"],
                receipt_number=result["receipt_number"],
            )

            return {"verified": True, **result}

    return {"verified": False, "message": verification.get("message")}

@router.post("/payments/webhook")
async def paystack_webhook(
    request: Request,
    payment_repo=Depends(get_payment_repo),
    paystack: PaystackService = Depends(get_paystack_service),
):
    """Paystack webhook endpoint for automatic payment confirmation"""

    signature = request.headers.get("x-paystack-signature", "")
    body = await request.body()

    if not paystack.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    payload = await request.json()
    event = payload.get("event")

    if event == "charge.success":
        reference = payload["data"]["reference"]
        payment = await payment_repo.get_one(payment_reference=reference)

        if payment:
            use_case = ProcessPaymentUseCase(payment_repo)
            await use_case.confirm_payment(str(payment.id), reference)

    return {"status": "received"}

@router.get("/payments", response_model=List[PaymentListItem])
async def list_payments(
    student_id: str | None = Query(None, alias="student_id"),
    status: str | None = Query(None),
    fee_type: str | None = Query(None, alias="fee_type"),
    start_date: datetime | None = Query(None, alias="start_date"),
    end_date: datetime | None = Query(None, alias="end_date"),
    current_user: User = Depends(require_roles("finance_officer", "university_admin", "super_admin")),
    payment_repo=Depends(get_payment_repo),
):
    tenant_id = current_user.tenant_id or "default"
    query = {"tenant_id": tenant_id}
    if student_id:
        query["student_id"] = student_id
    if status:
        query["status"] = status.lower()
    if fee_type:
        query["fee_type"] = fee_type
    if start_date or end_date:
        date_filter: Dict[str, datetime] = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        query["payment_date"] = date_filter

    payments = await payment_repo.model.find(query).to_list(None)
    return [
        PaymentListItem(
            id=str(p.id), tenant_id=p.tenant_id,
            student_id=getattr(p, "student_id", None),
            applicant_id=getattr(p, "applicant_id", None),
            amount=p.amount, fee_type=p.fee_type,
            academic_year=getattr(p, "academic_year", None),
            payment_method=p.payment_method, payment_reference=p.payment_reference,
            status=p.status, paystack_reference=p.paystack_reference,
            payment_date=p.payment_date, receipt_number=p.receipt_number,
            created_at=p.created_at,
        )
        for p in payments
    ]


@router.get("/payments/student/{student_id}", response_model=List[PaymentHistoryItem])
async def get_payment_history(
    student_id: str,
    current_user: User = Depends(get_current_user),
    payment_repo=Depends(get_payment_repo),
):
    use_case = ProcessPaymentUseCase(payment_repo)
    payments = await use_case.get_student_payment_history(
        current_user.tenant_id or "default", student_id
    )
    return [
        PaymentHistoryItem(
            id=str(p.id), amount=p.amount, fee_type=p.fee_type,
            status=p.status, payment_date=p.payment_date,
            receipt_number=p.receipt_number
        )
        for p in payments
    ]


@router.post("/payments/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_id: str,
    current_user: User = Depends(require_roles("finance_officer", "university_admin", "super_admin")),
    payment_repo=Depends(get_payment_repo),
    audit_repo=Depends(get_audit_repo),
):
    payment = await payment_repo.get_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if current_user.role.value != "super_admin" and payment.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    if payment.status == PaymentStatusEnum.SUCCESS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment is already confirmed")

    use_case = ProcessPaymentUseCase(payment_repo)
    result = await use_case.confirm_payment(payment_id, "manual")

    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "payment_confirmed",
        "entity_type": "payment",
        "entity_id": payment_id,
        "action": "confirm_payment",
        "performed_by": str(current_user.id),
        "details": {"payment_reference": payment.payment_reference, "amount": payment.amount, "status": result.get("status")},
    })

    return PaymentResponse(
        payment_id=payment_id,
        payment_reference=payment.payment_reference,
        amount=payment.amount,
        status=result["status"],
    )


@router.post("/payments/{payment_id}/reject", response_model=PaymentResponse)
async def reject_payment(
    payment_id: str,
    reason: str | None = Query(None),
    current_user: User = Depends(require_roles("finance_officer", "university_admin", "super_admin")),
    payment_repo=Depends(get_payment_repo),
    audit_repo=Depends(get_audit_repo),
):
    payment = await payment_repo.get_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if current_user.role.value != "super_admin" and payment.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    if payment.status == PaymentStatusEnum.FAILED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment is already rejected")

    use_case = ProcessPaymentUseCase(payment_repo)
    result = await use_case.fail_payment(payment_id, reason)

    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "payment_rejected",
        "entity_type": "payment",
        "entity_id": payment_id,
        "action": "reject_payment",
        "performed_by": str(current_user.id),
        "details": {"reason": reason, "payment_reference": payment.payment_reference, "amount": payment.amount, "status": result.get("status")},
    })

    return PaymentResponse(
        payment_id=payment_id,
        payment_reference=payment.payment_reference,
        amount=payment.amount,
        status=result["status"],
    )


@router.post("/payments/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: str,
    current_user: User = Depends(require_roles("finance_officer", "university_admin", "super_admin")),
    payment_repo=Depends(get_payment_repo),
    audit_repo=Depends(get_audit_repo),
):
    payment = await payment_repo.get_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if current_user.role.value != "super_admin" and payment.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    if payment.status != PaymentStatusEnum.SUCCESS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only successful payments can be refunded")

    refunded_payment = await payment_repo.update(payment_id, {"status": PaymentStatusEnum.CANCELLED})

    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "payment_refunded",
        "entity_type": "payment",
        "entity_id": payment_id,
        "action": "refund_payment",
        "performed_by": str(current_user.id),
        "details": {"payment_reference": payment.payment_reference, "amount": payment.amount, "status": refunded_payment.status},
    })
    return PaymentResponse(
        payment_id=payment_id,
        payment_reference=payment.payment_reference,
        amount=payment.amount,
        status=refunded_payment.status,
    )


@router.get("/balance/{student_id}", response_model=BalanceResponse)
async def get_student_balance(
    student_id: str,
    academic_year: str | None = Query(None, alias="academic_year"),
    current_user: User = Depends(require_roles("finance_officer", "university_admin", "super_admin")),
    payment_repo=Depends(get_payment_repo),
    scholarship_repo=Depends(get_scholarship_repo),
    fee_repo=Depends(get_fee_structure_repo),
):
    tenant_id = current_user.tenant_id or "default"
    calculator = FeeCalculatorUseCase(
        payment_repo=payment_repo,
        scholarship_repo=scholarship_repo,
        fee_repo=fee_repo,
    )
    balance_data = await calculator.calculate_balance(tenant_id, student_id, academic_year)
    clearance_service = FinancialClearanceService()
    balance_data["balance"] = await clearance_service.calculate_fee_balance(
        balance_data["total_due"], balance_data["total_paid"], balance_data["total_scholarships"]
    )

    return BalanceResponse(**balance_data)


@router.get("/clearance/{student_id}", response_model=ClearanceResponse)
async def get_student_clearance(
    student_id: str,
    academic_year: str | None = Query(None, alias="academic_year"),
    current_user: User = Depends(require_roles("finance_officer", "university_admin", "super_admin")),
    payment_repo=Depends(get_payment_repo),
    scholarship_repo=Depends(get_scholarship_repo),
    fee_repo=Depends(get_fee_structure_repo),
):
    tenant_id = current_user.tenant_id or "default"
    calculator = FeeCalculatorUseCase(
        payment_repo=payment_repo,
        scholarship_repo=scholarship_repo,
        fee_repo=fee_repo,
    )
    balance_data = await calculator.calculate_balance(tenant_id, student_id, academic_year)
    clearance_service = FinancialClearanceService()
    balance = await clearance_service.calculate_fee_balance(
        balance_data["total_due"], balance_data["total_paid"], balance_data["total_scholarships"]
    )

    payments = await payment_repo.get_by_student(tenant_id, student_id)
    pending_count = len([p for p in payments if str(getattr(p, "status", "")).lower() == "pending"])
    is_cleared, message = await clearance_service.check_clearance(student_id, balance, pending_count)

    return ClearanceResponse(
        student_id=student_id,
        tenant_id=tenant_id,
        is_cleared=is_cleared,
        message=message,
        balance=balance,
        pending_payments=pending_count,
    )


@router.post("/structures", response_model=FeeStructureResponse)
async def create_fee_structure(
    request: FeeStructureCreateRequest,
    current_user: User = Depends(require_roles("finance_officer", "university_admin", "super_admin")),
    fee_repo: FeeStructureRepository = Depends(get_fee_structure_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    data = {"tenant_id": current_user.tenant_id or "default", **request.dict()}
    structure = await fee_repo.create(data)

    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "fee_structure_created",
        "entity_type": "fee_structure",
        "entity_id": str(structure.id),
        "action": "create_fee_structure",
        "performed_by": str(current_user.id),
        "details": {"academic_year": structure.academic_year, "programme_id": structure.programme_id},
    })
    return FeeStructureResponse(
        id=str(structure.id), programme_id=structure.programme_id,
        level=structure.level, academic_year=structure.academic_year,
        fees=structure.fees,
    )


@router.get("/structures/{structure_id}", response_model=FeeStructureResponse)
async def get_fee_structure(
    structure_id: str,
    current_user: User = Depends(get_current_user),
    fee_repo: FeeStructureRepository = Depends(get_fee_structure_repo),
):
    structure = await fee_repo.get_by_id(structure_id)
    if not structure or structure.tenant_id != (current_user.tenant_id or "default"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee structure not found")
    return FeeStructureResponse(
        id=str(structure.id), programme_id=structure.programme_id,
        level=structure.level, academic_year=structure.academic_year,
        fees=structure.fees,
    )


@router.put("/structures/{structure_id}", response_model=FeeStructureResponse)
async def update_fee_structure(
    structure_id: str,
    request: FeeStructureUpdateRequest,
    current_user: User = Depends(require_roles("finance_officer", "university_admin", "super_admin")),
    fee_repo: FeeStructureRepository = Depends(get_fee_structure_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    structure = await fee_repo.get_by_id(structure_id)
    if not structure or structure.tenant_id != (current_user.tenant_id or "default"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee structure not found")

    update_data = request.dict(exclude_none=True)
    updated = await fee_repo.update(structure_id, update_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to update fee structure")

    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "fee_structure_updated",
        "entity_type": "fee_structure",
        "entity_id": structure_id,
        "action": "update_fee_structure",
        "performed_by": str(current_user.id),
        "details": update_data,
    })

    return FeeStructureResponse(
        id=str(updated.id), programme_id=updated.programme_id,
        level=updated.level, academic_year=updated.academic_year,
        fees=updated.fees,
    )


@router.get("/structures", response_model=List[FeeStructureResponse])
async def list_fee_structures(
    programme_id: str | None = Query(None, alias="programme_id"),
    level: str | None = Query(None),
    academic_year: str | None = Query(None, alias="academic_year"),
    current_user: User = Depends(get_current_user),
    fee_repo: FeeStructureRepository = Depends(get_fee_structure_repo),
):
    filters: Dict[str, Any] = {"tenant_id": current_user.tenant_id or "default"}
    if programme_id is not None:
        filters["programme_id"] = programme_id
    if level is not None:
        filters["level"] = level
    if academic_year is not None:
        filters["academic_year"] = academic_year

    structures = await fee_repo.get_all(**filters)
    return [
        FeeStructureResponse(
            id=str(s.id), programme_id=s.programme_id,
            level=s.level, academic_year=s.academic_year,
            fees=s.fees,
        ) for s in structures
    ]


@router.get("/scholarships", response_model=List[ScholarshipResponse])
async def list_scholarships(
    student_id: str | None = Query(None, alias="student_id"),
    scholarship_type: str | None = Query(None, alias="scholarship_type"),
    is_active: bool | None = Query(None, alias="is_active"),
    current_user: User = Depends(require_roles("finance_officer", "university_admin", "super_admin")),
    scholarship_repo: ScholarshipRepository = Depends(get_scholarship_repo),
):
    filters: Dict[str, Any] = {"tenant_id": current_user.tenant_id or "default"}
    if student_id is not None:
        filters["student_id"] = student_id
    if scholarship_type is not None:
        filters["scholarship_type"] = scholarship_type
    if is_active is not None:
        filters["is_active"] = is_active

    scholarships = await scholarship_repo.get_all(**filters)
    return [
        ScholarshipResponse(
            id=str(s.id), student_id=s.student_id,
            name=s.name, scholarship_type=s.scholarship_type,
            amount=s.amount, percentage=s.percentage,
            start_date=s.start_date, end_date=s.end_date,
            is_active=s.is_active,
        ) for s in scholarships
    ]


@router.get("/scholarships/{scholarship_id}", response_model=ScholarshipResponse)
async def get_scholarship(
    scholarship_id: str,
    current_user: User = Depends(require_roles("finance_officer", "university_admin", "super_admin")),
    scholarship_repo: ScholarshipRepository = Depends(get_scholarship_repo),
):
    scholarship = await scholarship_repo.get_by_id(scholarship_id)
    if not scholarship or scholarship.tenant_id != (current_user.tenant_id or "default"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found")
    return ScholarshipResponse(
        id=str(scholarship.id), student_id=scholarship.student_id,
        name=scholarship.name, scholarship_type=scholarship.scholarship_type,
        amount=scholarship.amount, percentage=scholarship.percentage,
        start_date=scholarship.start_date, end_date=scholarship.end_date,
        is_active=scholarship.is_active,
    )


@router.post("/scholarships", response_model=ScholarshipResponse)
async def create_scholarship(
    request: ScholarshipRequest,
    current_user: User = Depends(require_roles("finance_officer", "university_admin", "super_admin")),
    scholarship_repo: ScholarshipRepository = Depends(get_scholarship_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    data = {
        "tenant_id": current_user.tenant_id or "default",
        "approved_by": str(current_user.id),
        "approved_date": datetime.utcnow(),
        **request.dict(),
    }
    scholarship = await scholarship_repo.create(data)

    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "scholarship_created",
        "entity_type": "scholarship",
        "entity_id": str(scholarship.id),
        "action": "create_scholarship",
        "performed_by": str(current_user.id),
        "details": {"student_id": scholarship.student_id, "amount": scholarship.amount},
    })
    return ScholarshipResponse(
        id=str(scholarship.id), student_id=scholarship.student_id,
        name=scholarship.name, scholarship_type=scholarship.scholarship_type,
        amount=scholarship.amount, percentage=scholarship.percentage,
        start_date=scholarship.start_date, end_date=scholarship.end_date,
        is_active=scholarship.is_active,
    )


@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    request: TenantCreateRequest,
    current_user: User = Depends(require_roles("super_admin")),
    tenant_repo=Depends(get_tenant_repo),
):
    if await tenant_repo.exists(subdomain=request.subdomain):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant subdomain already exists")

    tenant = await tenant_repo.create(request.dict())
    return build_tenant_response(tenant)


@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(
    include_inactive: bool = False,
    current_user: User = Depends(require_roles("super_admin", "university_admin")),
    tenant_repo=Depends(get_tenant_repo),
):
    if current_user.role.value == "super_admin":
        tenants = await tenant_repo.get_all_tenants(include_inactive=include_inactive)
    else:
        tenants = await tenant_repo.get_all_tenants(include_inactive=include_inactive)
        tenants = [t for t in tenants if str(t.id) == current_user.tenant_id]
    return [build_tenant_response(t) for t in tenants]


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    current_user: User = Depends(require_roles("super_admin", "university_admin")),
    tenant_repo=Depends(get_tenant_repo),
):
    tenant = await tenant_repo.get_by_id(tenant_id)
    if not tenant or (current_user.role.value != "super_admin" and str(tenant.id) != current_user.tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return build_tenant_response(tenant)


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    request: TenantUpdateRequest,
    current_user: User = Depends(require_roles("super_admin", "university_admin")),
    tenant_repo=Depends(get_tenant_repo),
):
    tenant = await tenant_repo.get_by_id(tenant_id)
    if not tenant or (current_user.role.value != "super_admin" and str(tenant.id) != current_user.tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    update_data = request.dict(exclude_none=True)
    tenant = await tenant_repo.update(tenant_id, update_data)
    return build_tenant_response(tenant)


@router.patch("/tenants/{tenant_id}/activate", response_model=TenantResponse)
async def activate_tenant(
    tenant_id: str,
    current_user: User = Depends(require_roles("super_admin")),
    tenant_repo=Depends(get_tenant_repo),
):
    tenant = await tenant_repo.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    tenant = await tenant_repo.update(tenant_id, {"is_active": True})
    return build_tenant_response(tenant)


@router.patch("/tenants/{tenant_id}/deactivate", response_model=TenantResponse)
async def deactivate_tenant(
    tenant_id: str,
    current_user: User = Depends(require_roles("super_admin")),
    tenant_repo=Depends(get_tenant_repo),
):
    tenant = await tenant_repo.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    tenant = await tenant_repo.update(tenant_id, {"is_active": False})
    return build_tenant_response(tenant)


@router.get("/audit/summary", response_model=AuditSummaryResponse)
async def audit_summary(
    tenant_id: str | None = Query(None, alias="tenant_id"),
    current_user: User = Depends(require_roles("auditor", "university_admin", "super_admin")),
    audit_repo=Depends(get_audit_repo),
):
    tenant_filter = {}
    if current_user.role.value != "super_admin":
        tenant_filter = {"tenant_id": current_user.tenant_id or "default"}
    elif tenant_id:
        tenant_filter = {"tenant_id": tenant_id}

    audits = await audit_repo.model.find(tenant_filter).to_list(None)
    event_types = {}
    recent_events = []

    sorted_audits = sorted(audits, key=lambda audit: audit.created_at, reverse=True)[:10]
    for audit in audits:
        event_types[audit.event_type] = event_types.get(audit.event_type, 0) + 1

    for audit in sorted_audits:
        recent_events.append({
            "event_type": audit.event_type,
            "entity_type": audit.entity_type,
            "entity_id": getattr(audit, "entity_id", None),
            "action": audit.action,
            "performed_by": audit.performed_by,
            "details": audit.details,
            "created_at": audit.created_at,
        })

    return AuditSummaryResponse(
        total_events=len(audits),
        event_types=event_types,
        recent_events=recent_events,
    )


@router.get("/audit", response_model=AuditListResponse)
async def list_audits(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    event_type: str | None = Query(None),
    performed_by: str | None = Query(None),
    entity_type: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    tenant_id: str | None = Query(None),
    current_user: User = Depends(require_roles("auditor", "university_admin", "super_admin")),
    audit_repo=Depends(get_audit_repo),
):
    query: Dict[str, Any] = {}
    if current_user.role.value != "super_admin":
        query["tenant_id"] = current_user.tenant_id or "default"
    elif tenant_id:
        query["tenant_id"] = tenant_id

    if event_type:
        query["event_type"] = event_type
    if performed_by:
        query["performed_by"] = performed_by
    if entity_type:
        query["entity_type"] = entity_type
    if start_date or end_date:
        date_filter: Dict[str, datetime] = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        query["created_at"] = date_filter

    total = await audit_repo.model.find(query).count()
    skip = (page - 1) * page_size
    docs = await audit_repo.model.find(query).sort("-created_at").skip(skip).limit(page_size).to_list()

    events = [
        AuditEventResponse(
            event_type=d.event_type,
            entity_type=d.entity_type,
            entity_id=getattr(d, "entity_id", None),
            action=d.action,
            performed_by=getattr(d, "performed_by", None),
            details=getattr(d, "details", {}),
            created_at=d.created_at,
        )
        for d in docs
    ]

    return AuditListResponse(total=total, page=page, page_size=page_size, events=events)


@router.get("/audit/export")
async def export_audits(
    event_type: str | None = Query(None),
    performed_by: str | None = Query(None),
    entity_type: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    tenant_id: str | None = Query(None),
    current_user: User = Depends(require_roles("auditor", "university_admin", "super_admin")),
    audit_repo=Depends(get_audit_repo),
):
    query: Dict[str, Any] = {}
    if current_user.role.value != "super_admin":
        query["tenant_id"] = current_user.tenant_id or "default"
    elif tenant_id:
        query["tenant_id"] = tenant_id

    if event_type:
        query["event_type"] = event_type
    if performed_by:
        query["performed_by"] = performed_by
    if entity_type:
        query["entity_type"] = entity_type
    if start_date or end_date:
        date_filter: Dict[str, datetime] = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        query["created_at"] = date_filter

    # For very large exports, generate file in background and return job id
    docs_cursor = audit_repo.model.find(query).sort("-created_at")
    total_count = await docs_cursor.count()

    # threshold beyond which we enqueue background export
    BACKGROUND_EXPORT_THRESHOLD = 5000

    if total_count <= BACKGROUND_EXPORT_THRESHOLD:
        docs = await docs_cursor.to_list(None)

        def iter_csv():
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["created_at", "event_type", "entity_type", "entity_id", "action", "performed_by", "details"])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
            for d in docs:
                writer.writerow([
                    getattr(d, "created_at", ""),
                    getattr(d, "event_type", ""),
                    getattr(d, "entity_type", ""),
                    getattr(d, "entity_id", ""),
                    getattr(d, "action", ""),
                    getattr(d, "performed_by", ""),
                    getattr(d, "details", {}),
                ])
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)

        return StreamingResponse(iter_csv(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=audits.csv"})

    # otherwise start background export job
    job_id = str(uuid.uuid4())
    tmp_dir = tempfile.gettempdir()
    file_path = os.path.join(tmp_dir, f"audit_export_{job_id}.csv")

    # store jobs in module-level dict
    if not hasattr(router, "_export_jobs"):
        router._export_jobs = {}

    router._export_jobs[job_id] = {"status": "pending", "path": file_path, "created_at": datetime.now(timezone.utc), "total": total_count}

    def worker(q, out_path):
        import asyncio

        async def async_worker():
            try:
                out = io.StringIO()
                writer = csv.writer(out)
                writer.writerow(["created_at", "event_type", "entity_type", "entity_id", "action", "performed_by", "details"])
                with open(out_path, "w", newline='', encoding='utf-8') as fh:
                    fh.write(out.getvalue())
                    out.seek(0)
                    out.truncate(0)
                    batch_size = 500
                    skip = 0
                    while True:
                        docs_batch = await audit_repo.model.find(query).sort("-created_at").skip(skip).limit(batch_size).to_list(None)
                        if not docs_batch:
                            break
                        for d in docs_batch:
                            writer.writerow([
                                getattr(d, "created_at", ""),
                                getattr(d, "event_type", ""),
                                getattr(d, "entity_type", ""),
                                getattr(d, "entity_id", ""),
                                getattr(d, "action", ""),
                                getattr(d, "performed_by", ""),
                                getattr(d, "details", {}),
                            ])
                            fh.write(out.getvalue())
                            out.seek(0)
                            out.truncate(0)
                        if len(docs_batch) < batch_size:
                            break
                        skip += batch_size

                router._export_jobs[job_id]["status"] = "ready"
            except Exception as e:
                router._export_jobs[job_id]["status"] = "failed"
                router._export_jobs[job_id]["error"] = str(e)

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(async_worker())
        finally:
            loop.close()

    # Start background thread
    thread = threading.Thread(target=worker, args=(docs_cursor, file_path), daemon=True)
    thread.start()

    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"job_id": job_id, "status_url": f"/finance/audit/export/status/{job_id}", "download_url": f"/finance/audit/export/download/{job_id}"})


@router.post("/audit/export")
async def start_export_post(
    request: Request,
    current_user: User = Depends(require_roles("auditor", "university_admin", "super_admin")),
    audit_repo=Depends(get_audit_repo),
):
    payload = {}
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    # extract known params and forward
    event_type = payload.get("event_type")
    performed_by = payload.get("performed_by")
    entity_type = payload.get("entity_type")
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")
    tenant_id = payload.get("tenant_id")

    return await export_audits(event_type, performed_by, entity_type, start_date, end_date, tenant_id, current_user, audit_repo)


@router.get("/audit/export/status/{job_id}")
async def export_status(job_id: str):
    jobs = getattr(router, "_export_jobs", {})
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    return job


@router.get("/audit/export/download/{job_id}")
async def export_download(job_id: str):
    jobs = getattr(router, "_export_jobs", {})
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    if job.get("status") != "ready":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Export not ready")
    return FileResponse(job.get("path"), media_type="text/csv", filename="audits.csv")
