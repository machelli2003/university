# Two-Phase Credential Lifecycle System

## Overview

This document describes the complete two-phase credential system for Ghana university admissions. Applicants use **temporary credentials** (PIN + Serial) during the application phase, then transition to **permanent credentials** (username + password) after acceptance.

## System Architecture

### Phase 1: Application Phase (Temporary Credentials)

**Duration**: From form purchase until application decision
**Credentials**: PIN (6 digits) + Serial Number (8 characters)
**Storage Model**: `ApplicationForm`
**Purpose**: Access application portal to fill and submit application

#### Flow
```
1. Applicant purchases form via Paystack payment
   ↓
2. PIN + Serial generated (unique pair)
   ↓
3. Applicant receives PIN + Serial (email/SMS)
   ↓
4. Applicant logs in with PIN + Serial + Email
   ↓
5. Account created (if first time)
   ↓
6. ApplicationForm marked as USED
   ↓
7. Applicant can fill/submit application
   ↓
8. (Application cycles through evaluations)
```

#### Key Features
- **One-time use**: PIN/Serial can only be used once (status transitions PURCHASED → USED)
- **Email verification**: Email must match purchase email
- **Automatic account creation**: Account created on first login if doesn't exist
- **Login tracking**: Tracks first_login_at, last_login_at, login_count
- **No password required**: PIN/Serial login doesn't require a password

### Phase 2: Enrollment Phase (Permanent Credentials)

**Duration**: After applicant is OFFERED (accepted) until graduation/exit
**Credentials**: Username + Password (permanent)
**Storage Model**: `PermanentCredential`
**Purpose**: Access enrollment system, course registration, grades, etc.

#### Flow
```
1. Admissions decision: Applicant marked as OFFERED
   ↓
2. Admin calls `/issue-credentials` endpoint
   ↓
3. Permanent credentials generated:
   - Username (derived from email)
   - Temporary Password (random, strong)
   ↓
4. PermanentCredential record created
   ↓
5. ApplicationForm marked: has_real_credentials = True
   ↓
6. Credentials sent to applicant via email
   ↓
7. Applicant logs in with username + temporary password
   ↓
8. System requires password change on first login
   ↓
9. Applicant sets permanent password
   ↓
10. Can now access enrollment system
```

#### Key Features
- **Issued on acceptance only**: Real credentials only for OFFERED applicants
- **Temporary password**: Must be changed on first login
- **One-way transition**: After real credentials issued, PIN/Serial becomes invalid
- **Multiple logins allowed**: Unlike PIN/Serial, real credentials support unlimited logins
- **Password management**: Full password change capability after first change
- **Account linkage**: PermanentCredential linked to existing or auto-created user account
- **Status tracking**: Credentials can be deactivated if needed

## Database Schema

### ApplicationForm Collection

```python
class ApplicationForm(Document):
    # Temporary Credentials (Phase 1)
    pin: str  # 6-digit unique PIN
    serial_number: str  # 8-char unique Serial
    status: ApplicationFormStatusEnum  # PURCHASED, USED, EXPIRED, CANCELLED
    applicant_email: str  # Purchase email
    first_name: Optional[str]
    last_name: Optional[str]
    
    # Payment Info
    payment_reference: str  # Paystack reference
    amount: float  # In GHS
    payment_status: str  # "completed", "pending", etc.
    
    # Admission Cycle
    admission_cycle_id: str  # Which cycle
    academic_year: str  # e.g., "2023/2024"
    
    # Usage Tracking
    applicant_id: Optional[str]  # User ID after login
    first_login_at: Optional[datetime]
    last_login_at: Optional[datetime]
    login_count: int
    
    # Real Credentials Transition (Phase 2)
    permanent_credential_id: Optional[str]  # Link to real credentials
    has_real_credentials: bool  # Flag: real creds issued
    credential_issued_at: Optional[datetime]  # When real creds issued
    application_decision: Optional[str]  # OFFERED, REJECTED, WAITLISTED
    decision_date: Optional[datetime]  # When decision made
```

### PermanentCredential Collection

```python
class PermanentCredential(Document):
    # Reference Info
    applicant_id: str  # The user ID
    application_form_id: str  # Back-link to form
    
    # Real Credentials
    username: str  # Unique username
    email: str  # Associated email
    password_hash: str  # Bcrypt hashed
    temporary_password_hash: Optional[str]  # Temp password hash
    
    # Status
    is_temporary_password: bool  # True = must change on first login
    status: CredentialStatusEnum  # GENERATED, ACTIVE, DEACTIVATED, EXPIRED
    password_change_required: bool  # True = must change password
    
    # Admission Info
    admission_cycle_id: str
    academic_year: str
    
    # Lifecycle Dates
    issued_at: datetime  # When credentials created
    issued_by: str  # Admin who issued (if manual)
    issued_reason: str  # "admission_offered", etc.
    activation_deadline: Optional[datetime]  # By when must activate
    expires_at: Optional[datetime]  # When credentials expire
    
    # Login Tracking
    first_login_at: Optional[datetime]
    last_login_at: Optional[datetime]
    login_count: int
    last_password_change: Optional[datetime]
    
    # Access Control
    is_active: bool  # Can be deactivated
```

## API Endpoints

### Phase 1: Application Form (PIN + Serial)

#### Purchase Application Form
```
POST /api/v1/application-form/purchase
Content-Type: application/json

{
  "email": "applicant@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+233201234567",
  "admission_cycle_id": "cycle_2024"
}

Response: 200 OK
{
  "payment_url": "https://checkout.paystack.com/...",
  "reference": "paystack_ref_123",
  "amount": 50000  // in pesewa (GHS 500)
}
```

#### Verify Payment & Get PIN+Serial
```
POST /api/v1/application-form/verify-payment
Content-Type: application/json

{
  "reference": "paystack_ref_123"
}

Response: 200 OK
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

#### Login with PIN + Serial
```
POST /api/v1/auth/login/application-form
Content-Type: application/json

{
  "pin": "123456",
  "serial_number": "ABC12DEF",
  "email": "applicant@example.com",
  "first_name": "John",  // optional
  "last_name": "Doe"     // optional
}

Response: 200 OK
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

### Phase 2: Real Credentials (Username + Password)

#### Issue Real Credentials (Admin)
```
POST /api/v1/admissions/applicant/{applicant_id}/issue-credentials
Authorization: Bearer admin_token

Response: 200 OK
{
  "success": true,
  "message": "Real credentials generated and issued",
  "credential_id": "perm_cred_123",
  "username": "john.doe",
  "activation_deadline": "2024-02-15T00:00:00Z",
  "must_change_password": true
}
```

#### Login with Real Credentials
```
POST /api/v1/auth/login/permanent-credential
Content-Type: application/json

{
  "username": "john.doe",
  "password": "temppass123!@#"
}

Response: 200 OK
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

#### Change Temporary Password
```
POST /api/v1/auth/change-temporary-password
Authorization: Bearer access_token
Content-Type: application/json

{
  "old_password": "temppass123!@#",
  "new_password": "mynewpass456!@#"
}

Response: 200 OK
{
  "message": "Password changed successfully"
}
```

## Services Layer

### ApplicationFormPurchaseService
Handles PIN+Serial generation and payment:
- `initialize_payment()` - Call Paystack, return payment URL
- `verify_payment()` - Check Paystack, generate credentials
- `_generate_pin()` - Create 6-digit PIN
- `_generate_serial_number()` - Create 8-char alphanumeric

### PermanentCredentialService
Handles real credential generation and management:
- `generate_credentials()` - Create username + temp password
- `issue_credentials_for_applicant()` - Issue to accepted applicant
- `change_password()` - Change temp to permanent password
- `verify_password()` - Password verification
- `_generate_username()` - Username generation
- `_generate_temporary_password()` - Strong random password
- `_hash_password()` - Bcrypt hashing

## Security Features

### PIN + Serial Security
- **Uniqueness**: Each PIN and Serial is cryptographically unique
- **One-time use**: Status changes prevent replay attacks
- **Email verification**: Email must match purchase
- **Random generation**: Uses `secrets` module for true randomness
- **Short validity**: Only valid for current admission cycle

### Real Credential Security
- **Password hashing**: Bcrypt with proper rounds
- **Temporary password**: Forced change on first login
- **No plaintext**: Passwords never stored/transmitted in plain
- **Session tracking**: Login history and last login dates
- **Deactivation**: Can be revoked if needed
- **Email verification**: Real credentials linked to verified email

### Access Control
- **Role-based**: Admin endpoints require specific roles
- **Audit logging**: All credential operations logged
- **Status validation**: Checks prevent invalid transitions
- **User linkage**: Credentials linked to specific user accounts

## Status Transitions

### ApplicationForm Status
```
PURCHASED → USED (after first login)
PURCHASED → EXPIRED (at admission cycle end)
PURCHASED → CANCELLED (if refunded)
USED → EXPIRED (end of cycle, only after USED)
```

### PermanentCredential Status
```
GENERATED → ACTIVE (first login and password change)
ACTIVE → DEACTIVATED (manual deactivation)
ACTIVE → EXPIRED (past expiration date)
```

## Usage Examples

### Complete Workflow: Purchase to Enrollment

#### Day 1: Form Purchase
```
1. Applicant visits website → Click "Buy Application Form"
2. Frontend: ApplicationFormPurchasePage component
3. Enter email, name, phone
4. Click "Proceed to Payment"
5. Redirected to Paystack
6. Pay GHS 500 (50,000 pesewa)
7. Paystack redirects back with reference
8. Frontend calls /verify-payment
9. Receive PIN: 123456, Serial: ABC12DEF
10. Credentials displayed with copy buttons
```

#### Day 2: Application Login
```
1. Applicant visits login → Select "Application Form Login"
2. Frontend: ApplicationFormLoginPage component
3. Enter email, PIN (123456), Serial (ABC12DEF)
4. Click Login
5. Backend:
   - Validates PIN+Serial pair
   - Verifies email matches
   - Finds/creates applicant account
   - Marks ApplicationForm as USED
6. Applicant logged in
7. Can now fill application
```

#### Day 60: Admissions Decision
```
1. Admissions officer reviews applications
2. Marks some as OFFERED
3. Batch process calls /issue-credentials for each OFFERED
4. For each applicant:
   - Username generated (e.g., "john.doe")
   - Temporary password generated
   - PermanentCredential created
   - Email sent with username + temp password
   - ApplicationForm updated
```

#### Day 65: Student First Login
```
1. Student receives email with username and temp password
2. Visits enrollment portal → Real Credential Login
3. Enters username "john.doe" and temp password
4. System logs in but shows password change prompt
5. Enters new permanent password
6. Password changed, can now access full system
7. Can register for courses, view grades, etc.
```

## Error Handling

### Common Errors

#### Invalid PIN+Serial
```
Status: 401 Unauthorized
{
  "detail": "Invalid PIN or Serial number. Please verify and try again."
}
```

#### Already Used PIN+Serial
```
Status: 401 Unauthorized
{
  "detail": "This PIN and Serial combination has already been used."
}
```

#### Email Mismatch
```
Status: 401 Unauthorized
{
  "detail": "Email does not match the application form purchase"
}
```

#### Not Offered (Can't Issue Creds)
```
Status: 400 Bad Request
{
  "detail": "Applicant status is waitlisted, not OFFERED. Only OFFERED applicants can receive real credentials."
}
```

#### Invalid Username/Password
```
Status: 401 Unauthorized
{
  "detail": "Invalid username or password"
}
```

#### Temp Password Not Changed
```
Status: 403 Forbidden
{
  "detail": "You must change your temporary password before accessing this resource"
}
```

## Database Indexes

### ApplicationForm
- `pin`: Fast PIN lookup
- `serial_number`: Fast Serial lookup
- `applicant_id`: Find forms by applicant
- `admission_cycle_id + status`: List forms by cycle and status
- `payment_reference`: Track payments
- `created_at`: Recent forms first

### PermanentCredential
- `applicant_id`: Find credential by applicant
- `application_form_id`: Back-link to form
- `username`: Fast username lookup for login
- `email`: Find by email
- `status`: Query by status (ACTIVE, DEACTIVATED, etc.)
- `issued_at`: Recent credentials first

## Future Enhancements

1. **Batch credential generation**: Generate credentials for multiple accepted applicants
2. **Credential renewal**: Renew expired credentials for existing students
3. **Credential revocation**: Automatic revocation for rejected applicants
4. **Email templates**: Customizable email for credential distribution
5. **SMS notifications**: Send PIN+Serial and real credentials via SMS
6. **Credential recovery**: Self-service password reset
7. **Two-factor authentication**: SMS/Email OTP for first login
8. **Login analytics**: Track login patterns and anomalies
9. **Audit compliance**: Export audit logs for regulatory compliance

## Deployment Checklist

- [ ] Verify Paystack test keys in .env (if testing)
- [ ] Ensure MongoDB collections created with proper indexes
- [ ] Email service configured for credential distribution
- [ ] Frontend pages for both login types deployed
- [ ] Admin UI for issuing credentials available
- [ ] Audit logging enabled and tested
- [ ] Error handling and user messages tested
- [ ] Documentation provided to admissions staff
- [ ] Test flow end-to-end (purchase → login → decision → real login)

## Testing Scenarios

### Test Case 1: Purchase → PIN Login → Application
```
1. User purchases form
2. Verify PIN+Serial generated
3. Log in with PIN+Serial
4. Verify account created
5. Verify ApplicationForm marked USED
6. Verify PIN+Serial no longer works for login
```

### Test Case 2: Issue Credentials → Real Login
```
1. User in system with OFFERED decision
2. Call issue-credentials endpoint
3. Verify username generated
4. Verify credentials sent/returned
5. Log in with username + temp password
6. Verify must_change_password flag set
7. Change password
8. Verify can log back in with new password
```

### Test Case 3: Security - One-Time Use
```
1. User logs in with PIN+Serial (first time)
2. Verify success
3. Log out
4. Try login again with same PIN+Serial
5. Verify rejected (status is USED now)
```

### Test Case 4: Transition Prevention
```
1. User has real credentials issued
2. Try to log in with original PIN+Serial
3. Verify rejected (ApplicationForm status = EXPIRED)
```
