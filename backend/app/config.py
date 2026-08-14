import os
from pydantic_settings import BaseSettings
from typing import List, Optional

ENV_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority"
    MONGODB_DB: str = "eump_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30
    JWT_REFRESH_EXPIRATION_DAYS: int = 7

    # Admin credentials (for local/dev seeding only)
    ADMIN_EMAIL: Optional[str] = None
    ADMIN_PASSWORD: Optional[str] = None
    SUPER_ADMIN_EMAIL: Optional[str] = None
    SUPER_ADMIN_PASSWORD: Optional[str] = None

    # Paystack (Test Keys)
    PAYSTACK_PUBLIC_KEY: str = "pk_test_..."
    PAYSTACK_SECRET_KEY: str = "sk_test_..."

    # Email provider
    EMAIL_PROVIDER: str = "stub"
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    EMAIL_FROM_ADDRESS: Optional[str] = None

    # SMS provider
    SMS_PROVIDER: str = "stub"
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None

    # File storage provider
    FILE_STORAGE_PROVIDER: str = "stub"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_S3_REGION: Optional[str] = None
    AWS_S3_ENDPOINT_URL: Optional[str] = None

    # WAEC / Exam verification API
    WAEC_API_ENABLED: bool = False
    WAEC_API_BASE_URL: Optional[str] = None
    WAEC_API_KEY: Optional[str] = None

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://eump-frontend.onrender.com"
    ]

    # Celery
    CELERY_BROKER: str = "redis://localhost:6379/1"
    CELERY_BACKEND: str = "redis://localhost:6379/2"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ENV_FILE_PATH

    def production_checks(self) -> None:
        if self.ENVIRONMENT == "production":
            if not self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("JWT_SECRET_KEY must be set and at least 32 characters for production")

            if self.EMAIL_PROVIDER == "smtp":
                if not self.SMTP_HOST or not self.SMTP_PORT or not self.EMAIL_FROM_ADDRESS:
                    raise ValueError("SMTP_HOST, SMTP_PORT and EMAIL_FROM_ADDRESS must be configured for SMTP email provider")

            if self.SMS_PROVIDER == "twilio":
                if not self.TWILIO_ACCOUNT_SID or not self.TWILIO_AUTH_TOKEN or not self.TWILIO_FROM_NUMBER:
                    raise ValueError("TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER must be configured for Twilio SMS provider")

            if self.FILE_STORAGE_PROVIDER == "s3":
                if not self.AWS_ACCESS_KEY_ID or not self.AWS_SECRET_ACCESS_KEY or not self.AWS_S3_BUCKET or not self.AWS_S3_REGION:
                    raise ValueError("AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET and AWS_S3_REGION must be configured for S3 storage provider")

            if self.WAEC_API_ENABLED:
                if not self.WAEC_API_BASE_URL or not self.WAEC_API_KEY:
                    raise ValueError("WAEC_API_BASE_URL and WAEC_API_KEY must be configured when WAEC_API_ENABLED is true")

            if not self.MONGODB_URL:
                raise ValueError("MONGODB_URL must be configured")

            if not self.REDIS_URL:
                raise ValueError("REDIS_URL must be configured")

            if not self.ALLOWED_ORIGINS:
                raise ValueError("ALLOWED_ORIGINS must include at least one allowed origin")

            if self.ENVIRONMENT == "production" and self.DEBUG:
                raise ValueError("DEBUG must be false in production")


def get_settings() -> Settings:
    settings = Settings()
    settings.production_checks()
    return settings
