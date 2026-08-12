from fastapi import APIRouter, HTTPException, status, Depends
from app.presentation.api.v1.auth.schemas import (
    LoginRequest, RegisterRequest, RefreshRequest,
    LoginResponse, RegisterResponse, UserResponse, TokenResponse
)
from app.application.auth.login import AuthService
from app.dependencies import get_current_user, get_auth_service
from app.infrastructure.models.user import User

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.register(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        password=request.password,
        role="applicant",
    )

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    return RegisterResponse(id=str(user.id), email=user.email)

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    access_token, refresh_token, user = await auth_service.login(request.email, request.password)

    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=str(user.id), email=user.email, first_name=user.first_name,
            last_name=user.last_name, age=user.age, role=user.role.value,
            permissions=user.permissions, is_active=user.is_active,
            is_verified=user.is_verified, created_at=user.created_at,
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id), email=current_user.email,
        first_name=current_user.first_name, last_name=current_user.last_name,
        age=current_user.age, role=current_user.role.value, permissions=current_user.permissions,
        is_active=current_user.is_active, is_verified=current_user.is_verified,
        created_at=current_user.created_at,
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest, auth_service: AuthService = Depends(get_auth_service)):
    result = await auth_service.refresh_access_token(request.refresh_token)

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token, refresh_token = result
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
