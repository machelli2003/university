# Two-Phase Credential System - API Quick Reference

## Endpoints Summary

### Phase 1: Application Form (Temporary Credentials)

#### 1. Purchase Application Form
```
POST /api/v1/application-form/purchase
```
**Purpose**: Initiate payment for application form
**Body**:
```json
{
  "email": "applicant@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+233201234567",
  "admission_cycle_id": "cycle_2024"
}
```
**Response** (200):
```json
{
  "payment_url": "https://checkout.paystack.com/...",
  "reference": "paystack_ref_123",
  "access_code": "code_123",
  "amount": 50000
}
```

#### 2. Verify Payment & Get Credentials
```
POST /api/v1/application-form/verify-payment
```
**Purpose**: Verify Paystack payment and receive PIN+Serial
**Body**:
```json
{
  "reference": "paystack_ref_123"
}
```
**Response** (200):
```json
{
  "success": true,
  "message": "Payment verified",
  "credentials": {
    "pin": "123456",
    "serial_number": "ABC12DEF"
  },
  "email": "applicant@example.com"
}
```

#### 3. Login with PIN + Serial
```
POST /api/v1/auth/login/application-form
```
**Purpose**: Login to application portal using PIN+Serial
**Body**:
```json
{
  "pin": "123456",
  "serial_number": "ABC12DEF",
  "email": "applicant@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```
**Response** (200):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "user_123",
    "email": "applicant@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "applicant",
    "must_change_password": false
  }
}
```

### Phase 2: Real Credentials (Permanent)

#### 4. Issue Real Credentials (Admin Only)
```
POST /api/v1/admissions/applicant/{applicant_id}/issue-credentials
Authorization: Bearer admin_token
```
**Purpose**: Issue real credentials when applicant is OFFERED
**Requires Role**: admissions_officer, registrar, university_admin, super_admin
**Path Parameters**:
- `applicant_id`: The applicant user ID

**Response** (200):
```json
{
  "success": true,
  "message": "Real credentials generated and issued",
  "credential_id": "perm_cred_123",
  "username": "john.doe",
  "activation_deadline": "2024-02-15T00:00:00Z",
  "must_change_password": true
}
```

#### 5. Login with Real Credentials
```
POST /api/v1/auth/login/permanent-credential
```
**Purpose**: Login using username + password (after acceptance)
**Body**:
```json
{
  "username": "john.doe",
  "password": "temppass123!@#"
}
```
**Response** (200):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "user_123",
    "email": "applicant@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "must_change_password": true
  }
}
```

#### 6. Change Temporary Password
```
POST /api/v1/auth/change-temporary-password
Authorization: Bearer access_token
```
**Purpose**: Change temporary password on first login
**Requires**: Valid access token (authenticated)
**Body**:
```json
{
  "old_password": "temppass123!@#",
  "new_password": "mynewpass456!@#"
}
```
**Response** (200):
```json
{
  "message": "Password changed successfully"
}
```

## Error Responses

### Authentication Errors

#### Invalid PIN/Serial (401)
```json
{
  "detail": "Invalid PIN or Serial number. Please verify and try again."
}
```

#### Already Used PIN/Serial (401)
```json
{
  "detail": "This PIN and Serial combination has already been used."
}
```

#### Email Mismatch (401)
```json
{
  "detail": "Email does not match the application form purchase"
}
```

#### Invalid Username/Password (401)
```json
{
  "detail": "Invalid username or password"
}
```

### Authorization Errors

#### Not OFFERED Status (400)
```json
{
  "detail": "Applicant status is waitlisted, not OFFERED. Only OFFERED applicants can receive real credentials."
}
```

#### Credentials Already Issued (400)
```json
{
  "detail": "Real credentials already issued for this applicant"
}
```

#### Insufficient Permissions (403)
```json
{
  "detail": "Not authorized to perform this action"
}
```

### Validation Errors

#### Invalid PIN Format (422)
```json
{
  "detail": [
    {
      "loc": ["body", "pin"],
      "msg": "ensure this value has at least 6 characters",
      "type": "value_error.string.min_length"
    }
  ]
}
```

## Frontend Integration Examples

### React: PIN/Serial Purchase
```typescript
const purchaseForm = async (email, firstName, lastName, phone) => {
  const response = await fetch('/api/v1/application-form/purchase', {
    method: 'POST',
    body: JSON.stringify({
      email, first_name: firstName, last_name: lastName,
      phone_number: phone, admission_cycle_id: 'cycle_2024'
    })
  });
  const data = await response.json();
  // Redirect to data.payment_url
  window.location.href = data.payment_url;
};
```

### React: PIN/Serial Login
```typescript
const loginWithPinSerial = async (pin, serial, email) => {
  const response = await fetch('/api/v1/auth/login/application-form', {
    method: 'POST',
    body: JSON.stringify({ pin, serial_number: serial, email })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  // Redirect to application portal
  window.location.href = '/applicant/dashboard';
};
```

### React: Real Credential Login
```typescript
const loginWithRealCredentials = async (username, password) => {
  const response = await fetch('/api/v1/auth/login/permanent-credential', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  
  if (data.user.must_change_password) {
    // Redirect to password change form
    window.location.href = '/change-password';
  } else {
    // Redirect to main dashboard
    window.location.href = '/dashboard';
  }
};
```

### React: Change Temporary Password
```typescript
const changePassword = async (oldPassword, newPassword) => {
  const response = await fetch('/api/v1/auth/change-temporary-password', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword
    })
  });
  const data = await response.json();
  // Redirect to main dashboard
  window.location.href = '/dashboard';
};
```

## curl Examples

### Purchase Form
```bash
curl -X POST http://localhost:8000/api/v1/application-form/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+233201234567",
    "admission_cycle_id": "cycle_2024"
  }'
```

### Verify Payment
```bash
curl -X POST http://localhost:8000/api/v1/application-form/verify-payment \
  -H "Content-Type: application/json" \
  -d '{"reference": "paystack_ref_123"}'
```

### Login with PIN/Serial
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/application-form \
  -H "Content-Type: application/json" \
  -d '{
    "pin": "123456",
    "serial_number": "ABC12DEF",
    "email": "john@example.com"
  }'
```

### Issue Credentials
```bash
curl -X POST http://localhost:8000/api/v1/admissions/applicant/user_123/issue-credentials \
  -H "Authorization: Bearer admin_token" \
  -H "Content-Type: application/json"
```

### Login with Real Credentials
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/permanent-credential \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe",
    "password": "temppass123!@#"
  }'
```

### Change Temporary Password
```bash
curl -X POST http://localhost:8000/api/v1/auth/change-temporary-password \
  -H "Authorization: Bearer access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "temppass123!@#",
    "new_password": "mynewpass456!@#"
  }'
```

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation, logic error) |
| 401 | Unauthorized (invalid credentials) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 422 | Unprocessable Entity (validation error) |
| 500 | Internal Server Error |

## Workflow Timeline

```
Day 1: PURCHASE
  POST /purchase
    ↓
  Paystack payment
    ↓
  POST /verify-payment
    ↓
  Receive PIN + Serial

Day 2-30: APPLICATION
  POST /login/application-form
    ↓
  Account created (if new)
    ↓
  Access application portal
    ↓
  Fill and submit application

Day 31-60: EVALUATION
  (Admissions processing)

Day 61: DECISION
  Admin marks as OFFERED
    ↓
  POST /issue-credentials
    ↓
  Real credentials generated
    ↓
  Email sent to applicant

Day 62: ENROLLMENT
  POST /login/permanent-credential (with temp password)
    ↓
  POST /change-temporary-password
    ↓
  Access enrollment system
```

## Security Notes

1. **PIN/Serial**: 6-digit PIN + 8-char Serial is cryptographically unique
2. **Passwords**: Always use HTTPS in production
3. **Tokens**: JWT tokens include expiration (access: 1 hour, refresh: 7 days)
4. **Rate Limiting**: Consider rate limiting on login endpoints
5. **Email Verification**: PIN/Serial linked to purchase email for verification
6. **Audit Logging**: All credential operations logged with user and IP
7. **One-time Use**: PIN/Serial cannot be reused after first successful login
