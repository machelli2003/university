from fastapi import APIRouter, HTTPException, status, Depends
from app.presentation.api.v1.auth.schemas import (
    LoginRequest, RegisterRequest, RefreshRequest,
    LoginResponse, RegisterResponse, UserResponse, TokenResponse
)
from app.application.auth.login import AuthService
from app.dependencies import get_current_user, get_auth_service
from app.infrastructure.models.user import User
from fastapi import Body
import pyotp
from app.infrastructure.database.repositories.token_repository import TokenRepository

_token_repo = TokenRepository()

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


@router.post("/token/rotate", response_model=TokenResponse)
async def rotate_token(
    request: RefreshRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Item 75: Refresh Token Rotation
    
    Rotate refresh token for improved security.
    - Old refresh token is immediately invalidated
    - New refresh token is issued
    - Prevents token replay attacks
    """
    from app.infrastructure.security.token_rotation import RefreshTokenRotationService
    
    service = RefreshTokenRotationService()
    
    try:
        result = await service.rotate_token(
            user_id=str(current_user.id),
            old_refresh_token=request.refresh_token,
        )
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/revoke", response_model=dict)
async def revoke_token(token: dict = Body(...)):
    """Revoke/blacklist a refresh token (logout)."""
    refresh_token = token.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="refresh_token required")

    await _token_repo.blacklist(refresh_token, reason="user_revoked")
    return {"status": "success", "message": "Token revoked"}


@router.post("/mfa/setup", response_model=dict)
async def mfa_setup(current_user: User = Depends(get_current_user)):
    """Generate a TOTP secret and return provisioning URI."""
    secret = pyotp.random_base32()
    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=current_user.email, issuer_name="UniversityPlatform")
    # store secret in user profile (must be verified to enable)
    from app.infrastructure.database.repositories.user_repository import UserRepository
    repo = UserRepository()
    await repo.update(str(current_user.id), {"mfa_secret": secret})
    return {"secret": secret, "provisioning_uri": provisioning_uri}


@router.post("/mfa/verify", response_model=dict)
async def mfa_verify(code: dict = Body(...), current_user: User = Depends(get_current_user)):
    token = code.get("token")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="token required")

    if not current_user.mfa_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA not setup")

    totp = pyotp.TOTP(current_user.mfa_secret)
    if totp.verify(token):
        from app.infrastructure.database.repositories.user_repository import UserRepository
        repo = UserRepository()
        await repo.update(str(current_user.id), {"mfa_enabled": True})
        return {"verified": True}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
