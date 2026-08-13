"""
Example: Resource-Level Authorization Integration
Shows how to integrate resource-level authorization checks into endpoints
Section 57: Resource Authorization Pattern Example

This example demonstrates how to add resource-level authorization checks
to a real endpoint that needs to verify staff can access department resources.

USAGE PATTERN:
1. Import the authorization utilities
2. Call verify_resource_access before processing the request
3. Filter/return only authorized resources
"""

from fastapi import APIRouter, HTTPException, Depends
from app.dependencies import get_current_user
from app.domain.authorization.resource_auth_utils import (
    verify_resource_access,
    get_accessible_resources,
    get_staff_permissions,
)

# Example router
router = APIRouter(prefix="/api/v1/example", tags=["example"])


@router.get("/departments/{department_id}/staff")
async def get_department_staff(
    department_id: str,
    current_user = Depends(get_current_user)
):
    """
    Example: Get staff for a department (with resource-level authorization)
    
    PATTERN:
    1. Verify user can access this department resource
    2. Return department staff if authorized, else 403
    """
    tenant_id = current_user.get("tenant_id")
    staff_id = current_user.get("user_id")
    
    # RESOURCE-LEVEL AUTHORIZATION CHECK
    # This verifies the current user has assignment to this department
    # and has permission to view staff in this department
    await verify_resource_access(
        tenant_id=tenant_id,
        staff_id=staff_id,
        resource_id=department_id,
        required_permission="view_staff"  # Optional: check specific permission
    )
    
    # If we get here, user is authorized
    # Fetch and return department staff
    # (Database call would go here)
    return {
        "department_id": department_id,
        "staff": [
            {"id": "s1", "name": "Dr. Smith"},
            {"id": "s2", "name": "Prof. Johnson"}
        ]
    }


@router.get("/courses")
async def list_courses(current_user = Depends(get_current_user)):
    """
    Example: List only courses user can access
    
    PATTERN:
    1. Get all resources of type COURSE that user can access
    2. Filter database results by these resource IDs
    3. Return only authorized courses
    """
    tenant_id = current_user.get("tenant_id")
    staff_id = current_user.get("user_id")
    
    # Get all COURSE resources accessible to this user
    accessible_course_ids = await get_accessible_resources(
        tenant_id=tenant_id,
        staff_id=staff_id,
        resource_type="COURSE"
    )
    
    if not accessible_course_ids:
        return {"courses": []}
    
    # Filter database query by accessible course IDs
    # (Database call would go here)
    # courses = await course_repo.get_by_ids(accessible_course_ids)
    
    return {
        "courses": [
            {"id": accessible_course_ids[0], "name": "Data Structures"},
        ]
    }


@router.get("/dashboard")
async def get_personalized_dashboard(current_user = Depends(get_current_user)):
    """
    Example: Get personalized dashboard with only accessible resources
    
    PATTERN:
    1. Get all permissions for the user
    2. Build dashboard based on assigned resources and roles
    3. Return only data user can see
    """
    tenant_id = current_user.get("tenant_id")
    staff_id = current_user.get("user_id")
    
    # Get all permissions and resource assignments for user
    permissions = await get_staff_permissions(
        tenant_id=tenant_id,
        staff_id=staff_id
    )
    
    # permissions will look like:
    # {
    #   "dept_123": {
    #     "role": "head_of_department",
    #     "permissions": ["view_grades", "edit_course", ...],
    #     "resource_type": "DEPARTMENT",
    #     "resource_name": "Computer Science"
    #   },
    #   "course_456": {
    #     "role": "lecturer",
    #     "permissions": ["view_students", "submit_grades", ...],
    #     "resource_type": "COURSE",
    #     "resource_name": "Data Structures"
    #   }
    # }
    
    # Build dashboard based on these permissions
    dashboard_data = {
        "assigned_resources": permissions,
        "total_resources": len(permissions),
        "roles": list(set(p.get("role") for p in permissions.values())),
        "actions_available": []
    }
    
    # Add available actions based on permissions
    for resource_id, perms in permissions.items():
        if "edit_course" in perms.get("permissions", []):
            dashboard_data["actions_available"].append(f"Can edit {resource_id}")
    
    return dashboard_data


"""
INTEGRATION CHECKLIST:

When adding resource-level authorization to an endpoint:

1. ✓ Import authorization utilities:
   from app.domain.authorization.resource_auth_utils import verify_resource_access

2. ✓ Extract tenant and staff IDs from current_user:
   tenant_id = current_user.get("tenant_id")
   staff_id = current_user.get("user_id")

3. ✓ Call appropriate authorization check:
   - verify_resource_access(tenant_id, staff_id, resource_id)
   - verify_resource_type_access(tenant_id, staff_id, resource_type)
   - get_accessible_resources(tenant_id, staff_id, resource_type)

4. ✓ Use authorized resources to filter database queries

5. ✓ Return 403 automatically on unauthorized (HTTPException raised by check)

PERMISSION STRINGS CONVENTION:
- view_* : Read access
- create_* : Create access
- edit_* : Update access
- delete_* : Delete access
- manage_* : Full administrative access

ASSIGNMENT TYPES:
- DEPARTMENT : Assigned to department
- FACULTY : Assigned to faculty/school
- PROGRAMME : Assigned to degree programme
- COURSE : Assigned to course
- HOSTEL : Assigned to hostel
- CUSTOM : Custom resource assignment
"""
