from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from app.dependencies import require_roles, get_user_repo, get_auth_service
from app.infrastructure.models.user import User, RoleEnum
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.presentation.api.v1.auth.schemas import UserResponse
from app.presentation.api.v1.admin import schemas as admin_schemas

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
