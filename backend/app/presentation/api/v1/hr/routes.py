from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.presentation.api.v1.hr.schemas import CreateStaffRequest, LeaveRequest
from app.infrastructure.database.repositories.hr_repository import (
    StaffMemberRepository, LeaveRepository, PerformanceAppraisalRepository
)
from app.dependencies import get_current_user, require_roles
from app.infrastructure.models.user import User

router = APIRouter()

def get_staff_repo() -> StaffMemberRepository:
    return StaffMemberRepository()

def get_leave_repo() -> LeaveRepository:
    return LeaveRepository()

@router.post("/staff")
async def create_staff(
    request: CreateStaffRequest,
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    staff_repo=Depends(get_staff_repo),
):
    staff = await staff_repo.create({"tenant_id": current_user.tenant_id or "default", **request.dict()})
    return {"id": str(staff.id), "employee_id": staff.employee_id}

@router.get("/staff/department/{department_id}")
async def list_staff_by_department(
    department_id: str,
    current_user: User = Depends(get_current_user),
    staff_repo=Depends(get_staff_repo),
):
    staff = await staff_repo.get_by_department(department_id)
    return [{"id": str(s.id), "first_name": s.first_name, "last_name": s.last_name, "position": s.position} for s in staff]

@router.post("/leave/request")
async def request_leave(
    request: LeaveRequest,
    current_user: User = Depends(get_current_user),
    staff_repo=Depends(get_staff_repo),
    leave_repo=Depends(get_leave_repo),
):
    staff = await staff_repo.get_by_user_id(current_user.tenant_id or "default", str(current_user.id))
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff record not found")

    leave = await leave_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "staff_id": str(staff.id),
        **request.dict()
    })
    return {"id": str(leave.id), "status": "pending"}

@router.get("/leave/pending")
async def list_pending_leaves(
    current_user: User = Depends(require_roles("head_of_department", "university_admin", "super_admin")),
    leave_repo=Depends(get_leave_repo),
):
    leaves = await leave_repo.get_pending(current_user.tenant_id or "default")
    return [{"id": str(l.id), "staff_id": l.staff_id, "leave_type": l.leave_type, "reason": l.reason} for l in leaves]

@router.post("/leave/{leave_id}/approve")
async def approve_leave(
    leave_id: str,
    current_user: User = Depends(require_roles("head_of_department", "university_admin", "super_admin")),
    leave_repo=Depends(get_leave_repo),
):
    await leave_repo.update(leave_id, {"status": "approved", "approved_by": str(current_user.id)})
    return {"id": leave_id, "status": "approved"}

@router.post("/leave/{leave_id}/reject")
async def reject_leave(
    leave_id: str,
    current_user: User = Depends(require_roles("head_of_department", "university_admin", "super_admin")),
    leave_repo=Depends(get_leave_repo),
):
    await leave_repo.update(leave_id, {"status": "rejected", "approved_by": str(current_user.id)})
    return {"id": leave_id, "status": "rejected"}
