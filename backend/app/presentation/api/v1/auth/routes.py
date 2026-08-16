from fastapi import APIRouter, HTTPException, status, Depends
from app.presentation.api.v1.auth.schemas import (
    LoginRequest, RegisterRequest, RefreshRequest, ChangePasswordRequest,
    LoginResponse, RegisterResponse, UserResponse, TokenResponse,
    ApplicationFormLoginRequest, PermanentCredentialLoginRequest
)
from app.application.auth.login import AuthService
from app.dependencies import get_current_user, get_auth_service
from app.infrastructure.models.user import User
from fastapi import Body
import pyotp
import logging
from app.infrastructure.database.repositories.token_repository import TokenRepository
from app.infrastructure.database.repositories.application_form_repository import ApplicationFormRepository
from app.infrastructure.database.repositories.permanent_credential_repository import PermanentCredentialRepository
from app.infrastructure.models import ApplicationFormStatusEnum
from app.infrastructure.services.permanent_credential_service import PermanentCredentialService
from passlib.context import CryptContext

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        if user and getattr(user, "must_change_password", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Password reset required. Please change your password before continuing.",
                headers={"x-password-reset-required": "true"},
            )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=str(user.id), email=user.email, first_name=user.first_name,
            last_name=user.last_name, age=user.age, role=user.role.value,
            permissions=user.permissions, is_active=user.is_active,
            is_verified=user.is_verified, must_change_password=user.must_change_password,
            created_at=user.created_at,
        )
    )


@router.post("/login/application-form", response_model=LoginResponse, tags=["Application Form"])
async def login_with_application_form(
    request: ApplicationFormLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    app_form_repo: ApplicationFormRepository = Depends(lambda: ApplicationFormRepository()),
):
    """
    Login using PIN and Serial number from purchased application form.
    
    This is the Ghana university model where applicants must:
    1. Purchase an application form (get PIN and Serial)
    2. Login with PIN/Serial to access the application portal
    3. After successful login, create or update their applicant account
    """
    try:
        # Verify PIN and Serial are valid and unused
        app_form = await app_form_repo.get_active_by_pin_and_serial(
            request.pin,
            request.serial_number
        )
        
        if not app_form:
            logger.warning(f"Invalid/used PIN-Serial combination from {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid PIN or Serial number. Please verify and try again."
            )
        
        # Verify email matches (safety check)
        if app_form.applicant_email.lower() != request.email.lower():
            logger.warning(f"PIN-Serial email mismatch: form={app_form.applicant_email}, request={request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email does not match the application form purchase"
            )
        
        # Check if applicant already has an account
        existing_user = await auth_service.user_repo.get_by_email(request.email)
        
        if existing_user:
            # User exists, just login
            access_token, refresh_token, user = await auth_service.login(
                request.email,
                password="temp_pass"  # This will fail, so we handle it differently
            )
            
            # For PIN/serial login, we skip password and just create token
            from app.infrastructure.security.token_service import TokenService
            token_service = TokenService()
            access_token = token_service.create_access_token({"sub": str(existing_user.id)})
            refresh_token = token_service.create_refresh_token({"sub": str(existing_user.id)})
            
            user = existing_user
        else:
            # Create new applicant account
            user = await auth_service.register(
                email=request.email,
                first_name=request.first_name or app_form.first_name or "Applicant",
                last_name=request.last_name or app_form.last_name or "User",
                password=None,  # No password for PIN-based login
                role="applicant",
            )
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create account"
                )
            
            # Create tokens for new user
            from app.infrastructure.security.token_service import TokenService
            token_service = TokenService()
            access_token = token_service.create_access_token({"sub": str(user.id)})
            refresh_token = token_service.create_refresh_token({"sub": str(user.id)})
        
        # Mark application form as used
        app_form.status = ApplicationFormStatusEnum.USED
        app_form.applicant_id = str(user.id)
        from datetime import datetime
        app_form.used_at = datetime.utcnow()
        app_form.first_login_at = datetime.utcnow()
        app_form.last_login_at = datetime.utcnow()
        app_form.login_count = 1
        await app_form_repo.save(app_form)
        
        logger.info(f"Applicant {user.email} logged in using PIN-Serial from form {app_form.serial_number}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse(
                id=str(user.id), email=user.email, first_name=user.first_name,
                last_name=user.last_name, age=user.age, role=user.role.value,
                permissions=user.permissions, is_active=user.is_active,
                is_verified=user.is_verified, must_change_password=user.must_change_password,
                created_at=user.created_at,
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during PIN-Serial login: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login failed. Please try again."
        )


@router.post("/login/permanent-credential", response_model=LoginResponse, tags=["Authentication"])
async def login_with_permanent_credential(
    request: PermanentCredentialLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    cred_service: PermanentCredentialService = Depends(lambda: PermanentCredentialService()),
    cred_repo: PermanentCredentialRepository = Depends(lambda: PermanentCredentialRepository()),
):
    """
    Login using permanent credentials (issued after applicant acceptance).
    
    Applicants use this after they are OFFERED admission.
    They receive a username and temporary password.
    On first login, they must change the temporary password.
    """
    try:
        # Find credential by username
        credential = await cred_repo.get_by_username(request.username)
        
        if not credential:
            logger.warning(f"Login attempt with non-existent username: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not pwd_context.verify(request.password, credential.password_hash):
            logger.warning(f"Failed login attempt for username: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Check if credential is active
        if not credential.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This credential has been deactivated"
            )
        
        # Get or create the associated user account
        user = await auth_service.user_repo.get_by_id(credential.applicant_id)
        
        if not user:
            # Create user if doesn't exist
            user = await auth_service.register(
                email=credential.email,
                first_name=user.first_name if user else "Student",
                last_name=user.last_name if user else "User",
                password=None,
                role="student",
            )
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account"
                )
        
        # Create tokens
        from app.infrastructure.security.token_service import TokenService
        token_service = TokenService()
        access_token = token_service.create_access_token({"sub": str(user.id)})
        refresh_token = token_service.create_refresh_token({"sub": str(user.id)})
        
        # Track login
        from datetime import datetime
        credential.last_login_at = datetime.utcnow()
        await cred_repo.save(credential)
        
        logger.info(f"User {user.email} logged in with permanent credentials")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse(
                id=str(user.id), email=user.email, first_name=user.first_name,
                last_name=user.last_name, age=user.age, role=user.role.value,
                permissions=user.permissions, is_active=user.is_active,
                is_verified=user.is_verified, must_change_password=credential.password_change_required,
                created_at=user.created_at,
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during permanent credential login: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login failed. Please try again."
        )


@router.post("/change-temporary-password", tags=["Authentication"])
async def change_temporary_password(
    old_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    cred_service: PermanentCredentialService = Depends(lambda: PermanentCredentialService()),
    cred_repo: PermanentCredentialRepository = Depends(lambda: PermanentCredentialRepository()),
):
    """
    Change temporary password on first login with permanent credentials.
    
    Called after applicant logs in with temporary password.
    Must be called before applicant can access full system features.
    """
    try:
        # Get credential
        credential = await cred_repo.get_by_applicant_id(str(current_user.id))
        
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No permanent credential found for this user"
            )
        
        # Verify old password
        if not pwd_context.verify(old_password, credential.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Change password
        await cred_service.change_password(
            str(credential.id),
            old_password,
            new_password,
        )
        
        logger.info(f"User {current_user.email} changed temporary password")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing temporary password: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )



async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id), email=current_user.email,
        first_name=current_user.first_name, last_name=current_user.last_name,
        age=current_user.age, role=current_user.role.value, permissions=current_user.permissions,
        is_active=current_user.is_active, is_verified=current_user.is_verified,
        must_change_password=current_user.must_change_password,
        created_at=current_user.created_at,
    )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password and confirmation do not match")

    try:
        await auth_service.change_password(
            str(current_user.id),
            request.current_password,
            request.new_password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return {"message": "Password updated successfully. Please log in again with your new password."}


@router.post("/reset-password")
async def reset_password_without_auth(
    request: dict = Body(...),
    auth_service: AuthService = Depends(get_auth_service),
):
    email = (request.get("email") or "").strip().lower()
    current_password = request.get("current_password")
    new_password = request.get("new_password")
    confirm_password = request.get("confirm_password")

    if not email or not current_password or not new_password or not confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email, current password, new password, and confirmation are required")

    if new_password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password and confirmation do not match")

    user = await auth_service.user_repo.get_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not getattr(user, "must_change_password", False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password reset is not required for this account")

    try:
        await auth_service.change_password(str(user.id), current_password, new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return {"message": "Password updated successfully. Please log in again with your new password."}

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
