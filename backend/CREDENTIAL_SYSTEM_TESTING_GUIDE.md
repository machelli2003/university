# Two-Phase Credential System - Developer Setup & Testing Guide

## Quick Start

### Prerequisites
- Python 3.11+
- MongoDB running
- Paystack test API keys (already in `.env`)
- Virtual environment activated

### Environment Setup

1. **Verify .env has Paystack keys**:
```bash
# Check backend/.env
echo "PAYSTACK_PUBLIC_KEY=pk_test_046133ed63812af62707092b06ba00e2a4d8226c"
echo "PAYSTACK_SECRET_KEY=sk_test_4c83be8eebcdd0dc5cdd74587b0d51dd19b9a07b"
```

2. **Activate venv**:
```bash
cd backend
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies** (if needed):
```bash
pip install -r requirements.txt
```

## Manual Testing Workflow

### Step 1: Start Backend Server
```bash
# In venv-activated terminal
python run.py
# Server starts at http://localhost:8000
```

### Step 2: Test Application Form Purchase

#### Using curl:
```bash
# Purchase form
curl -X POST http://localhost:8000/api/v1/application-form/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testapplicant@example.com",
    "first_name": "Test",
    "last_name": "Applicant",
    "phone_number": "+233201234567",
    "admission_cycle_id": "cycle_2024"
  }'

# Response includes:
# "payment_url": "https://checkout.paystack.com/..."
# "reference": "paystack_ref_123"
```

#### Using Postman:
1. Create new Request: `POST http://localhost:8000/api/v1/application-form/purchase`
2. Body (JSON):
```json
{
  "email": "testapplicant@example.com",
  "first_name": "Test",
  "last_name": "Applicant",
  "phone_number": "+233201234567",
  "admission_cycle_id": "cycle_2024"
}
```
3. Send

### Step 3: Verify Payment

**Note**: In test environment, we simulate payment verification. The Paystack reference is stored.

```bash
# Verify payment and get PIN+Serial
curl -X POST http://localhost:8000/api/v1/application-form/verify-payment \
  -H "Content-Type: application/json" \
  -d '{"reference": "paystack_ref_123"}'

# Response:
# {
#   "success": true,
#   "credentials": {
#     "pin": "123456",
#     "serial_number": "ABC12DEF"
#   }
# }
```

**Save these credentials** for next step!

### Step 4: Login with PIN+Serial

```bash
# Login using PIN and Serial
curl -X POST http://localhost:8000/api/v1/auth/login/application-form \
  -H "Content-Type: application/json" \
  -d '{
    "pin": "123456",
    "serial_number": "ABC12DEF",
    "email": "testapplicant@example.com"
  }'

# Response:
# {
#   "access_token": "eyJ0eXAi...",
#   "refresh_token": "eyJ0eXAi...",
#   "user": {
#     "id": "user_123",
#     "email": "testapplicant@example.com",
#     "role": "applicant",
#     "must_change_password": false
#   }
# }
```

**Save the access_token** for next steps!

### Step 5: Verify PIN+Serial One-Time Use

Try to login again with the same PIN+Serial:

```bash
# Try login again (should fail)
curl -X POST http://localhost:8000/api/v1/auth/login/application-form \
  -H "Content-Type: application/json" \
  -d '{
    "pin": "123456",
    "serial_number": "ABC12DEF",
    "email": "testapplicant@example.com"
  }'

# Expected: 401 Unauthorized
# "Invalid PIN or Serial number. Please verify and try again."
```

### Step 6: Issue Real Credentials (Admin)

First, get admin token. For testing, use a super_admin account.

```bash
# Login as admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "AdminPassword123!"
  }'

# Save the admin access_token
```

Now issue real credentials:

```bash
# Get user ID from applicant (use "user_123" from earlier response)
# First, mark applicant as OFFERED (would be done via admissions endpoint)
# For testing, we'll directly call issue-credentials

curl -X POST http://localhost:8000/api/v1/admissions/applicant/user_123/issue-credentials \
  -H "Authorization: Bearer admin_access_token" \
  -H "Content-Type: application/json"

# Response:
# {
#   "success": true,
#   "message": "Real credentials generated and issued",
#   "credential_id": "perm_cred_123",
#   "username": "test.applicant",
#   "activation_deadline": "2024-02-15T00:00:00Z",
#   "must_change_password": true
# }
```

**Save the username** for next step!

### Step 7: Login with Real Credentials

```bash
# Login with permanent credentials
curl -X POST http://localhost:8000/api/v1/auth/login/permanent-credential \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test.applicant",
    "password": "temppass123!@#"  // placeholder - actual password from email
  }'

# Response:
# {
#   "access_token": "eyJ0eXAi...",
#   "user": {
#     ...
#     "must_change_password": true
#   }
# }
```

### Step 8: Change Temporary Password

```bash
# Change password (required on first login)
curl -X POST http://localhost:8000/api/v1/auth/change-temporary-password \
  -H "Authorization: Bearer access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "temppass123!@#",
    "new_password": "MyNewPassword456!@#"
  }'

# Response:
# {"message": "Password changed successfully"}
```

### Step 9: Login with New Password

```bash
# Login with new permanent password
curl -X POST http://localhost:8000/api/v1/auth/login/permanent-credential \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test.applicant",
    "password": "MyNewPassword456!@#"
  }'

# Response: Successfully logged in with new password
```

## Automated Testing

### Run Existing Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test
python -m pytest tests/test_application_form.py -v
```

### Create New Tests

Create file `tests/test_credential_system.py`:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.models import ApplicationForm, PermanentCredential

client = TestClient(app)

class TestApplicationFormPurchase:
    @pytest.mark.asyncio
    async def test_purchase_application_form(self):
        """Test purchasing an application form"""
        response = client.post(
            "/api/v1/application-form/purchase",
            json={
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
                "phone_number": "+233201234567",
                "admission_cycle_id": "cycle_2024"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "payment_url" in data
        assert "reference" in data

class TestPinSerialLogin:
    @pytest.mark.asyncio
    async def test_login_with_pin_serial(self):
        """Test PIN+Serial login"""
        # Would need to create form first
        # Then login
        pass

class TestRealCredentialsIssue:
    @pytest.mark.asyncio
    async def test_issue_real_credentials(self):
        """Test issuing real credentials to OFFERED applicant"""
        pass

class TestRealCredentialsLogin:
    @pytest.mark.asyncio
    async def test_login_with_permanent_credentials(self):
        """Test login with real credentials"""
        pass

class TestPasswordChange:
    @pytest.mark.asyncio
    async def test_change_temporary_password(self):
        """Test changing temporary password on first login"""
        pass
```

Run the tests:
```bash
python -m pytest tests/test_credential_system.py -v
```

## Database Inspection

### MongoDB - View Collections

```bash
# Connect to MongoDB (if running locally)
mongosh

# Switch to database
use eump_db

# View application forms
db.application_forms.find().pretty()

# View permanent credentials
db.permanent_credentials.find().pretty()

# Count by status
db.application_forms.aggregate([
  { $group: { _id: "$status", count: { $sum: 1 } } }
])
```

### Check Indexes

```bash
# Application form indexes
db.application_forms.getIndexes()

# Permanent credential indexes
db.permanent_credentials.getIndexes()
```

## Debugging

### Enable Debug Logging

In `backend/app/main.py` or `backend/app/config.py`:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

Then in terminal:
```bash
# Set logging level
export LOG_LEVEL=DEBUG
python run.py
```

### Check Logs

Look for these log messages:

```
# Purchase flow
"Generated PIN for form: pin=123456, serial=ABC12DEF"
"Payment verified for reference: paystack_ref_123"

# Login flow
"Applicant <email> logged in using PIN-Serial"
"Applicant <email> marked ApplicationForm as USED"

# Credentials issued
"Generated credentials for applicant <id>: username=<username>"
"Issued real credentials for application <form_id>"

# Real credential login
"User <email> logged in with permanent credentials"
"Password changed for credential <id>"
```

### Common Issues

#### Issue: "Database connection failed"
**Solution**: 
- Check MongoDB is running
- Check connection string in `.env`
- Run: `mongosh` to verify MongoDB access

#### Issue: "Import error: No module named 'app'"
**Solution**:
- Activate virtual environment
- cd into backend directory
- Ensure you're running python from venv

#### Issue: "Paystack payment verification failed"
**Solution**:
- Check Paystack keys in `.env`
- In test mode, use Paystack test reference
- Check internet connection for API calls

#### Issue: "PIN/Serial already used error"
**Solution**:
- This is expected behavior (one-time use)
- Generate new form with new PIN/Serial
- Or find unused PIN/Serial in database

## Performance Testing

### Load Test PIN/Serial Login

```bash
# Using Apache Bench
ab -n 100 -c 10 \
  -p payload.json \
  -T application/json \
  http://localhost:8000/api/v1/auth/login/application-form

# payload.json:
# {
#   "pin": "123456",
#   "serial_number": "ABC12DEF",
#   "email": "test@example.com"
# }
```

### Check Database Performance

```bash
# MongoDB query profiler
db.setProfilingLevel(1)

# Run query
db.application_forms.find({"pin": "123456"})

# Check profiling results
db.system.profile.find({millis: {$gt: 100}}).pretty()
```

## Checklist for Complete Testing

- [ ] Can purchase form (POST /purchase)
- [ ] Receive PIN+Serial from verify-payment
- [ ] Can login with PIN+Serial once (POST /login/application-form)
- [ ] Second login with same PIN+Serial fails
- [ ] Can issue real credentials when OFFERED (POST /issue-credentials)
- [ ] Real username generated correctly
- [ ] Can login with real credentials (POST /login/permanent-credential)
- [ ] must_change_password flag is true on first login
- [ ] Can change temporary password (POST /change-temporary-password)
- [ ] Can login with new password
- [ ] must_change_password flag is false after change
- [ ] PIN/Serial invalid after real credentials issued
- [ ] Audit logs contain all operations
- [ ] Database indexes exist and working
- [ ] Error messages are helpful
- [ ] API responses match documentation

## Next Steps for Development

1. **Create frontend components**:
   - ApplicationFormLoginPage (existing)
   - PermanentCredentialLoginPage (needs creation)
   - PasswordChangeForm (needs creation)

2. **Email integration**:
   - Send PIN+Serial after payment
   - Send real credentials after issue-credentials
   - Send password reset emails

3. **Admin UI**:
   - Batch issue credentials
   - View credential statistics
   - Export issued credentials

4. **Analytics**:
   - Track login attempts and successes
   - Monitor credential usage
   - Report on application-to-enrollment conversion

5. **Integration**:
   - Connect to admissions workflow
   - Integrate with student registration
   - Link to course enrollment system
