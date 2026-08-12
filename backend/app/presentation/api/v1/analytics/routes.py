from fastapi import APIRouter, Depends, Query
from app.dependencies import (
    get_current_user, get_applicant_repo, get_student_repo,
    get_payment_repo, require_roles
)
from app.infrastructure.models.user import User

router = APIRouter()

@router.get("/admissions/summary")
async def admissions_summary(
    tenant_id: str | None = Query(None, alias="tenant_id"),
    current_user: User = Depends(require_roles("admissions_officer", "university_admin", "super_admin")),
    applicant_repo=Depends(get_applicant_repo),
):
    if current_user.role.value == "super_admin" and tenant_id:
        selected_tenant_id = tenant_id
    else:
        selected_tenant_id = current_user.tenant_id or "default"

    total = await applicant_repo.count(tenant_id=selected_tenant_id)
    eligible = len(await applicant_repo.get_eligible_applicants(selected_tenant_id))
    pending = len(await applicant_repo.get_pending_verification(selected_tenant_id))

    return {
        "total_applications": total,
        "eligible": eligible,
        "pending_verification": pending,
    }

@router.get("/enrollment/summary")
async def enrollment_summary(
    tenant_id: str | None = Query(None, alias="tenant_id"),
    current_user: User = Depends(require_roles("registrar", "university_admin", "super_admin")),
    student_repo=Depends(get_student_repo),
):
    if current_user.role.value == "super_admin" and tenant_id:
        selected_tenant_id = tenant_id
    else:
        selected_tenant_id = current_user.tenant_id or "default"

    active = len(await student_repo.get_by_status(selected_tenant_id, "active"))
    probation = len(await student_repo.get_on_probation(selected_tenant_id))

    return {
        "active_students": active,
        "on_probation": probation,
    }

@router.get("/finance/summary")
async def finance_summary(
    tenant_id: str | None = Query(None, alias="tenant_id"),
    current_user: User = Depends(require_roles("finance_officer", "university_admin", "super_admin")),
    payment_repo=Depends(get_payment_repo),
):
    from datetime import datetime, timedelta
    if current_user.role.value == "super_admin" and tenant_id:
        selected_tenant_id = tenant_id
    else:
        selected_tenant_id = current_user.tenant_id or "default"

    start = datetime.utcnow() - timedelta(days=30)
    end = datetime.utcnow()

    revenue = await payment_repo.get_revenue_for_period(selected_tenant_id, start, end)
    pending = len(await payment_repo.get_pending_payments(selected_tenant_id))

    return {
        "revenue_last_30_days": revenue,
        "pending_payments": pending,
    }
