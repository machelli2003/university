"""
Staff Assignment CRUD Routes
Endpoints for managing staff-to-resource assignments
Section 57: Staff Assignment Management
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from app.dependencies import get_current_user
from app.infrastructure.models.staff_assignment import StaffAssignment
from app.infrastructure.repositories.staff_assignment_repository import StaffAssignmentRepository

router = APIRouter(prefix="/api/v1/staff-assignments", tags=["staff-assignments"])


# Response Models
class AssignmentResponse(BaseModel):
    """Staff Assignment response"""
    id: str = Field(alias="_id")
    tenant_id: str
    staff_id: str
    assignment_type: str
    resource_id: str
    resource_name: str
    staff_role: str
    permissions: List[str]
    is_active: bool
    assigned_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class CreateAssignmentRequest(BaseModel):
    """Create staff assignment request"""
    staff_id: str
    assignment_type: str  # DEPARTMENT, FACULTY, PROGRAMME, COURSE, etc.
    resource_id: str
    resource_name: str
    staff_role: str
    permissions: List[str] = []
    start_date: datetime
    end_date: datetime | None = None


class UpdateAssignmentRequest(BaseModel):
    """Update staff assignment request"""
    staff_role: str | None = None
    permissions: List[str] | None = None
    is_active: bool | None = None
    end_date: datetime | None = None


def _get_role(user) -> str:
    if isinstance(user, dict):
        return user.get("role", "")
    return user.role.value if hasattr(user.role, "value") else str(getattr(user, "role", ""))

def _get_tenant_id(user) -> str:
    if isinstance(user, dict):
        return user.get("tenant_id", "single-university")
    return str(getattr(user, "tenant_id", "single-university") or "single-university")

def _get_user_id(user) -> str:
    if isinstance(user, dict):
        return str(user.get("user_id") or user.get("id") or "")
    return str(getattr(user, "id", ""))


# Routes
@router.post("", response_model=AssignmentResponse, status_code=201)
async def create_assignment(
    request: CreateAssignmentRequest,
    current_user = Depends(get_current_user)
) -> AssignmentResponse:
    """
    Create a new staff assignment
    Only super_admin and university_admin can create assignments
    """
    # Authorization check
    if _get_role(current_user) not in ["super_admin", "university_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized: Only admins can create assignments")

    tenant_id = _get_tenant_id(current_user)
    
    assignment = StaffAssignment(
        tenant_id=tenant_id,
        staff_id=request.staff_id,
        assignment_type=request.assignment_type,
        resource_id=request.resource_id,
        resource_name=request.resource_name,
        staff_role=request.staff_role,
        permissions=request.permissions,
        start_date=request.start_date,
        end_date=request.end_date,
        is_active=True,
        assigned_by=_get_user_id(current_user),
        assigned_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    created = await StaffAssignmentRepository.create(assignment)
    
    return AssignmentResponse(
        id=str(created.id),
        tenant_id=created.tenant_id,
        staff_id=created.staff_id,
        assignment_type=created.assignment_type,
        resource_id=created.resource_id,
        resource_name=created.resource_name,
        staff_role=created.staff_role,
        permissions=created.permissions,
        is_active=created.is_active,
        assigned_at=created.assigned_at,
        updated_at=created.updated_at
    )


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: str,
    current_user = Depends(get_current_user)
) -> AssignmentResponse:
    """Get assignment by ID"""
    tenant_id = _get_tenant_id(current_user)
    
    assignment = await StaffAssignmentRepository.get_by_id(PydanticObjectId(assignment_id))
    
    if not assignment or assignment.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    return AssignmentResponse(
        id=str(assignment.id),
        tenant_id=assignment.tenant_id,
        staff_id=assignment.staff_id,
        assignment_type=assignment.assignment_type,
        resource_id=assignment.resource_id,
        resource_name=assignment.resource_name,
        staff_role=assignment.staff_role,
        permissions=assignment.permissions,
        is_active=assignment.is_active,
        assigned_at=assignment.assigned_at,
        updated_at=assignment.updated_at
    )


@router.get("/staff/{staff_id}", response_model=List[AssignmentResponse])
async def get_staff_assignments(
    staff_id: str,
    current_user = Depends(get_current_user)
) -> List[AssignmentResponse]:
    """Get all assignments for a staff member"""
    tenant_id = _get_tenant_id(current_user)
    
    assignments = await StaffAssignmentRepository.get_by_staff_id(tenant_id, staff_id)
    
    return [
        AssignmentResponse(
            id=str(a.id),
            tenant_id=a.tenant_id,
            staff_id=a.staff_id,
            assignment_type=a.assignment_type,
            resource_id=a.resource_id,
            resource_name=a.resource_name,
            staff_role=a.staff_role,
            permissions=a.permissions,
            is_active=a.is_active,
            assigned_at=a.assigned_at,
            updated_at=a.updated_at
        )
        for a in assignments
    ]


@router.get("", response_model=List[AssignmentResponse])
async def list_assignments(
    skip: int = 0,
    limit: int = 50,
    current_user = Depends(get_current_user)
) -> List[AssignmentResponse]:
    """List all assignments for current tenant"""
    tenant_id = _get_tenant_id(current_user)
    
    assignments = await StaffAssignmentRepository.list_by_tenant(tenant_id, skip, limit)
    
    return [
        AssignmentResponse(
            id=str(a.id),
            tenant_id=a.tenant_id,
            staff_id=a.staff_id,
            assignment_type=a.assignment_type,
            resource_id=a.resource_id,
            resource_name=a.resource_name,
            staff_role=a.staff_role,
            permissions=a.permissions,
            is_active=a.is_active,
            assigned_at=a.assigned_at,
            updated_at=a.updated_at
        )
        for a in assignments
    ]


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: str,
    request: UpdateAssignmentRequest,
    current_user = Depends(get_current_user)
) -> AssignmentResponse:
    """
    Update staff assignment
    Only super_admin and university_admin can update assignments
    """
    # Authorization check
    if _get_role(current_user) not in ["super_admin", "university_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized: Only admins can update assignments")

    tenant_id = _get_tenant_id(current_user)
    
    assignment = await StaffAssignmentRepository.get_by_id(PydanticObjectId(assignment_id))
    
    if not assignment or assignment.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Prepare update data
    update_data = {}
    if request.staff_role is not None:
        update_data["staff_role"] = request.staff_role
    if request.permissions is not None:
        update_data["permissions"] = request.permissions
    if request.is_active is not None:
        update_data["is_active"] = request.is_active
    if request.end_date is not None:
        update_data["end_date"] = request.end_date
    
    update_data["updated_at"] = datetime.utcnow()
    
    updated = await StaffAssignmentRepository.update(PydanticObjectId(assignment_id), update_data)
    
    return AssignmentResponse(
        id=str(updated.id),
        tenant_id=updated.tenant_id,
        staff_id=updated.staff_id,
        assignment_type=updated.assignment_type,
        resource_id=updated.resource_id,
        resource_name=updated.resource_name,
        staff_role=updated.staff_role,
        permissions=updated.permissions,
        is_active=updated.is_active,
        assigned_at=updated.assigned_at,
        updated_at=updated.updated_at
    )


@router.delete("/{assignment_id}", status_code=204)
async def delete_assignment(
    assignment_id: str,
    current_user = Depends(get_current_user)
):
    """
    Delete staff assignment
    Only super_admin and university_admin can delete assignments
    """
    # Authorization check
    if _get_role(current_user) not in ["super_admin", "university_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized: Only admins can delete assignments")

    tenant_id = _get_tenant_id(current_user)
    
    assignment = await StaffAssignmentRepository.get_by_id(PydanticObjectId(assignment_id))
    
    if not assignment or assignment.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    await StaffAssignmentRepository.delete(PydanticObjectId(assignment_id))
