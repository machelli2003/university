"""
Resource Authorization Utilities
Helpers for integrating resource-level authorization into endpoints
Section 57: Resource-Level Authorization Integration
"""
from functools import wraps
from fastapi import HTTPException
from app.domain.authorization.resource_authorization_service import ResourceAuthorizationService


async def verify_resource_access(
    tenant_id: str,
    staff_id: str,
    resource_id: str,
    required_permission: str | None = None
) -> None:
    """
    Verify staff can access a resource
    Raises HTTPException 403 if unauthorized
    
    Usage:
        await verify_resource_access(
            tenant_id=current_user.get("tenant_id"),
            staff_id=current_user.get("user_id"),
            resource_id=department_id,
            required_permission="view_grades"
        )
    """
    can_access = await ResourceAuthorizationService.can_access_resource(
        tenant_id=tenant_id,
        staff_id=staff_id,
        resource_id=resource_id,
        required_permission=required_permission
    )
    
    if not can_access:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: No access to this resource"
        )


async def verify_resource_type_access(
    tenant_id: str,
    staff_id: str,
    resource_type: str,
    required_permission: str | None = None
) -> None:
    """
    Verify staff has assignment of a resource type
    Raises HTTPException 403 if unauthorized
    
    Usage:
        await verify_resource_type_access(
            tenant_id=current_user.get("tenant_id"),
            staff_id=current_user.get("user_id"),
            resource_type="DEPARTMENT",
            required_permission="manage_staff"
        )
    """
    can_access = await ResourceAuthorizationService.can_access_resource_type(
        tenant_id=tenant_id,
        staff_id=staff_id,
        resource_type=resource_type,
        required_permission=required_permission
    )
    
    if not can_access:
        raise HTTPException(
            status_code=403,
            detail=f"Unauthorized: No {resource_type} access"
        )


async def get_accessible_resources(
    tenant_id: str,
    staff_id: str,
    resource_type: str | None = None
) -> list[str]:
    """
    Get all resources accessible to staff member
    
    Usage:
        resources = await get_accessible_resources(
            tenant_id=current_user.get("tenant_id"),
            staff_id=current_user.get("user_id"),
            resource_type="COURSE"
        )
        # Filter data by these resources
        courses = await course_repo.get_by_ids(resources)
    """
    return await ResourceAuthorizationService.get_accessible_resources(
        tenant_id=tenant_id,
        staff_id=staff_id,
        resource_type=resource_type
    )


async def get_staff_permissions(
    tenant_id: str,
    staff_id: str,
    resource_id: str | None = None
) -> dict:
    """
    Get all permissions for staff member
    
    Usage:
        perms = await get_staff_permissions(
            tenant_id=current_user.get("tenant_id"),
            staff_id=current_user.get("user_id")
        )
        # Check specific permission
        can_edit = "edit_grades" in perms.get("resource_123", {}).get("permissions", [])
    """
    return await ResourceAuthorizationService.get_staff_permissions(
        tenant_id=tenant_id,
        staff_id=staff_id,
        resource_id=resource_id
    )
