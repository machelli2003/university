import pytest

from app.application.auth.login import AuthService


class FakeUserRepo:
    def __init__(self):
        self.users = {}

    async def exists_by_email(self, email):
        return email.lower() in self.users

    async def create(self, data):
        class User:
            pass

        user = User()
        user.id = f"user-{len(self.users)+1}"
        user.email = data["email"]
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.password_hash = data["password_hash"]
        user.role = data["role"]
        user.tenant_id = data.get("tenant_id")
        user.must_change_password = data.get("must_change_password", False)
        self.users[user.email.lower()] = user
        return user


@pytest.mark.asyncio
async def test_auth_service_register_can_force_password_reset():
    repo = FakeUserRepo()
    service = AuthService(repo)

    user = await service.register(
        email="newapplicant@test.com",
        first_name="Ada",
        last_name="Boateng",
        password="TempPass123!",
        role="applicant",
        tenant_id="tenant-123",
        must_change_password=True,
    )

    assert user is not None
    assert user.tenant_id == "tenant-123"
    assert user.must_change_password is True
