import pytest
from fastapi.testclient import TestClient
from app.application.auth.login import AuthService
from app.infrastructure.database.connection import init_db
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.models.user import RoleEnum, User
from app.main import app


class FakeUserRepo:
    def __init__(self, user):
        self.user = user

    async def get_by_email(self, email):
        return self.user

    async def increment_login_attempts(self, user_id):
        return None

    async def reset_login_attempts(self, user_id):
        return None

    async def update(self, user_id, data):
        for key, value in data.items():
            setattr(self.user, key, value)
        return self.user


@pytest.mark.asyncio
async def test_login_requires_password_reset_for_first_login_user():
    password = "UniversityAdmin@123"
    user = User(
        email="admin@test.edu",
        first_name="University",
        last_name="Admin",
        password_hash=AuthService.hash_password(password),
        role=RoleEnum.UNIVERSITY_ADMIN,
        tenant_id="tenant-1",
        must_change_password=True,
        is_active=True,
    )
    auth_service = AuthService(FakeUserRepo(user))

    access_token, refresh_token, auth_user = await auth_service.login("admin@test.edu", password)

    assert access_token is None
    assert refresh_token is None
    assert auth_user is not None
    assert auth_user.must_change_password is True


@pytest.mark.asyncio
async def test_login_allows_normal_user_without_force_reset():
    password = "StrongPassword@123"
    user = User(
        email="registrar@test.edu",
        first_name="Registrar",
        last_name="User",
        password_hash=AuthService.hash_password(password),
        role=RoleEnum.REGISTRAR,
        tenant_id="tenant-1",
        must_change_password=False,
        is_active=True,
    )
    auth_service = AuthService(FakeUserRepo(user))

    access_token, refresh_token, auth_user = await auth_service.login("registrar@test.edu", password)

    assert access_token is not None
    assert refresh_token is not None
    assert auth_user is not None
    assert auth_user.must_change_password is False


@pytest.mark.asyncio
async def test_super_admin_can_create_university_admin_for_tenant():
    await init_db()

    repo = UserRepository()
    email = "superadmin-create@test.edu"
    admin_email = "tenant-admin-create@test.edu"

    existing_admin = await repo.get_by_email(email)
    if existing_admin:
        await repo.delete(str(existing_admin.id))

    existing_user = await repo.get_by_email(admin_email)
    if existing_user:
        await repo.delete(str(existing_user.id))

    super_admin = await repo.create({
        "email": email,
        "first_name": "Super",
        "last_name": "Admin",
        "password_hash": AuthService.hash_password("StrongPass@123"),
        "role": RoleEnum.SUPER_ADMIN,
        "tenant_id": None,
        "permissions": [],
        "is_active": True,
        "must_change_password": False,
    })

    token = AuthService.create_access_token(str(super_admin.id), tenant_id=None)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/admin/users",
            json={
                "email": admin_email,
                "first_name": "Tenant",
                "last_name": "Admin",
                "password": "UniversityAdmin@2026",
                "role": "university_admin",
                "tenant_id": "tenant-123",
                "must_change_password": True,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == admin_email
    assert data["role"] == "university_admin"
    assert data["tenant_id"] == "tenant-123"
    assert data["must_change_password"] is True


@pytest.mark.asyncio
async def test_password_can_be_reset_without_auth_for_force_reset_users():
    await init_db()
    repo = UserRepository()
    email = "reset-without-auth@test.edu"
    existing = await repo.get_by_email(email)
    if existing:
        await repo.delete(str(existing.id))

    password = "UniversityAdmin@123"
    user = await repo.create({
        "email": email,
        "first_name": "Reset",
        "last_name": "User",
        "password_hash": AuthService.hash_password(password),
        "role": RoleEnum.UNIVERSITY_ADMIN,
        "tenant_id": "tenant-reset",
        "permissions": [],
        "is_active": True,
        "must_change_password": True,
    })

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "email": email,
                "current_password": password,
                "new_password": "NewPassword@456",
                "confirm_password": "NewPassword@456",
            },
        )

    assert response.status_code == 200

    updated_user = await repo.get_by_id(str(user.id))
    assert updated_user.must_change_password is False
    assert AuthService.verify_password("NewPassword@456", updated_user.password_hash) is True
