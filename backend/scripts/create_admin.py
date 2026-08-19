"""
Create or update the platform super admin user.

Usage:
  python -m scripts.create_admin superadmin@example.com StrongP@ssword

This script reads DB settings from `app.config` and will not write
secrets into the repository. Use carefully.
"""

import os
import sys
import certifi
from typing import Optional

# Ensure backend directory is on Python path regardless of execution location
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from passlib.context import CryptContext

from app.config import get_settings
from app.infrastructure.models.user import User, RoleEnum
from app.infrastructure.models.tenant import Tenant

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin(email: str, password: str, client: Optional[AsyncIOMotorClient] = None) -> None:
    settings = get_settings()
    should_close = False
    if client is None:
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=True,
        )
        should_close = True
    db = client[settings.MONGODB_DB]

    await init_beanie(database=db, document_models=[User, Tenant])

    role_enum = RoleEnum("super_admin")
    user = await User.find_one({"email": email})
    password_hash = pwd_context.hash(password)

    if not user:
        user = User(
            tenant_id="single-university",
            email=email,
            first_name="Platform",
            last_name="Admin",
            password_hash=password_hash,
            role=role_enum,
            is_active=True,
            is_verified=True,
        )
        await user.insert()
        print(f"Created platform super admin: {email}")
    else:
        user.password_hash = password_hash
        user.tenant_id = "single-university"
        user.role = role_enum
        user.is_active = True
        user.is_verified = True
        await user.save()
        print(f"Updated existing platform super admin: {email}")

    if should_close:
        client.close()


async def run_main():
    settings = get_settings()
    client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=20000,
        tlsAllowInvalidCertificates=True,
    )
    try:
        if len(sys.argv) == 1:
            if settings.SUPER_ADMIN_EMAIL and settings.SUPER_ADMIN_PASSWORD:
                await create_admin(settings.SUPER_ADMIN_EMAIL, settings.SUPER_ADMIN_PASSWORD, client=client)
            else:
                print("Usage: python -m scripts.create_admin superadmin@example.com StrongPassword")
                print("Or set SUPER_ADMIN_EMAIL/SUPER_ADMIN_PASSWORD in .env")
                sys.exit(1)
        else:
            if len(sys.argv) != 3:
                print("Usage: python -m scripts.create_admin superadmin@example.com StrongPassword")
                sys.exit(1)

            email = sys.argv[1]
            password = sys.argv[2]
            await create_admin(email, password, client=client)
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(run_main())
