"""
Pytest configuration and fixtures for test suite.
Provides authentication helpers, test clients, and mock data.
"""

import pytest
import os
from datetime import datetime, timedelta
from httpx import AsyncClient
from fastapi.testclient import TestClient
from jose import jwt
from app.main import app
from app.config import get_settings

settings = get_settings()

# ==================== JWT TOKEN GENERATION ====================

def create_test_token(user_id: str, email: str, role: str, tenant_id: str) -> str:
    """
    Create a valid JWT token for testing.
    
    Args:
        user_id: User ID
        email: User email
        role: User role (student, lecturer, admin, etc.)
        tenant_id: Tenant ID for multi-tenancy
    
    Returns:
        JWT token string
    """
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "tenant_id": tenant_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm="HS256"
    )
    return token


def get_auth_headers(user_id: str = "test-user-123", 
                     email: str = "test@test.com",
                     role: str = "student",
                     tenant_id: str = "test-tenant") -> dict:
    """
    Get Authorization headers with valid JWT token.
    
    Returns:
        Dict with Authorization header ready for requests
    """
    token = create_test_token(user_id, email, role, tenant_id)
    return {
        "Authorization": f"Bearer {token}",
        "X-User-ID": user_id,
        "X-Tenant-ID": tenant_id,
    }


# ==================== TEST FIXTURES ====================

@pytest.fixture
async def async_client():
    """Async HTTP client for tests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def authenticated_client():
    """Async HTTP client with authentication headers."""
    headers = get_auth_headers()
    async with AsyncClient(
        app=app,
        base_url="http://test",
        headers=headers
    ) as client:
        yield client


@pytest.fixture
def test_headers():
    """Standard test authentication headers."""
    return get_auth_headers()


@pytest.fixture
def admin_headers():
    """Admin authentication headers."""
    return get_auth_headers(
        user_id="admin-123",
        email="admin@test.com",
        role="super_admin",
        tenant_id="test-tenant"
    )


@pytest.fixture
def officer_headers():
    """Admissions officer authentication headers."""
    return get_auth_headers(
        user_id="officer-123",
        email="officer@test.com",
        role="admissions_officer",
        tenant_id="test-tenant"
    )


@pytest.fixture
def lecturer_headers():
    """Lecturer authentication headers."""
    return get_auth_headers(
        user_id="lecturer-123",
        email="lecturer@test.com",
        role="lecturer",
        tenant_id="test-tenant"
    )


@pytest.fixture
def test_user():
    """Test user data."""
    return {
        "id": "test-user-123",
        "email": "test@test.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "student",
        "tenant_id": "test-tenant",
    }


@pytest.fixture
def test_admin():
    """Test admin user data."""
    return {
        "id": "admin-123",
        "email": "admin@test.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "super_admin",
        "tenant_id": "test-tenant",
    }


@pytest.fixture
def test_officer():
    """Test admissions officer data."""
    return {
        "id": "officer-123",
        "email": "officer@test.com",
        "first_name": "Admissions",
        "last_name": "Officer",
        "role": "admissions_officer",
        "tenant_id": "test-tenant",
    }


@pytest.fixture
def test_tenant():
    """Test tenant data."""
    return {
        "id": "test-tenant",
        "name": "Test University",
        "subdomain": "test-university",
        "school_code": "TEST",
    }


# ==================== PYTEST CONFIGURATION ====================

def pytest_configure(config):
    """Configure pytest."""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["TESTING"] = "true"
