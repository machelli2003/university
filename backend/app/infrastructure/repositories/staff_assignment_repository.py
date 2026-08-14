"""
Staff Assignment Repository
Handles CRUD operations for staff-to-resource assignments
"""
import inspect
from typing import List, Optional
from beanie import PydanticObjectId
from app.infrastructure.models.staff_assignment import AssignmentTypeEnum, StaffAssignment


class StaffAssignmentRepository:
    """Repository for staff assignment operations"""

    @staticmethod
    async def create(assignment: StaffAssignment) -> StaffAssignment:
        """Create a new staff assignment"""
        await assignment.insert()
        return assignment

    @staticmethod
    async def get_by_id(assignment_id: PydanticObjectId) -> Optional[StaffAssignment]:
        """Get assignment by ID"""
        return await StaffAssignment.get(assignment_id)

    @staticmethod
    async def get_by_staff_id(tenant_id: str, staff_id: str) -> List[StaffAssignment]:
        """Get all assignments for a staff member"""
        return await StaffAssignment.find(
            StaffAssignment.tenant_id == tenant_id,
            StaffAssignment.staff_id == staff_id
        ).to_list()

    @staticmethod
    async def get_by_resource(tenant_id: str, resource_id: str) -> List[StaffAssignment]:
        """Get all staff assigned to a resource"""
        return await StaffAssignment.find(
            StaffAssignment.tenant_id == tenant_id,
            StaffAssignment.resource_id == resource_id
        ).to_list()

    @staticmethod
    async def get_by_type(
        tenant_id: str, 
        assignment_type: str, 
        is_active: bool = True
    ) -> List[StaffAssignment]:
        """Get assignments by type and status"""
        normalized_type = AssignmentTypeEnum._missing_(assignment_type)
        if normalized_type is None:
            normalized_type = assignment_type.strip().lower() if isinstance(assignment_type, str) else assignment_type
        return await StaffAssignment.find(
            StaffAssignment.tenant_id == tenant_id,
            StaffAssignment.assignment_type == normalized_type,
            StaffAssignment.is_active == is_active
        ).to_list()

    @staticmethod
    async def update(
        assignment_id: PydanticObjectId, 
        update_data: dict
    ) -> Optional[StaffAssignment]:
        """Update an assignment"""
        assignment = await StaffAssignment.get(assignment_id)
        if not assignment:
            return None
        
        await assignment.update({"$set": update_data})
        return await StaffAssignment.get(assignment_id)

    @staticmethod
    async def delete(assignment_id: PydanticObjectId) -> bool:
        """Delete an assignment"""
        assignment = await StaffAssignment.get(assignment_id)
        if not assignment:
            return False
        
        await assignment.delete()
        return True

    @staticmethod
    async def list_by_tenant(
        tenant_id: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[StaffAssignment]:
        """List all assignments for a tenant"""
        query = StaffAssignment.find(StaffAssignment.tenant_id == tenant_id)
        skip_query = query.skip(skip)
        if inspect.isawaitable(skip_query):
            skip_query = await skip_query
        limit_query = skip_query.limit(limit)
        if inspect.isawaitable(limit_query):
            limit_query = await limit_query
        to_list = limit_query.to_list()
        if inspect.isawaitable(to_list):
            return await to_list
        return to_list

    @staticmethod
    async def check_assignment(
        tenant_id: str,
        staff_id: str,
        resource_id: str,
        permission: Optional[str] = None
    ) -> bool:
        """Check if staff has assignment to resource with optional permission"""
        assignment = await StaffAssignment.find(
            StaffAssignment.tenant_id == tenant_id,
            StaffAssignment.staff_id == staff_id,
            StaffAssignment.resource_id == resource_id,
            StaffAssignment.is_active == True
        ).first_or_none()
        
        if not assignment:
            return False
        
        if permission:
            return permission in assignment.permissions
        
        return True
