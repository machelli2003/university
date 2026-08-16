from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List, Optional
from datetime import datetime
from app.dependencies import require_roles, get_user_repo, get_auth_service
from app.config import get_settings
from redis import Redis
from app.dependencies import get_tenant_repo, get_audit_repo
from app.infrastructure.models.user import User, RoleEnum
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.presentation.api.v1.auth.schemas import UserResponse
from app.presentation.api.v1.admin import schemas as admin_schemas
from datetime import timedelta

router = APIRouter()


@router.get("/dashboard/stats")
async def get_admin_stats(
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
):
    return {
        "message": "Admin dashboard stats endpoint",
        "tenant_id": current_user.tenant_id,
    }


# --- User management endpoints for University Admin / Super Admin ---
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    tenant_id: Optional[str] = None,
    include_inactive: bool = False,
    user_repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
):
    # Single-university mode: tenant selection is disabled.
    if current_user.role.value == "super_admin":
        users = await user_repo.get_users(include_inactive=include_inactive)
    else:
        users = await user_repo.get_users(current_user.tenant_id, include_inactive=include_inactive)
        users = [
            u for u in users
            if str(getattr(u, "created_by", "")) == str(current_user.id)
        ]
    return [
        UserResponse(
            id=str(u.id), tenant_id=u.tenant_id, email=u.email, first_name=u.first_name,
            last_name=u.last_name, age=u.age, role=u.role.value, permissions=u.permissions,
            is_active=u.is_active, is_verified=u.is_verified,
            must_change_password=getattr(u, "must_change_password", False),
            login_attempts=u.login_attempts, locked_until=u.locked_until,
            created_at=u.created_at,
        )
        for u in users
    ]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: admin_schemas.AdminCreateUserRequest,
    user_repo: UserRepository = Depends(get_user_repo),
    auth_service = Depends(get_auth_service),
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
):
    normalized_email = user_repo.normalize_email(request.email)
    if await user_repo.exists_by_email(normalized_email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Normalize and validate role
    try:
        role = RoleEnum(request.role)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    is_forced_reset = request.must_change_password if request.must_change_password is not None else role == RoleEnum.UNIVERSITY_ADMIN

    user_data = {
        "tenant_id": current_user.tenant_id or "single-university",
        "email": normalized_email,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "age": request.age,
        "password_hash": auth_service.hash_password(request.password),
        "role": role,
        "permissions": request.permissions or [],
        "must_change_password": is_forced_reset,
        "created_by": str(current_user.id),
    }

    user = await user_repo.create(user_data)
    return UserResponse(
        id=str(user.id), tenant_id=user.tenant_id, email=user.email, first_name=user.first_name,
        last_name=user.last_name, age=user.age, role=user.role.value, permissions=user.permissions,
        is_active=user.is_active, is_verified=user.is_verified,
        must_change_password=getattr(user, "must_change_password", False),
        login_attempts=user.login_attempts, locked_until=user.locked_until,
        created_at=user.created_at,
    )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: admin_schemas.AdminUpdateUserRequest,
    user_repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
):
    user = await user_repo.get_by_id(user_id)
    if not user or (current_user.role.value != "super_admin" and user.tenant_id != current_user.tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = {}
    if request.first_name is not None:
        update_data["first_name"] = request.first_name
    if request.last_name is not None:
        update_data["last_name"] = request.last_name
    if request.age is not None:
        update_data["age"] = request.age
    if request.is_active is not None:
        update_data["is_active"] = request.is_active
    if request.role is not None:
        try:
            update_data["role"] = RoleEnum(request.role)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    if request.permissions is not None:
        update_data["permissions"] = request.permissions
    if request.login_attempts is not None:
        update_data["login_attempts"] = request.login_attempts
    if request.locked_until is not None:
        update_data["locked_until"] = request.locked_until

    await user_repo.update(user_id, update_data)
    user = await user_repo.get_by_id(user_id)
    return UserResponse(
        id=str(user.id), email=user.email, first_name=user.first_name,
        last_name=user.last_name, role=user.role.value, permissions=user.permissions,
        is_active=user.is_active, is_verified=user.is_verified, created_at=user.created_at,
    )


@router.patch("/users/{user_id}/unlock", response_model=UserResponse)
async def unlock_user(
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
):
    user = await user_repo.get_by_id(user_id)
    if not user or (current_user.role.value != "super_admin" and user.tenant_id != current_user.tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = {
        "login_attempts": 0,
        "locked_until": None,
        "is_active": True,
    }
    await user_repo.update(user_id, update_data)
    user = await user_repo.get_by_id(user_id)
    return UserResponse(
        id=str(user.id), email=user.email, first_name=user.first_name,
        last_name=user.last_name, role=user.role.value, permissions=user.permissions,
        is_active=user.is_active, is_verified=user.is_verified, created_at=user.created_at,
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
):
    user = await user_repo.get_by_id(user_id)
    if not user or (current_user.role.value != "super_admin" and user.tenant_id != current_user.tenant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await user_repo.delete(user_id)
    return None


@router.post("/impersonate")
async def impersonate_tenant(
    current_user: User = Depends(require_roles("super_admin")),
):
    return {
        "status": "disabled",
        "message": "Tenant impersonation is disabled in single-university mode.",
        "user_id": str(current_user.id),
    }


@router.post("/impersonate/stop")
async def stop_impersonation(
    current_user: User = Depends(require_roles("super_admin")),
):
    return {
        "status": "stopped",
        "message": "Single-university mode does not use impersonation.",
        "user_id": str(current_user.id),
    }


@router.get("/impersonations")
async def list_impersonations(
    current_user: User = Depends(require_roles("super_admin")),
):
    return {
        "status": "disabled",
        "message": "Tenant impersonation is disabled in single-university mode.",
        "user_id": str(current_user.id),
    }


# --- Staff Role Management ---
@router.patch("/users/{user_id}/staff/role")
async def change_staff_role(
    user_id: str,
    request: admin_schemas.ChangeStaffRoleRequest,
    user_repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    audit_repo=Depends(get_audit_repo),
):
    """
    Change a staff member's role.
    
    Only university_admin and super_admin can change staff roles.
    Super admin can change roles across tenants.
    University admin can only change roles within their own tenant.
    """
    # Get the user to be updated
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Enforce tenant isolation - university admin cannot change roles in other tenants
    if current_user.role.value == "university_admin" and user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify staff in another tenant")
    
    # Validate the new role
    try:
        new_role = RoleEnum(request.new_role)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role: {request.new_role}")
    
    # Prevent role demotion/escalation violations
    # University admin cannot grant super_admin or university_admin roles
    if current_user.role.value == "university_admin" and new_role.value in ("super_admin", "university_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="University admin cannot assign super_admin or university_admin roles"
        )
    
    # Store old role for audit
    old_role = user.role.value if user.role else None
    
    # Update the user's role and permissions
    update_data = {
        "role": new_role,
        "permissions": request.permissions or []
    }
    
    await user_repo.update(user_id, update_data)
    
    # Audit the role change
    try:
        await audit_repo.create({
            "tenant_id": user.tenant_id,
            "event_type": "staff_role_changed",
            "entity_type": "user",
            "entity_id": user_id,
            "action": "change_staff_role",
            "performed_by": str(current_user.id),
            "details": {
                "user_email": user.email,
                "old_role": old_role,
                "new_role": request.new_role,
                "permissions": request.permissions or [],
                "reason": request.reason or "Role modification",
            },
        })
    except Exception:
        pass  # Non-blocking audit failure
    
    # Fetch updated user for response
    updated_user = await user_repo.get_by_id(user_id)
    return UserResponse(
        id=str(updated_user.id),
        tenant_id=updated_user.tenant_id,
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        age=updated_user.age,
        role=updated_user.role.value,
        permissions=updated_user.permissions,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        login_attempts=updated_user.login_attempts,
        locked_until=updated_user.locked_until,
        created_at=updated_user.created_at,
    )


@router.get("/users/{user_id}/staff/permissions")
async def get_staff_permissions(
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
):
    """Get current permissions for a staff member"""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Enforce tenant isolation
    if current_user.role.value == "university_admin" and user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view staff in another tenant")
    
    return {
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role.value if user.role else None,
        "permissions": user.permissions or [],
        "is_active": user.is_active,
    }


@router.post("/users/{user_id}/staff/permissions")
async def add_permission_to_staff(
    user_id: str,
    request: admin_schemas.AddPermissionRequest,
    user_repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    audit_repo=Depends(get_audit_repo),
):
    """Add additional permission to staff member"""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Enforce tenant isolation
    if current_user.role.value == "university_admin" and user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify staff in another tenant")
    
    # Add permission if not already present
    permissions = user.permissions or []
    if request.permission not in permissions:
        permissions.append(request.permission)
        await user_repo.update(user_id, {"permissions": permissions})
    
    # Audit permission addition
    try:
        await audit_repo.create({
            "tenant_id": user.tenant_id,
            "event_type": "permission_added",
            "entity_type": "user",
            "entity_id": user_id,
            "action": "add_permission",
            "performed_by": str(current_user.id),
            "details": {
                "user_email": user.email,
                "permission": request.permission,
                "reason": request.reason or "Permission grant",
            },
        })
    except Exception:
        pass  # Non-blocking audit failure
    
    return {
        "user_id": str(user.id),
        "email": user.email,
        "permissions": permissions,
        "message": f"Permission '{request.permission}' added successfully"
    }


@router.delete("/users/{user_id}/staff/permissions/{permission}")
async def remove_permission_from_staff(
    user_id: str,
    permission: str,
    user_repo: UserRepository = Depends(get_user_repo),
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    audit_repo=Depends(get_audit_repo),
):
    """Remove permission from staff member"""
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Enforce tenant isolation
    if current_user.role.value == "university_admin" and user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify staff in another tenant")
    
    # Remove permission if present
    permissions = user.permissions or []
    if permission in permissions:
        permissions.remove(permission)
        await user_repo.update(user_id, {"permissions": permissions})
    
    # Audit permission removal
    try:
        await audit_repo.create({
            "tenant_id": user.tenant_id,
            "event_type": "permission_removed",
            "entity_type": "user",
            "entity_id": user_id,
            "action": "remove_permission",
            "performed_by": str(current_user.id),
            "details": {
                "user_email": user.email,
                "permission": permission,
            },
        })
    except Exception:
        pass  # Non-blocking audit failure
    
    return {
        "user_id": str(user.id),
        "email": user.email,
        "permissions": permissions,
        "message": f"Permission '{permission}' removed successfully"
    }


# ==================== ITEM 63: IMPERSONATION ====================

@router.post("/users/{target_user_id}/impersonate/start")
async def start_impersonation(
    target_user_id: str,
    reason: str,
    current_user: User = Depends(require_roles("super_admin")),
    user_repo: UserRepository = Depends(get_user_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    Start impersonating a user (admin support/investigation).
    
    Item 63: Impersonation
    - Only super admins can impersonate
    - Returns a short-lived impersonation token
    - All actions during impersonation are audited
    - Original admin is logged as the actual performer
    """
    from app.application.admin.impersonation import ImpersonationUseCase
    from app.domain.security.token_service import TokenService
    
    if current_user.role.value != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can impersonate users"
        )
    
    # Initialize token service (inject properly in production)
    from app.config import get_settings
    settings = get_settings()
    token_service = TokenService(settings.JWT_SECRET_KEY)
    
    # Create impersonation use case
    use_case = ImpersonationUseCase(
        user_repo=user_repo,
        audit_repo=audit_repo,
        token_service=token_service,
        impersonation_ttl_minutes=30,
    )
    
    try:
        result = await use_case.start_impersonation(
            target_user_id=target_user_id,
            impersonating_admin_id=str(current_user.id),
            tenant_id=str(current_user.tenant_id),
            reason=reason,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/impersonation/{impersonation_id}/stop")
async def stop_impersonation(
    impersonation_id: str,
    current_user: User = Depends(require_roles("super_admin")),
    audit_repo=Depends(get_audit_repo),
):
    """End an active impersonation session."""
    from app.application.admin.impersonation import ImpersonationUseCase
    from app.domain.security.token_service import TokenService
    from app.config import get_settings
    
    settings = get_settings()
    token_service = TokenService(settings.JWT_SECRET_KEY)
    
    user_repo = await get_user_repo()
    use_case = ImpersonationUseCase(
        user_repo=user_repo,
        audit_repo=audit_repo,
        token_service=token_service,
    )
    
    try:
        result = await use_case.end_impersonation(
            impersonation_id=impersonation_id,
            impersonating_admin_id=str(current_user.id),
            tenant_id=str(current_user.tenant_id),
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/impersonations/active")
async def list_active_impersonations(
    current_user: User = Depends(require_roles("super_admin")),
    audit_repo=Depends(get_audit_repo),
):
    """List active impersonation sessions."""
    from app.application.admin.impersonation import ImpersonationUseCase
    from app.domain.security.token_service import TokenService
    from app.config import get_settings
    
    settings = get_settings()
    token_service = TokenService(settings.JWT_SECRET_KEY)
    
    user_repo = await get_user_repo()
    use_case = ImpersonationUseCase(
        user_repo=user_repo,
        audit_repo=audit_repo,
        token_service=token_service,
    )
    
    result = await use_case.get_active_impersonations(
        tenant_id=str(current_user.tenant_id),
    )
    return result


# ==================== ITEM 64: SETUP COMPLETENESS ENGINE ====================

@router.get("/setup/completeness-check")
async def check_setup_completeness(
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    tenant_repo=Depends(get_tenant_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    Check if university setup is complete.
    
    Item 64: Setup Completeness Engine
    Validates mandatory configurations before university can be activated.
    Returns completion percentage and list of blocking issues.
    """
    from app.application.admin.setup_completeness import SetupCompletenessEngine
    from app.dependencies import (
        get_programme_repo, get_faculty_repo, get_course_repo,
        get_admission_cycle_repo, get_accommodation_repo
    )
    
    # Initialize dependencies
    programme_repo = await get_programme_repo()
    faculty_repo = await get_faculty_repo()
    course_repo = await get_course_repo()
    admission_repo = await get_admission_cycle_repo()
    accommodation_repo = await get_accommodation_repo()
    
    engine = SetupCompletenessEngine(
        tenant_repo=tenant_repo,
        programme_repo=programme_repo,
        faculty_repo=faculty_repo,
        course_repo=course_repo,
        user_repo=await get_user_repo(),
        admission_repo=admission_repo,
        accommodation_repo=accommodation_repo,
    )
    
    try:
        result = await engine.check_setup_completeness(
            tenant_id=str(current_user.tenant_id),
        )
        
        # Audit the check
        await audit_repo.create({
            "tenant_id": str(current_user.tenant_id),
            "event_type": "setup_completeness_check",
            "entity_type": "tenant",
            "entity_id": str(current_user.tenant_id),
            "action": "check_setup",
            "performed_by": str(current_user.id),
            "details": {
                "completion_percentage": result["completion_percentage"],
                "is_complete": result["is_complete"],
            },
        })
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/setup/activate")
async def activate_university(
    current_user: User = Depends(require_roles("super_admin")),
    tenant_repo=Depends(get_tenant_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    Activate university (only after setup is complete).
    
    Must be called by super admin after all setup checks pass.
    Prevents activation if blocking issues exist.
    """
    from app.application.admin.setup_completeness import SetupCompletenessEngine
    from app.dependencies import (
        get_programme_repo, get_faculty_repo, get_course_repo,
        get_admission_cycle_repo, get_accommodation_repo
    )
    
    if current_user.role.value != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can activate universities"
        )
    
    # Check completeness first
    programme_repo = await get_programme_repo()
    faculty_repo = await get_faculty_repo()
    course_repo = await get_course_repo()
    admission_repo = await get_admission_cycle_repo()
    accommodation_repo = await get_accommodation_repo()
    
    engine = SetupCompletenessEngine(
        tenant_repo=tenant_repo,
        programme_repo=programme_repo,
        faculty_repo=faculty_repo,
        course_repo=course_repo,
        user_repo=await get_user_repo(),
        admission_repo=admission_repo,
        accommodation_repo=accommodation_repo,
    )
    
    completeness = await engine.check_setup_completeness(
        tenant_id=str(current_user.tenant_id),
    )
    
    if not completeness["is_complete"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot activate: {', '.join(completeness['blocking_issues'])}",
        )
    
    # Activate the tenant
    tenant = await tenant_repo.get_by_id(str(current_user.tenant_id))
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Update activation status
    tenant.is_active = True
    tenant.activated_at = datetime.utcnow()
    await tenant_repo.update(str(tenant.id), tenant)
    
    # Audit activation
    await audit_repo.create({
        "tenant_id": str(current_user.tenant_id),
        "event_type": "university_activated",
        "entity_type": "tenant",
        "entity_id": str(current_user.tenant_id),
        "action": "activate_university",
        "performed_by": str(current_user.id),
        "details": {
            "completion_percentage": completeness["completion_percentage"],
        },
    })
    
    return {
        "status": "success",
        "message": "University activated successfully",
        "tenant_id": str(current_user.tenant_id),
        "activated_at": datetime.utcnow().isoformat(),
    }


# ==================== ITEM 65: MODULE ENABLEMENT ====================

@router.get("/modules")
async def list_modules(
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    tenant_repo=Depends(get_tenant_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    List enabled/disabled modules for the tenant.
    
    Item 65: Module Enablement
    Allows checking which features are available.
    """
    from app.application.admin.module_enablement import ModuleEnablementService
    
    service = ModuleEnablementService(
        tenant_repo=tenant_repo,
        audit_repo=audit_repo,
    )
    
    try:
        result = await service.get_enabled_modules(
            tenant_id=str(current_user.tenant_id),
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/modules/{module_name}/enable")
async def enable_module(
    module_name: str,
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    tenant_repo=Depends(get_tenant_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    Enable a module for the tenant.
    
    Also enables required dependencies automatically.
    """
    from app.application.admin.module_enablement import ModuleEnablementService
    
    service = ModuleEnablementService(
        tenant_repo=tenant_repo,
        audit_repo=audit_repo,
    )
    
    try:
        result = await service.enable_module(
            tenant_id=str(current_user.tenant_id),
            module_name=module_name,
            admin_id=str(current_user.id),
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/modules/{module_name}/disable")
async def disable_module(
    module_name: str,
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    tenant_repo=Depends(get_tenant_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    Disable a module for the tenant.
    
    Also disables dependent modules automatically.
    """
    from app.application.admin.module_enablement import ModuleEnablementService
    
    service = ModuleEnablementService(
        tenant_repo=tenant_repo,
        audit_repo=audit_repo,
    )
    
    try:
        result = await service.disable_module(
            tenant_id=str(current_user.tenant_id),
            module_name=module_name,
            admin_id=str(current_user.id),
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
