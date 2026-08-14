"""
Create or update an admin user for local/testing environments.

Usage:
  python -m scripts.create_admin admin@example.com StrongP@ssword

This script reads DB settings from `app.config` and will not write
secrets into the repository. Use carefully.
"""

import os
import sys
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


async def create_admin(email: str, password: str, role: str = "university_admin", client: Optional[AsyncIOMotorClient] = None) -> None:
    settings = get_settings()
    should_close = False
    if client is None:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        should_close = True
    db = client[settings.MONGODB_DB]

    await init_beanie(database=db, document_models=[User, Tenant])

    tenant = await Tenant.find_one({"subdomain": "test-university"})
    if not tenant:
        tenant = Tenant(
            name="Test University Ghana",
            subdomain="test-university",
            admin_email=email,
            country="Ghana",
        )
        await tenant.insert()
        print(f"Created tenant: {tenant.name} (id: {tenant.id})")
    tenant_id = str(tenant.id)

    try:
        role_enum = RoleEnum(role)
    except ValueError:
        raise ValueError(f"Invalid role: {role}")

    user = await User.find_one({"email": email})
    password_hash = pwd_context.hash(password)

    if not user:
        user = User(
            tenant_id=tenant_id,
            email=email,
            first_name="System",
            last_name="Admin",
            password_hash=password_hash,
            role=role_enum,
            is_active=True,
            is_verified=True,
        )
        await user.insert()
        print(f"Created {role} user: {email}")
    else:
        user.password_hash = password_hash
        user.tenant_id = tenant_id
        user.role = role_enum
        user.is_active = True
        user.is_verified = True
        await user.save()
        print(f"Updated existing user and set as {role}: {email}")

    if should_close:
        client.close()


async def run_main():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    try:
        if len(sys.argv) == 1:
            created = False
            if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
                await create_admin(settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD, "university_admin", client=client)
                created = True
            if settings.SUPER_ADMIN_EMAIL and settings.SUPER_ADMIN_PASSWORD:
                await create_admin(settings.SUPER_ADMIN_EMAIL, settings.SUPER_ADMIN_PASSWORD, "super_admin", client=client)
                created = True
            if not created:
                print("Usage: python -m scripts.create_admin email@example.com StrongPassword [role]")
                print("Or set ADMIN_EMAIL/ADMIN_PASSWORD and/or SUPER_ADMIN_EMAIL/SUPER_ADMIN_PASSWORD in .env")
                sys.exit(1)
        else:
            if len(sys.argv) not in (3, 4):
                print("Usage: python -m scripts.create_admin email@example.com StrongPassword [role]")
                sys.exit(1)

            email = sys.argv[1]
            password = sys.argv[2]
            role = sys.argv[3] if len(sys.argv) == 4 else "university_admin"
            await create_admin(email, password, role, client=client)
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(run_main())
