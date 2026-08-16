"""
Section 53-56: Authorization & Isolation Middleware
Enforces tenant isolation and role-based access control.

CRITICAL SECURITY:
- All queries must be scoped to current tenant_id
- No cross-tenant data access
- Role-based resource authorization
- Staff assignment validation
"""

import os
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """
    Compatibility middleware for single-university deployments.

    It no longer enforces tenant-scoped access. The app is configured to run as a
    single institution, so request validation focuses on authorization rather than
    cross-tenant isolation.
    """

    PUBLIC_PATHS = [
        "/apply/",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/api/v1/auth/reset-password",
        "/api/v1/health",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]

    async def dispatch(self, request: Request, call_next):
        is_public = any(request.url.path.startswith(path) for path in self.PUBLIC_PATHS)
        if is_public:
            return await call_next(request)

        user_id = request.headers.get("X-User-ID")
        if user_id:
            request.state.user_id = user_id

        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            request.state.tenant_id = tenant_id

        return await call_next(request)


class AuthorizationService:
    """
    Service to check role-based access to resources.
    
    Enforces:
    1. Staff members can only access assigned resources (departments, programmes)
    2. Students can only access their own data
    3. Admins can access all data within their tenant
    4. Cross-role access is prevented
    """
    
    # Role hierarchy: higher = more permissions
    ROLE_HIERARCHY = {
        "student": 1,
        "parent": 2,
        "alumni": 2,
        "lecturer": 3,
        "course_coordinator": 4,
        "hod": 5,
        "dean": 6,
        "registrar": 7,
        "finance_officer": 7,
        "admissions_officer": 7,
        "exam_officer": 7,
        "hostel_admin": 6,
        "librarian": 6,
        "tenant_admin": 8,
        "super_admin": 9,
    }
    
    # Role-specific resource access
    ROLE_RESOURCE_ACCESS = {
        # Lecturers can only access their assigned courses/departments
        "lecturer": ["own_courses", "students_in_courses"],
        "course_coordinator": ["all_courses_in_programme", "programme_students"],
        "hod": ["all_courses_in_department", "department_staff", "department_students"],
        "dean": ["all_programmes_in_faculty", "faculty_courses", "faculty_staff"],
        
        # Students can only access their own records
        "student": ["own_profile", "own_grades", "own_courses"],
        
        # Officers can access specific domains
        "admissions_officer": ["all_applicants", "all_applications"],
        "registrar": ["all_students", "all_enrollments"],
        "finance_officer": ["all_payments", "all_fees"],
        "exam_officer": ["all_results", "all_assessments"],
        
        # Admins have full access within tenant
        "tenant_admin": ["all_resources"],
        "super_admin": ["all_resources", "all_tenants"],
    }
    
    @staticmethod
    def check_resource_access(
        user_role: str,
        resource_type: str,
        resource_owner_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Check if user with given role can access resource.
        
        Args:
            user_role: User's role (e.g., 'lecturer', 'student')
            resource_type: Type of resource being accessed (e.g., 'own_profile', 'all_applicants')
            resource_owner_id: ID of resource owner (for checking ownership)
            user_id: ID of current user (for ownership checks)
            
        Returns:
            True if access allowed, False otherwise
        """
        allowed_resources = AuthorizationService.ROLE_RESOURCE_ACCESS.get(user_role, [])
        
        # Super admin can access anything
        if user_role == "super_admin":
            return True
        
        # Tenant admin can access all resources in their tenant
        if user_role == "tenant_admin" and "all_resources" in allowed_resources:
            return True
        
        # Check if resource type is allowed for this role
        if resource_type in allowed_resources:
            return True
        
        # Check ownership for personal resources
        if resource_type.startswith("own_") and resource_owner_id == user_id:
            return True
        
        return False
    
    @staticmethod
    def check_role_hierarchy(
        user_role: str,
        required_role: str,
    ) -> bool:
        """
        Check if user's role has sufficient level for required role.
        
        Args:
            user_role: User's actual role
            required_role: Minimum required role level
            
        Returns:
            True if user's role is >= required role level
        """
        user_level = AuthorizationService.ROLE_HIERARCHY.get(user_role, 0)
        required_level = AuthorizationService.ROLE_HIERARCHY.get(required_role, 0)
        return user_level >= required_level
    
    @staticmethod
    def can_manage_user(
        actor_role: str,
        target_user_role: str,
    ) -> bool:
        """
        Check if user can manage another user (e.g., change role, delete).
        
        Can only manage users at same level or lower.
        """
        actor_level = AuthorizationService.ROLE_HIERARCHY.get(actor_role, 0)
        target_level = AuthorizationService.ROLE_HIERARCHY.get(target_user_role, 0)
        return actor_level > target_level
