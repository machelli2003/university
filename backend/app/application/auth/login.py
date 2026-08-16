from datetime import datetime, timedelta
from typing import Tuple, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.models.user import User
from app.config import get_settings
from app.infrastructure.database.repositories.token_repository import TokenRepository

import bcrypt
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("about", (), {"__version__": getattr(bcrypt, "__version__", "4.0.0")})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

class AuthService:
    def __init__(self, user_repo: UserRepository, token_repo: TokenRepository = None):
        self.user_repo = user_repo
        self.token_repo = token_repo

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    @staticmethod
    def create_access_token(user_id: str, tenant_id: Optional[str] = None, expires_delta: timedelta = None) -> str:
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

        expire = datetime.utcnow() + expires_delta
        payload = {"sub": user_id, "tenant_id": tenant_id, "exp": expire}
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: str, expires_delta: timedelta = None) -> str:
        if expires_delta is None:
            expires_delta = timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)

        expire = datetime.utcnow() + expires_delta
        payload = {"sub": user_id, "type": "refresh", "exp": expire}
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except JWTError:
            return None

    async def login(self, email: str, password: str) -> Tuple[Optional[str], Optional[str], Optional[User]]:
        normalized_email = (email or "").strip().lower()
        user = await self.user_repo.get_by_email(normalized_email)

        if not user or not self.verify_password(password, user.password_hash):
            if user:
                await self.user_repo.increment_login_attempts(str(user.id))
            return None, None, None

        if not user.is_active:
            return None, None, None

        if user.must_change_password:
            return None, None, user

        access_token = self.create_access_token(str(user.id), user.tenant_id)
        refresh_token = self.create_refresh_token(str(user.id))

        await self.user_repo.reset_login_attempts(str(user.id))
        await self.user_repo.update(str(user.id), {"last_login": datetime.utcnow()})

        return access_token, refresh_token, user

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> Optional[User]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        if current_password and not self.verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        if not new_password or len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters")

        if self.verify_password(new_password, user.password_hash):
            raise ValueError("New password must be different from the current password")

        await self.user_repo.update(str(user.id), {
            "password_hash": self.hash_password(new_password),
            "must_change_password": False,
            "updated_at": datetime.utcnow(),
        })
        user = await self.user_repo.get_by_id(user_id)
        return user

    async def register(
        self, email: str, first_name: str, last_name: str,
        password: str, role: str = "applicant", tenant_id: Optional[str] = None,
        must_change_password: bool = False
    ) -> Optional[User]:
        normalized_email = self.user_repo.normalize_email(email)
        if await self.user_repo.exists_by_email(normalized_email):
            return None

        user_data = {
            "tenant_id": tenant_id,
            "email": normalized_email,
            "first_name": first_name,
            "last_name": last_name,
            "password_hash": self.hash_password(password) if password else None,
            "role": role,
            "permissions": [],
            "must_change_password": must_change_password,
        }

        return await self.user_repo.create(user_data)

    async def refresh_access_token(self, refresh_token: str) -> Optional[Tuple[str, str]]:
        # check blacklist first
        if self.token_repo and await self.token_repo.is_blacklisted(refresh_token):
            return None

        payload = self.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        new_access = self.create_access_token(user_id, user.tenant_id)
        new_refresh = self.create_refresh_token(user_id)
        return new_access, new_refresh
