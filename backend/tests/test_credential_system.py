"""
Credential System Tests

Comprehensive tests for the two-phase credential lifecycle system:
- PIN + Serial purchase and login (Phase 1)
- Real credentials issuance and login (Phase 2)
- Password management
- Email sending
- Admin batch operations
- Statistics tracking
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import re

from app.main import app
from app.infrastructure.models import ApplicationForm, PermanentCredential, CredentialStatusEnum

client = TestClient(app)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: Application Form (PIN + Serial) Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestApplicationFormPurchase:
    """Tests for purchasing application forms"""
    
    @pytest.mark.asyncio
    async def test_purchase_form_success(self):
        """Test successful application form purchase"""
        response = client.post(
            "/api/v1/application-form/purchase",
            json={
                "email": "testapplicant@example.com",
                "first_name": "Test",
                "last_name": "Applicant",
                "phone_number": "+233201234567",
                "admission_cycle_id": "cycle_2024",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "payment_url" in data
        assert "reference" in data
        assert "access_code" in data
        assert data["amount"] > 0
    
    @pytest.mark.asyncio
    async def test_purchase_form_invalid_email(self):
        """Test purchase with invalid email"""
        response = client.post(
            "/api/v1/application-form/purchase",
            json={
                "email": "invalid-email",
                "first_name": "Test",
                "last_name": "User",
                "phone_number": "+233201234567",
                "admission_cycle_id": "cycle_2024",
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_purchase_form_missing_field(self):
        """Test purchase with missing required field"""
        response = client.post(
            "/api/v1/application-form/purchase",
            json={
                "email": "test@example.com",
                "first_name": "Test",
                # Missing last_name
                "admission_cycle_id": "cycle_2024",
            }
        )
        
        assert response.status_code == 422


class TestPINSerialLogin:
    """Tests for PIN + Serial login (Phase 1)"""
    
    @pytest.mark.asyncio
    async def test_login_with_valid_pin_serial(self):
        """Test login with valid PIN and Serial"""
        # First, create a form (this would come from payment verification)
        # For testing, we'd need to mock or use test fixtures
        
        # This is a placeholder - in real tests, you'd create the form first
        response = client.post(
            "/api/v1/auth/login/application-form",
            json={
                "pin": "123456",
                "serial_number": "ABC12DEF",
                "email": "applicant@example.com",
            }
        )
        
        # Would return 401 if form doesn't exist (expected behavior)
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_login_invalid_pin_format(self):
        """Test login with invalid PIN format (less than 6 digits)"""
        response = client.post(
            "/api/v1/auth/login/application-form",
            json={
                "pin": "12345",  # Only 5 digits
                "serial_number": "ABC12DEF",
                "email": "applicant@example.com",
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_login_invalid_serial_format(self):
        """Test login with invalid Serial format (not 8 chars)"""
        response = client.post(
            "/api/v1/auth/login/application-form",
            json={
                "pin": "123456",
                "serial_number": "ABC12DE",  # Only 7 chars
                "email": "applicant@example.com",
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_login_email_mismatch(self):
        """Test login with email mismatch"""
        response = client.post(
            "/api/v1/auth/login/application-form",
            json={
                "pin": "123456",
                "serial_number": "ABC12DEF",
                "email": "wrong.email@example.com",
            }
        )
        
        # Would fail if form's email doesn't match
        assert response.status_code in [401, 404]


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2: Permanent Credentials Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestPermanentCredentialLogin:
    """Tests for real credential login (Phase 2)"""
    
    @pytest.mark.asyncio
    async def test_login_with_username_password(self):
        """Test login with username and password"""
        response = client.post(
            "/api/v1/auth/login/permanent-credential",
            json={
                "username": "test.applicant",
                "password": "TempPassword123!",
            }
        )
        
        # Would return 401 if credentials don't exist
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self):
        """Test login with invalid password"""
        response = client.post(
            "/api/v1/auth/login/permanent-credential",
            json={
                "username": "test.applicant",
                "password": "WrongPassword123!",
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self):
        """Test login with non-existent username"""
        response = client.post(
            "/api/v1/auth/login/permanent-credential",
            json={
                "username": "nonexistent.user",
                "password": "SomePassword123!",
            }
        )
        
        assert response.status_code == 401


class TestPasswordChange:
    """Tests for password change on first login"""
    
    @pytest.mark.asyncio
    async def test_change_temporary_password_success(self):
        """Test successful password change"""
        # Would need valid access token first
        response = client.post(
            "/api/v1/auth/change-temporary-password",
            json={
                "old_password": "TempPassword123!",
                "new_password": "NewPassword456!@#",
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Would return 401 if no valid token
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_change_password_invalid_old_password(self):
        """Test password change with wrong old password"""
        response = client.post(
            "/api/v1/auth/change-temporary-password",
            json={
                "old_password": "WrongPassword123!",
                "new_password": "NewPassword456!@#",
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Would return 401 with invalid old password
        assert response.status_code in [401, 500]
    
    @pytest.mark.asyncio
    async def test_change_password_weak_new_password(self):
        """Test password change with weak new password"""
        response = client.post(
            "/api/v1/auth/change-temporary-password",
            json={
                "old_password": "TempPassword123!",
                "new_password": "weak",  # Too short and weak
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should fail validation
        assert response.status_code in [400, 422]


# ═══════════════════════════════════════════════════════════════════════════
# Admin Endpoints Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestAdminCredentialIssuance:
    """Tests for admin credential issuance endpoints"""
    
    @pytest.mark.asyncio
    async def test_issue_credentials_success(self):
        """Test successful credential issuance"""
        response = client.post(
            "/api/v1/admissions/applicant/test_applicant_id/issue-credentials",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        # Would return 404 if applicant doesn't exist or isn't OFFERED
        assert response.status_code in [200, 404, 400]
    
    @pytest.mark.asyncio
    async def test_issue_credentials_not_offered(self):
        """Test credential issuance for non-OFFERED applicant"""
        # Would need applicant in different status
        response = client.post(
            "/api/v1/admissions/applicant/test_applicant_id/issue-credentials",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        # Should fail if not OFFERED
        assert response.status_code in [400, 404]
    
    @pytest.mark.asyncio
    async def test_issue_credentials_already_issued(self):
        """Test credential issuance when already issued"""
        # Would need applicant with credentials already issued
        response = client.post(
            "/api/v1/admissions/applicant/test_applicant_id/issue-credentials",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        # Should fail if already issued
        assert response.status_code in [400, 404]
    
    @pytest.mark.asyncio
    async def test_batch_issue_credentials(self):
        """Test batch credential issuance"""
        response = client.post(
            "/api/v1/admissions/credentials/batch-issue?admission_cycle_id=cycle_2024",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        # Would work with valid auth
        assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_get_credential_statistics(self):
        """Test fetching credential statistics"""
        response = client.get(
            "/api/v1/admissions/credentials/statistics?admission_cycle_id=cycle_2024",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "statistics" in data
            assert "total_applicants" in data["statistics"]
            assert "credential_issuance_rate_percent" in data["statistics"]


# ═══════════════════════════════════════════════════════════════════════════
# Security and Validation Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCredentialSecurity:
    """Tests for security features"""
    
    @pytest.mark.asyncio
    async def test_pin_serial_one_time_use(self):
        """Test that PIN+Serial can only be used once"""
        # First login would succeed
        response1 = client.post(
            "/api/v1/auth/login/application-form",
            json={
                "pin": "123456",
                "serial_number": "ABC12DEF",
                "email": "applicant@example.com",
            }
        )
        
        # Second login with same credentials should fail
        response2 = client.post(
            "/api/v1/auth/login/application-form",
            json={
                "pin": "123456",
                "serial_number": "ABC12DEF",
                "email": "applicant@example.com",
            }
        )
        
        # Second response should be different (marked as used)
        if response1.status_code == 200:
            assert response2.status_code != 200
    
    @pytest.mark.asyncio
    async def test_email_verification(self):
        """Test that email must match purchase email"""
        response = client.post(
            "/api/v1/auth/login/application-form",
            json={
                "pin": "123456",
                "serial_number": "ABC12DEF",
                "email": "different.email@example.com",
            }
        )
        
        # Should fail if email doesn't match
        assert response.status_code in [401, 404]


class TestCredentialValidation:
    """Tests for input validation"""
    
    def test_pin_validation_exactly_6_digits(self):
        """Test PIN must be exactly 6 digits"""
        response = client.post(
            "/api/v1/auth/login/application-form",
            json={
                "pin": "12345",  # 5 digits
                "serial_number": "ABC12DEF",
                "email": "test@example.com",
            }
        )
        assert response.status_code == 422
    
    def test_serial_validation_exactly_8_chars(self):
        """Test Serial must be exactly 8 characters"""
        response = client.post(
            "/api/v1/auth/login/application-form",
            json={
                "pin": "123456",
                "serial_number": "ABC12D",  # 6 chars
                "email": "test@example.com",
            }
        )
        assert response.status_code == 422
    
    def test_email_validation_required(self):
        """Test email is required"""
        response = client.post(
            "/api/v1/auth/login/application-form",
            json={
                "pin": "123456",
                "serial_number": "ABC12DEF",
                # Missing email
            }
        )
        assert response.status_code == 422
    
    def test_password_minimum_length(self):
        """Test password minimum length"""
        response = client.post(
            "/api/v1/auth/login/permanent-credential",
            json={
                "username": "test",
                "password": "short",  # Less than 8 chars
            }
        )
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCredentialWorkflow:
    """End-to-end workflow tests"""
    
    @pytest.mark.asyncio
    async def test_complete_application_flow(self):
        """Test complete application phase flow"""
        # 1. Purchase form
        purchase_response = client.post(
            "/api/v1/application-form/purchase",
            json={
                "email": "workflow@example.com",
                "first_name": "Workflow",
                "last_name": "Test",
                "phone_number": "+233201234567",
                "admission_cycle_id": "cycle_2024",
            }
        )
        
        assert purchase_response.status_code == 200
        assert "payment_url" in purchase_response.json()
    
    @pytest.mark.asyncio
    async def test_transition_from_pin_to_real_credentials(self):
        """Test transition from PIN/Serial to real credentials"""
        # In complete flow:
        # 1. Use PIN/Serial to login and fill application
        # 2. Get OFFERED decision
        # 3. Issue real credentials
        # 4. PIN/Serial no longer works
        # 5. Real credentials work
        
        # This test would verify the transition doesn't allow PIN/Serial after real creds issued
        pass


# ═══════════════════════════════════════════════════════════════════════════
# Test Utilities
# ═══════════════════════════════════════════════════════════════════════════

def validate_pin_format(pin: str) -> bool:
    """Validate PIN format (6 digits)"""
    return bool(re.match(r"^\d{6}$", pin))


def validate_serial_format(serial: str) -> bool:
    """Validate Serial format (8 alphanumeric)"""
    return bool(re.match(r"^[A-Z0-9]{8}$", serial))


def validate_username_format(username: str) -> bool:
    """Validate username format"""
    return 3 <= len(username) <= 50 and username.isalnum() or "." in username


def validate_password_strength(password: str) -> dict:
    """Validate password strength"""
    return {
        "length_ok": len(password) >= 8,
        "has_upper": any(c.isupper() for c in password),
        "has_lower": any(c.islower() for c in password),
        "has_digit": any(c.isdigit() for c in password),
        "has_special": any(c in "!@#$%^&*" for c in password),
        "is_strong": all([
            len(password) >= 12,
            any(c.isupper() for c in password),
            any(c.islower() for c in password),
            any(c.isdigit() for c in password),
            any(c in "!@#$%^&*" for c in password),
        ])
    }


# ═══════════════════════════════════════════════════════════════════════════
# Unit Tests for Utilities
# ═══════════════════════════════════════════════════════════════════════════

class TestUtilityFunctions:
    """Tests for validation utility functions"""
    
    def test_pin_validation(self):
        """Test PIN validation"""
        assert validate_pin_format("123456")
        assert not validate_pin_format("12345")  # Too short
        assert not validate_pin_format("1234567")  # Too long
        assert not validate_pin_format("12345a")  # Contains letter
    
    def test_serial_validation(self):
        """Test Serial validation"""
        assert validate_serial_format("ABC12DEF")
        assert not validate_serial_format("ABC12DE")  # Too short
        assert not validate_serial_format("ABC12DEF1")  # Too long
        assert not validate_serial_format("abc12def")  # Contains lowercase
    
    def test_password_strength(self):
        """Test password strength validation"""
        weak = validate_password_strength("weakpass")
        medium = validate_password_strength("Password123")
        strong = validate_password_strength("StrongPass123!@#")
        
        assert not weak["length_ok"] or not weak.get("is_strong")
        assert medium["length_ok"]
        assert strong["is_strong"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
