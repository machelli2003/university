import pytest
from types import SimpleNamespace
from fastapi.security import HTTPAuthorizationCredentials
from app.dependencies import get_current_user, require_roles
from app.application.auth.login import AuthService


class MockUser:
    def __init__(self, id_: str, role: str, tenant_id: str | None = None):
        self.id = id_
        self.role = type("R", (), {"value": role})()
        self.tenant_id = tenant_id
        self.is_active = True


class MockUserRepo:
    def __init__(self, user: MockUser | None):
        self.user = user

    async def get_by_id(self, user_id: str):
        if self.user and self.user.id == user_id:
            return self.user
        return None


class MockRequest:
    def __init__(self):
        self.state = SimpleNamespace()


@pytest.mark.asyncio
async def test_get_current_user_sets_request_state_for_super_admin_impersonation():
    auth_service = AuthService(MockUserRepo(None))
    user = MockUser(id_="super1", role="super_admin")
    token = auth_service.create_access_token(user.id, tenant_id="tenant123")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    request = MockRequest()

    current_user = await get_current_user(
        credentials=credentials,
        auth_service=auth_service,
        user_repo=MockUserRepo(user),
        request=request,
    )

    assert current_user.tenant_id == "tenant123"
    assert request.state.user_id == "super1"
    assert request.state.tenant_id == "tenant123"


@pytest.mark.asyncio
async def test_get_current_user_ignores_tenant_override_for_non_super_admin():
    auth_service = AuthService(MockUserRepo(None))
    user = MockUser(id_="user1", role="university_admin", tenant_id="tenant-origin")
    token = auth_service.create_access_token(user.id, tenant_id="tenant123")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    request = MockRequest()

    current_user = await get_current_user(
        credentials=credentials,
        auth_service=auth_service,
        user_repo=MockUserRepo(user),
        request=request,
    )

    assert current_user.tenant_id == "tenant-origin"
    assert request.state.tenant_id == "tenant-origin"
