# Application Form Purchase System (PIN & Serial Number)

## Overview

This system implements the Ghanaian university admission model where applicants must purchase an application form (receiving PIN and Serial number) before they can access the admission application portal.

**Workflow:**
1. Applicant purchases application form via online payment (Paystack)
2. System generates unique PIN (6 digits) and Serial Number (8 characters)
3. Applicant receives credentials and can login to the portal
4. After login, applicant fills out their application form
5. Application progresses through the admission workflow

---

## System Architecture

### Database Models

#### ApplicationForm Document
Located: `backend/app/infrastructure/models/application_form.py`

**Fields:**
- `pin` (Indexed): 6-digit unique PIN
- `serial_number` (Indexed): 8-character unique serial
- `admission_cycle_id`: Which admission cycle this form is for
- `academic_year`: Academic year (e.g., "2024/2025")
- `applicant_id`: Linked after first login
- `applicant_email`: Email used to purchase
- `first_name`, `last_name`, `phone_number`: Contact info
- `amount`, `currency`: Payment amount in GHS
- `payment_reference`: Paystack reference number
- `status`: PURCHASED, USED, EXPIRED, CANCELLED
- `login_count`, `first_login_at`, `last_login_at`: Usage tracking

**Indexes:**
- PIN lookup
- Serial number lookup
- Applicant ID (find forms by applicant)
- Admission cycle + status (active forms per cycle)
- Payment reference (track payments)

---

### Backend Services

#### ApplicationFormPurchaseService
Located: `backend/app/infrastructure/services/paystack_service.py`

**Responsibilities:**
1. **Payment Initialization**
   - Takes applicant email, amount, admission cycle info
   - Calls Paystack API to generate payment link
   - Returns authorization URL and payment reference

2. **Payment Verification**
   - Verifies payment status with Paystack
   - Confirms payment was successful
   - Extracts payment metadata

3. **Credential Generation**
   - Generates unique PIN and Serial Number
   - Creates ApplicationForm database record
   - Ensures uniqueness of credentials

4. **Usage Tracking**
   - Marks form as USED after login
   - Updates login count and timestamps
   - Links applicant to form

**Key Methods:**
```python
async def initialize_payment(...)  # Get Paystack link
async def verify_payment(reference: str)  # Confirm payment
async def create_application_form(...)  # Generate PIN/Serial
async def get_form_by_pin_and_serial(...)  # Lookup
async def mark_form_as_used(...)  # After login
```

#### ApplicationFormRepository
Located: `backend/app/infrastructure/database/repositories/application_form_repository.py`

**Data Access Methods:**
- `create()`, `save()`, `update()`, `delete()`: CRUD operations
- `get_by_pin_and_serial()`: Find active form by credentials
- `get_by_applicant_id()`: Find form by applicant
- `get_by_admission_cycle()`: Get all forms for cycle
- `get_by_paystack_reference()`: Track payments
- `count_by_status()`: Statistics and reporting

---

### API Endpoints

#### Purchase Endpoints

**POST `/api/v1/application-form/purchase`**
- **Purpose**: Initiate payment for application form
- **Request**:
  ```json
  {
    "email": "student@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+233XXXXXXXXX",
    "admission_cycle_id": "2024/2025"
  }
  ```
- **Response**:
  ```json
  {
    "payment_url": "https://checkout.paystack.com/...",
    "reference": "7PVQVP9Z0d",
    "access_code": "Access code here",
    "amount": 50.0
  }
  ```
- **Flow**:
  1. Validate applicant info
  2. Call Paystack to initialize payment
  3. Return payment URL for redirection

**POST `/api/v1/application-form/verify-payment`**
- **Purpose**: Verify payment and generate credentials
- **Request**:
  ```json
  {
    "reference": "7PVQVP9Z0d"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Payment verified...",
    "credentials": {
      "pin": "123456",
      "serial_number": "AB12CD34",
      "payment_reference": "APPFORM-123456"
    },
    "email": "student@example.com"
  }
  ```
- **Flow**:
  1. Verify payment with Paystack
  2. Check if form already created (prevent duplicates)
  3. Generate PIN and Serial
  4. Create ApplicationForm record
  5. Return credentials

**GET `/api/v1/application-form/check-form/{pin}/{serial_number}`**
- **Purpose**: Validate credentials before login
- **Response**:
  ```json
  {
    "valid": true,
    "message": "PIN and Serial are valid",
    "admission_cycle_id": "2024/2025",
    "academic_year": "2024/2025"
  }
  ```

#### Admin Endpoints

**GET `/api/v1/application-form/forms/by-cycle/{admission_cycle_id}`**
- Get all forms purchased for a cycle
- Shows PIN, serial, status, email, amount, dates

**GET `/api/v1/application-form/stats/by-cycle/{admission_cycle_id}`**
- Statistics: total purchased, used, unused, revenue

---

### Authentication Routes

#### PIN/Serial Login
**POST `/api/v1/auth/login/application-form`**
- **Purpose**: Login using PIN and Serial instead of password
- **Request**:
  ```json
  {
    "pin": "123456",
    "serial_number": "AB12CD34",
    "email": "student@example.com",
    "first_name": "John",  // optional
    "last_name": "Doe"     // optional
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJ0eXAi...",
    "refresh_token": "eyJ0eXAi...",
    "user": {
      "id": "user_id",
      "email": "student@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "applicant",
      "is_active": true,
      ...
    }
  }
  ```
- **Flow**:
  1. Validate PIN and Serial format
  2. Find ApplicationForm with PIN + Serial
  3. Verify credentials match provided email
  4. Check if applicant has existing account
  5. If not, create new applicant account
  6. Generate access and refresh tokens
  7. Mark form as USED
  8. Return tokens and user info

---

## Frontend Components

### 1. ApplicationFormPurchasePage
Located: `frontend/src/pages/applicant/ApplicationFormPurchasePage.tsx`

**Steps:**
1. **Info Step**: Collect applicant details
   - Email, First Name, Last Name, Phone
   - Display application fee
   - Validate form

2. **Payment Step**: Process Paystack payment
   - Show loading state
   - Display payment reference
   - Verify payment with backend

3. **Success Step**: Display credentials
   - Show PIN with show/hide toggle
   - Show Serial Number with show/hide toggle
   - Copy to clipboard buttons
   - Display payment reference
   - Important security notice
   - Button to proceed to login

**Features:**
- Form validation
- Error handling with user-friendly messages
- Credential masking for security
- Copy to clipboard functionality
- Responsive design
- Email delivery notice

### 2. ApplicationFormLoginPage
Located: `frontend/src/pages/auth/ApplicationFormLoginPage.tsx`

**Features:**
- Input fields for PIN (6 digits) and Serial (8 characters)
- Email verification field
- Show/hide toggles for security
- Real-time format validation
- Error handling
- Login attempt limiting
- Link to purchase form
- Help/support information

**Security:**
- Max 3 login attempts
- Form blur after failed attempts
- PIN/Serial masking by default

---

## Payment Flow with Paystack

### Overview
1. **Initiate**: Frontend calls POST `/api/v1/application-form/purchase`
2. **Backend Calls Paystack**: Creates payment session
3. **Get Payment Link**: Returns Paystack checkout URL
4. **Redirect to Paystack**: User completes payment on Paystack
5. **Verify**: Frontend calls POST `/api/v1/application-form/verify-payment`
6. **Backend Verifies**: Checks payment status with Paystack
7. **Generate Credentials**: Creates PIN/Serial if payment successful
8. **Return Credentials**: User receives PIN/Serial

### Paystack Integration

**Endpoint**: `https://api.paystack.co`

**Headers**:
```
Authorization: Bearer {PAYSTACK_SECRET_KEY}
Content-Type: application/json
```

**Environment Variables**:
```
PAYSTACK_PUBLIC_KEY=pk_test_...
PAYSTACK_SECRET_KEY=sk_test_...
```

**Initialize Payment Request**:
```json
{
  "email": "applicant@example.com",
  "amount": 5000,  // in pesewa (5000 = 50 GHS)
  "metadata": {
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+233XXXXXXXXX",
    "admission_cycle_id": "2024/2025",
    "academic_year": "2024/2025"
  },
  "callback_url": "http://localhost:5173/payment-verification"
}
```

**Verify Payment**:
```
GET https://api.paystack.co/transaction/verify/{reference}
```

---

## Database Schema Details

### ApplicationForm Collection (MongoDB)

```javascript
{
  _id: ObjectId,
  pin: String,              // Indexed, Unique
  serial_number: String,    // Indexed, Unique
  
  // Admission Info
  admission_cycle_id: String,
  academic_year: String,
  
  // Applicant Info
  applicant_id: String,     // Indexed, populated after first login
  applicant_email: String,  // Indexed
  first_name: String,
  last_name: String,
  phone_number: String,
  
  // Payment Info
  amount: Float,
  currency: String,         // "GHS"
  payment_method: String,   // "paystack"
  payment_reference: String,
  paystack_reference: String, // Indexed
  payment_status: String,   // "completed"
  
  // Status & Usage
  status: String,           // "purchased", "used", "expired", "cancelled"
  login_count: Integer,
  first_login_at: DateTime,
  last_login_at: DateTime,
  used_at: DateTime,
  expired_at: DateTime,
  
  // Timestamps
  created_at: DateTime,
  
  // Notes
  notes: String
}

// Indexes
- pin (ascending)
- serial_number (ascending)
- applicant_id (ascending)
- (admission_cycle_id, status) (ascending)
- paystack_reference (ascending)
- (created_at, -1) (descending)
```

---

## Configuration & Environment

### Required Environment Variables

```env
# Paystack Configuration
PAYSTACK_PUBLIC_KEY=pk_test_046133ed63812af62707092b06ba00e2a4d8226c
PAYSTACK_SECRET_KEY=sk_test_4c83be8eebcdd0dc5cdd74587b0d51dd19b9a07b

# Application Settings
APPLICATION_FORM_FEE=50.0  # Amount in GHS
PAYSTACK_CALLBACK_URL=http://localhost:5173/payment-verification
```

### Paystack API Setup
1. Get API keys from Paystack dashboard (https://dashboard.paystack.com/)
2. Add keys to `.env` file
3. Test with test keys first
4. Switch to live keys for production

---

## Security Considerations

### PIN Generation
- Random 6-digit number: `000000` to `999999`
- Cryptographically secure generation using `secrets.choice()`
- Uniqueness verified before saving

### Serial Number Generation
- Random 8-character alphanumeric: `A-Z`, `0-9`
- Format: `AB12CD34` (example)
- Cryptographically secure generation
- Uniqueness verified before saving

### Credential Protection
- PIN and Serial stored in database (hashing not needed - they're temporary)
- Frontend masks credentials by default (show/hide toggle)
- Email delivery for backup
- One-time use (marked USED after login)
- Expiration after admission cycle ends

### Login Security
- PIN/Serial verified before account creation
- Email verification matches
- Rate limiting on failed attempts
- Account lockout after suspicious activity
- JWT tokens issued after successful login

---

## Error Handling

### Common Errors & Solutions

**"Invalid PIN or Serial number"**
- Form has already been used
- Form has expired
- Credentials are incorrect
- → User should purchase a new form

**"Email does not match"**
- Email provided doesn't match purchase record
- → User should use the email from original purchase

**"Payment service not configured"**
- Paystack API key missing in environment
- → Set PAYSTACK_SECRET_KEY in .env

**"Payment verification failed"**
- Payment not found or still processing
- Network issue with Paystack
- → Retry verification or contact support

---

## Testing

### Manual Testing Checklist

1. **Purchase Form**
   - ✓ Fill in applicant details
   - ✓ Verify payment form loads
   - ✓ Simulate payment completion

2. **Verify Payment**
   - ✓ Check credentials returned
   - ✓ Verify PIN format (6 digits)
   - ✓ Verify Serial format (8 chars)
   - ✓ Check ApplicationForm in database

3. **Login with PIN/Serial**
   - ✓ Enter PIN, Serial, Email
   - ✓ Verify form marked as USED
   - ✓ Verify applicant account created
   - ✓ Verify tokens returned

4. **Prevent Reuse**
   - ✓ Try logging in with same PIN/Serial
   - ✓ Should get "Invalid PIN or Serial" error

5. **Admin Dashboard**
   - ✓ View forms by admission cycle
   - ✓ View statistics and revenue
   - ✓ Search by reference number

### API Testing (curl examples)

**Purchase Form:**
```bash
curl -X POST http://localhost:8000/api/v1/application-form/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+233XXXXXXXXX",
    "admission_cycle_id": "2024/2025"
  }'
```

**Login with PIN/Serial:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/application-form \
  -H "Content-Type: application/json" \
  -d '{
    "pin": "123456",
    "serial_number": "AB12CD34",
    "email": "test@example.com"
  }'
```

---

## Deployment Notes

### Production Setup

1. **Paystack Keys**
   - Switch from test keys to live keys
   - Update in environment: `PAYSTACK_SECRET_KEY`, `PAYSTACK_PUBLIC_KEY`

2. **Callback URL**
   - Update `PAYSTACK_CALLBACK_URL` to production frontend URL
   - Ensure HTTPS

3. **Database Indexes**
   - Ensure all indexes are created on ApplicationForm collection
   - Check index performance

4. **Email Notifications**
   - Set up email service to send PIN/Serial after purchase
   - Add email template with credentials

5. **Monitoring**
   - Track payment success/failure rates
   - Monitor PIN/Serial generation
   - Alert on system failures

### Scaling Considerations

- PIN/Serial generation may conflict at scale (multiple simultaneous purchases)
- Consider UUID fallback if conflicts occur
- Database indexes critical for performance
- Rate limiting on payment endpoint

---

## Future Enhancements

1. **Email Notifications**
   - Auto-send PIN/Serial via email after purchase
   - Send reminders before admission cycle closes
   - Send confirmation when form is first used

2. **Mobile OTP**
   - Send PIN via SMS instead of email
   - Verify phone number at purchase

3. **Payment Plans**
   - Allow installment payments
   - Partial payment with balance due

4. **Digital Receipt**
   - Generate PDF receipt after payment
   - Send via email and make available in portal

5. **Bulk Purchase**
   - University staff can purchase forms for multiple applicants
   - Batch PIN/Serial generation

6. **Form Renewal**
   - Allow re-purchase for new admission cycles
   - Automatic PIN/Serial renewal

7. **Analytics Dashboard**
   - Real-time sales dashboard for admins
   - Revenue tracking
   - Applicant sourcing analysis

---

## Summary

This PIN & Serial Number system provides:
- **Security**: Unique credentials prevent fraud
- **Control**: University controls admission access
- **Revenue**: Payment collection before application
- **Tracking**: Complete audit trail of purchases and logins
- **Ghana Model**: Implements authentic Ghanaian university admission flow

The system is production-ready with Paystack integration, comprehensive error handling, and secure credential generation.
