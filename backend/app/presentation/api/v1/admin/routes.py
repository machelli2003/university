from fastapi import APIRouter, Depends, HTTPException, status
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
    if current_user.role.value == "super_admin":
        users = await user_repo.get_users(tenant_id, include_inactive=include_inactive)
    else:
        users = await user_repo.get_users(current_user.tenant_id, include_inactive=include_inactive)
    return [
        UserResponse(
            id=str(u.id), tenant_id=u.tenant_id, email=u.email, first_name=u.first_name,
            last_name=u.last_name, age=u.age, role=u.role.value, permissions=u.permissions,
            is_active=u.is_active, is_verified=u.is_verified,
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
    if await user_repo.exists_by_email(request.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Normalize and validate role
    try:
        role = RoleEnum(request.role)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    user_data = {
        "tenant_id": request.tenant_id if current_user.role.value == "super_admin" and request.tenant_id else current_user.tenant_id,
        "email": request.email,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "age": request.age,
        "password_hash": auth_service.hash_password(request.password),
        "role": role,
        "permissions": request.permissions or [],
    }

    user = await user_repo.create(user_data)
    return UserResponse(
        id=str(user.id), tenant_id=user.tenant_id, email=user.email, first_name=user.first_name,
        last_name=user.last_name, age=user.age, role=user.role.value, permissions=user.permissions,
        is_active=user.is_active, is_verified=user.is_verified,
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
    tenant_id: str,
    current_user: User = Depends(require_roles("super_admin")),
    auth_service = Depends(get_auth_service),
    tenant_repo=Depends(get_tenant_repo),
    audit_repo=Depends(get_audit_repo),
):
    # Validate tenant exists
    tenant = await tenant_repo.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    # Create short-lived access token scoped to the tenant
    token = auth_service.create_access_token(str(current_user.id), tenant_id=tenant_id, expires_delta=timedelta(minutes=30))

    # Audit impersonation event
    await audit_repo.create({
        "tenant_id": tenant_id,
        "event_type": "impersonation_started",
        "entity_type": "tenant",
        "entity_id": tenant_id,
        "action": "impersonate_tenant",
        "performed_by": str(current_user.id),
        "details": {"impersonated_tenant": tenant_id},
    })

    return {"access_token": token, "expires_in": 60 * 30, "tenant_id": tenant_id}


@router.post("/impersonate/stop")
async def stop_impersonation(
    tenant_id: str | None = None,
    current_user: User = Depends(require_roles("super_admin")),
    audit_repo=Depends(get_audit_repo),
):
    # record end of impersonation
    await audit_repo.create({
        "tenant_id": tenant_id or current_user.tenant_id,
        "event_type": "impersonation_stopped",
        "entity_type": "tenant",
        "entity_id": tenant_id or current_user.tenant_id,
        "action": "stop_impersonation",
        "performed_by": str(current_user.id),
        "details": {"tenant_id": tenant_id},
    })

    # increment Redis metric if available
    try:
        settings = get_settings()
        r = Redis.from_url(settings.REDIS_URL)
        r.incr("impersonation:stopped")
    except Exception:
        pass

    return {"status": "stopped", "tenant_id": tenant_id}


@router.get("/impersonations")
async def list_impersonations(
    limit: int = 100,
    current_user: User = Depends(require_roles("super_admin")),
    audit_repo=Depends(get_audit_repo),
):
    # return recent impersonation audit events
    cursor = audit_repo.model.find({"event_type": {"$in": ["impersonation_started", "impersonation_stopped"]}}).sort("-created_at").limit(limit)
    docs = await cursor.to_list()
    return [
        {
            "event_type": d.event_type,
            "entity_id": getattr(d, "entity_id", None),
            "performed_by": getattr(d, "performed_by", None),
            "details": getattr(d, "details", {}),
            "created_at": d.created_at,
        }
        for d in docs
    ]


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
