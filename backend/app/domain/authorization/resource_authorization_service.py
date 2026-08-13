"""
Resource-Level Authorization Service
Validates staff assignments and permissions for resource access
Section 57: Resource-Level Authorization
"""
from typing import Optional, List
from app.infrastructure.repositories.staff_assignment_repository import StaffAssignmentRepository


class ResourceAuthorizationService:
    """Service for resource-level authorization checks"""

    @staticmethod
    async def can_access_resource(
        tenant_id: str,
        staff_id: str,
        resource_id: str,
        required_permission: Optional[str] = None
    ) -> bool:
        """
        Check if staff member can access a specific resource
        
        Args:
            tenant_id: Tenant ID
            staff_id: Staff member ID
            resource_id: Resource ID to access
            required_permission: Specific permission required (optional)
        
        Returns:
            True if authorized, False otherwise
        """
        return await StaffAssignmentRepository.check_assignment(
            tenant_id=tenant_id,
            staff_id=staff_id,
            resource_id=resource_id,
            permission=required_permission
        )

    @staticmethod
    async def can_access_resource_type(
        tenant_id: str,
        staff_id: str,
        resource_type: str,
        required_permission: Optional[str] = None
    ) -> bool:
        """
        Check if staff member has assignment of a specific type
        
        Args:
            tenant_id: Tenant ID
            staff_id: Staff member ID
            resource_type: Type of resource (DEPARTMENT, PROGRAMME, COURSE, etc.)
            required_permission: Specific permission required (optional)
        
        Returns:
            True if authorized, False otherwise
        """
        assignments = await StaffAssignmentRepository.get_by_type(
            tenant_id=tenant_id,
            assignment_type=resource_type,
            is_active=True
        )
        
        for assignment in assignments:
            if assignment.staff_id == staff_id:
                if required_permission:
                    if required_permission in assignment.permissions:
                        return True
                else:
                    return True
        
        return False

    @staticmethod
    async def get_accessible_resources(
        tenant_id: str,
        staff_id: str,
        resource_type: Optional[str] = None
    ) -> List[str]:
        """
        Get all resource IDs accessible to staff member
        
        Args:
            tenant_id: Tenant ID
            staff_id: Staff member ID
            resource_type: Optional filter by resource type
        
        Returns:
            List of accessible resource IDs
        """
        assignments = await StaffAssignmentRepository.get_by_staff_id(tenant_id, staff_id)
        
        resources = []
        for assignment in assignments:
            if assignment.is_active:
                if resource_type is None or assignment.assignment_type == resource_type:
                    resources.append(assignment.resource_id)
        
        return resources

    @staticmethod
    async def validate_resource_access(
        tenant_id: str,
        staff_id: str,
        resource_id: str,
        required_permission: Optional[str] = None
    ) -> dict:
        """
        Validate resource access and return authorization details
        
        Args:
            tenant_id: Tenant ID
            staff_id: Staff member ID
            resource_id: Resource ID to access
            required_permission: Specific permission required (optional)
        
        Returns:
            Dict with authorization details or raises error
        """
        assignment = await StaffAssignmentRepository.get_by_staff_id(tenant_id, staff_id)
        
        authorized_assignment = None
        for a in assignment:
            if a.resource_id == resource_id and a.is_active:
                authorized_assignment = a
                break
        
        if not authorized_assignment:
            return {"authorized": False, "reason": "No assignment for this resource"}
        
        if required_permission and required_permission not in authorized_assignment.permissions:
            return {"authorized": False, "reason": f"Missing permission: {required_permission}"}
        
        return {
            "authorized": True,
            "staff_role": authorized_assignment.staff_role,
            "permissions": authorized_assignment.permissions,
            "resource_id": resource_id
        }

    @staticmethod
    async def get_staff_permissions(
        tenant_id: str,
        staff_id: str,
        resource_id: Optional[str] = None
    ) -> dict:
        """
        Get all permissions for staff member
        
        Args:
            tenant_id: Tenant ID
            staff_id: Staff member ID
            resource_id: Optional filter by specific resource
        
        Returns:
            Dict with staff permissions by resource
        """
        assignments = await StaffAssignmentRepository.get_by_staff_id(tenant_id, staff_id)
        
        permissions_map = {}
        for assignment in assignments:
            if assignment.is_active:
                if resource_id is None or assignment.resource_id == resource_id:
                    permissions_map[assignment.resource_id] = {
                        "role": assignment.staff_role,
                        "permissions": assignment.permissions,
                        "resource_type": assignment.assignment_type,
                        "resource_name": assignment.resource_name
                    }
        
        return permissions_map
