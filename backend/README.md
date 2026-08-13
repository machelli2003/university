# EUMP Backend - Enterprise University Management Platform

Multi-tenant university management backend for Ghanaian/African universities.

## Stack
- Python 3.11+, FastAPI
- MongoDB (via Motor + Beanie ODM)
- Redis + Celery (background jobs)
- Paystack (payments, test keys)
- Clean Architecture: domain → application → infrastructure → presentation

## Transformation status

### 1. Architecture changes made ✅
The platform is structured around a multi-tenant university SaaS architecture that preserves the working backend modules while extending them for onboarding, admissions, and role-scoped dashboards.

- Backend: FastAPI service with clean separation across domain, application, infrastructure, and presentation layers.
- Frontend: React + TypeScript + Vite + Tailwind stack with role-specific dashboards and route-level access boundaries.
- Auth model: JWT-based session auth, tenant-aware user context, and role checks enforced through dependency-based guards.
- Tenant model: each tenant owns isolated resources and uses tenant_id as the primary security boundary.
- University onboarding: application wizard + approval flow + setup completeness engine before activation.
- Admissions: manual WASSCE verification is the supported path until a live WAEC provider is integrated.
- Auditability: request logging and audit repository patterns are active across the API layer.

This keeps the original working functionality intact while establishing the new enterprise multi-tenant university platform architecture.

### 2. Database/schema changes made ✅
The current backend uses MongoDB collections via Beanie models, with tenant-first data design and isolated records for applicants, students, staff assignments, applications, and audit data.

Key schema additions and updates:
- `tenants`: holds tenant identity, school code, school metadata, subscription status, and default identifier formats.
- `users`: central identity model with `tenant_id`, `role`, `permissions`, MFA, activity, and login state.
- `roles` and `permissions`: support permission-based authorization and reusable access checks.
- `university_applications`: stores the onboarding wizard content, setup status, approval state, and all configuration blocks for each university application.
- `identifier_sequences`: ensures server-side generation of unique IDs without trusting frontend input.
- `applicants`: holds applicant profile, results, verification workflow, programme choices, offer status, and WASSCE manual verification metadata.
- `students`: represents accepted/admitted learners with tenant-bound academic and financial records.
- `staff_assignments`: defines department/faculty/course-level assignments for resource-scoped authorization.
- `audits`: captures request and operational events for compliance and support visibility.

This preserves the existing application model while adding the required tenant-isolated data model for onboarding, admissions, and staff access control.

### 3. API changes made ✅
The backend exposes the university SaaS APIs through FastAPI routers under the v1 namespace. The major route groups already cover authentication, onboarding, admissions, finance, exam, academic management, support modules, and role-specific dashboard endpoints.

Implemented API families:
- Auth: `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/me`, `/api/v1/auth/refresh`
- Onboarding: `/api/v1/onboarding/applications`, wizard endpoints, setup completeness, review, approve/reject, activation
- Admissions: `/api/v1/admissions/*` for application flows, eligibility, ranking, allocation, offers, and WASSCE/manual verification routes
- Finance: `/api/v1/finance/*` for payments, fee structures, scholarships, and reconciliation
- Academic: `/api/v1/academic/*` for faculties, departments, programmes, and course management
- Students, lecturer, attendance, and staff assignment endpoints for authenticated role-specific workflows
- Dashboard endpoints for admissions, registrar, lecturer, HOD, dean, finance, hostel, library, exam, student, alumni, tenant admin, and super admin views

The API layer is structured to support tenant-aware access, request logging, audit entries, and role checks before sensitive operations are allowed.

### 4. Frontend routes/pages added ✅
The frontend uses React Router with route guards and role-based access protection. The current app already includes role-specific client-side routes and landing pages for applicant portal, staff dashboards, and super-admin workspaces.

Included route groups:
- Applicant portal: `/apply/:schoolCode`, login, registration, dashboard, WASSCE entry
- Shared portal routes: dashboard, application status, academic registration, finance payments, documents, notifications, and workflow tasks
- Officer/admin routes: admissions officer, registrar, HOD, dean, finance officer, hostels, librarian, exam officer, tenant admin, and super admin
- Lecturer/student routes with restricted workspaces and role guards
- `PrivateRoute` enforces login + allowed role checks and redirects unauthorized users to `/unauthorized`

This gives the app the required route protection foundation while keeping the code organized around role-specific workspaces instead of one giant generic dashboard.

### 5. Roles and permissions added ✅
The platform already includes a role and access-control model that matches the SaaS university architecture.

Role model:
- `super_admin`, `university_admin`, `registrar`, `admissions_officer`, `dean`, `head_of_department`, `finance_officer`, `hostel_administrator`, `librarian`, `counselor`, `lecturer`, `student`, `applicant`, `parent_guardian`, `auditor`

Permission and access model:
- `User.role` and `User.permissions` are stored centrally and used to gate access.
- `Role` and `Permission` collection models support permission-based authorization.
- `AuthorizationService` and `ResourceAuthorizationService` enforce resource and role-based access rules.
- `StaffAssignment` records define department/faculty/course-level ownership and explicit assignment scope.
- Frontend `PrivateRoute` and backend `require_roles` dependency enforce route and API access restrictions.

This architecture prevents generic dashboard exposure and supports the rule: a user only sees data and routes for roles and scopes explicitly allowed for that tenant.

### 6. University onboarding workflow ✅
The onboarding flow is implemented as a staged configuration process that prevents activation before the institution is fully prepared.

Flow implemented in the backend:
- Application created with unique `university_application_id` and pending setup state.
- University admin fills wizard sections for information, IDs, academic years, faculties, departments, programmes, courses, admission cycle, requirements, fees, staff setup, and module configuration.
- Each wizard section updates the application document and marks the section complete in `setup_sections`.
- `SetupCompletenessService` calculates completion and enforces all mandatory sections before submission.
- `submit_for_review()` moves the application to `AWAITING_SUPER_ADMIN_APPROVAL` only when every mandatory section is complete.
- `approve_application()` creates the tenant record, marks the application as `PROVISIONING`, and then `activate_application()` transitions it to `ACTIVE`.
- Rejection and requested-changes paths return the application to a reviewable state without silently deleting data.

This implements the required DRAFT → PENDING_SETUP → APPROVED/PROVISIONING → ACTIVE lifecycle at the application and tenant boundary.

### 7. Admissions workflow ✅
The admissions pipeline is already structured as a real workflow instead of a single flat form.

Implemented flow:
- `POST /api/v1/admissions/apply` creates an applicant record for the authenticated user in the current tenant.
- `POST /api/v1/admissions/{applicant_id}/submit` stores programme choices and moves the application to a submitted state.
- `POST /api/v1/admissions/{applicant_id}/results/submit` supports manual results upload for the current no-WAEC integration scenario.
- `GET /api/v1/admissions/results/pending` returns pending verification entries for admissions officers.
- `POST /api/v1/admissions/{applicant_id}/results/approve` and reject paths handle result disposition.
- Eligibility checks, merit ranking, allocation, and final offers are implemented through the admissions application use cases.
- `POST /api/v1/admissions/{applicant_id}/offer/accept` transitions the applicant into the enrollment path and creates the student record flow when the accepted offer is processed.

This preserves the real admissions lifecycle for manual verification, review, and enrollment while keeping the backend modular for future integration with an official WAEC or results provider.

### 8. WASSCE verification workflow ✅
The platform follows the manual/front-end-assisted WASSCE verification model required by the specification.

Current implementation:
- `ManualVerificationService` is the active verification abstraction.
- `ResultVerificationService` provides an abstract interface for future `WAECVerificationService` integrations.
- `WASSCE` submission stores exam type, year, index number, subject-grade map, and verification status.
- Admissions officers can review details and either verify, reject, or request correction.
- The system records `verified_by`, `verified_at`, and `verification_notes` on the applicant record.
- Audit entries are logged for each verification event.

This avoids any false claim of automatic WAEC verification and keeps a clean extension point for a future official API.

### 9. Student and staff ID generation design ✅
IDs are server-generated and cannot be trusted from the frontend.

Implemented design:
- `IdentifierService` generates university application IDs, applicant IDs, student IDs, and staff IDs server-side.
- `IdentifierSequence` documents track unique, tenant-scoped sequences by year and type.
- `Tenant.identifier_formats` stores configurable templates such as:
  - `{SCHOOL_CODE}-{YEAR}-{SEQUENCE}`
  - `{SCHOOL_CODE}-STF-{SEQUENCE}`
  - `{SCHOOL_CODE}-APP-{YEAR}-{SEQUENCE}`
- `generate_university_application_id()`, `generate_student_id()`, `generate_staff_id()`, and `generate_applicant_id()` all use tenant-aware sequencing and formatting.

This satisfies the requirement to separate `university_application_id`, `tenant_id`, `school_code`, `student_id`, `staff_id`, and `applicant_id` while keeping them unique and server-authored.

### 10. Tenant isolation implementation ✅
Tenant scoping is enforced at the model and middleware/authentication boundary.

Implemented checks:
- `User.tenant_id` is part of the identity layer.
- `TenantIsolationMiddleware` sits in the API stack and validates protected requests.
- `get_current_user()` binds tenant context from the authenticated session.
- `require_roles()` and route guards restrict actions to allowed roles.
- `staff_assignments` and resource authorization services enforce assignment-based access to faculties, departments, courses, and other scope-specific resources.
- Cross-tenant access is denied by design and audited when attempted.

This enforces the rule that UI filtering is not security; the backend must own the tenant boundary.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy env file and fill in your values
cp .env.example .env
# Edit .env: set MONGODB_URL, PAYSTACK_SECRET_KEY, PAYSTACK_PUBLIC_KEY, JWT_SECRET_KEY

# 3. Run with Docker (recommended - includes Redis)
docker-compose up --build

# OR run locally (requires local MongoDB + Redis)
uvicorn app.main:app --reload

# 4. Seed test data (creates tenant, admin, officer, applicant, programme)
python -m scripts.seed_data
```

API docs available at `http://localhost:8000/docs` once running.

## WAEC Results Verification (Important)

There is currently **no live WAEC API integration**. The system uses a manual verification workflow for now:

1. Applicant submits results manually via `POST /api/v1/admissions/{id}/results/submit`
2. Admissions officer reviews pending submissions via `GET /api/v1/admissions/results/pending`
3. Officer approves via `POST /api/v1/admissions/{id}/results/approve` (or rejects)
4. Once approved, eligibility can be evaluated, then ranking/allocation/offers proceed

This manual verification path is the supported admissions workflow until WAEC integration is available.

### SMS and notifications

SMS support is currently paused and stubbed in the backend. The system still supports email/SMS stubs for development, but real SMS provider integration is not yet configured.

When a WAEC API becomes available, only `app/domain/admissions/waec_service.py` needs to change
(`_verify_via_api` method) — the rest of the pipeline is unaffected.

## Test Credentials (after seeding)

| Role | Email | Password |
|---|---|---|
| Admin | admin@test.com | Admin123! |
| Admissions Officer | officer@test.com | Officer123! |
| Applicant | applicant@test.com | Applicant123! |

## Full Admissions Test Flow

1. Register/login as applicant
2. `POST /admissions/apply` — create application
3. `POST /admissions/{id}/submit` — submit with programme choices
4. `POST /admissions/{id}/results/submit` — upload results manually
5. Login as officer
6. `GET /admissions/results/pending` — view pending
7. `POST /admissions/{id}/results/approve` — approve results
8. `POST /admissions/{id}/eligibility/evaluate` — check eligibility
9. `POST /admissions/programmes/{id}/rank` — rank applicants
10. `POST /admissions/allocate` — run allocation
11. `POST /admissions/offers/publish` — publish offers
12. `POST /admissions/{id}/offer/accept` — accept offer → student record auto-created

## Modules (22 total, all with working routes)

Auth, Admissions, Academic (Faculties/Departments/Programmes/Courses/Registration),
Finance (Paystack), Exam/Grading, Accommodation, Library, HR, Health Services,
Research, Alumni, Communication, Documents, Workflow/Approvals, Inventory, Analytics, Admin.

## Still To Do

- Frontend (React/TypeScript)
- WebSocket real-time notifications
- Live WAEC API integration (see above)
- Email/SMS provider integration (currently stubbed — logs only)
- S3/file storage integration (currently stubbed — mock URLs)
- Additional Celery scheduled tasks (cron-style, e.g. fee reminders)
# UNIVERSITY MANAGEMENT SaaS — MASTER TRANSFORMATION & IMPLEMENTATION PROMPT

## 1. ROLE
You are a senior software architect and full-stack engineer taking over an **existing working University Management SaaS application**.

The existing application already contains working functionality. Do NOT blindly rebuild the project from scratch.

Your task is to **restructure, extend, and replace the old tenant/onboarding/admissions/user-dashboard concepts** with the architecture defined in this specification while preserving useful existing functionality.

Treat this as a production-grade multi-tenant university platform.

Do not remove working modules unless they directly conflict with this specification.

Before changing code:

1. Inspect the entire existing repository.
2. Identify frontend architecture.
3. Identify backend architecture.
4. Identify authentication implementation.
5. Identify existing tenant implementation.
6. Identify existing user/role implementation.
7. Identify existing admissions functionality.
8. Identify existing student/staff models.
9. Identify existing database collections/tables.
10. Identify existing routes.
11. Identify existing API endpoints.
12. Identify existing dashboard pages.
13. Identify reusable components.
14. Identify functionality that can be migrated instead of rewritten.
Then create a migration plan before making destructive changes.

---

# 2. PRODUCT VISION
Transform the existing system into a:

**Multi-Tenant Enterprise University Management SaaS Platform**

The platform must support:

```
Super Admin
    ↓
Universities / Tenants
    ↓
University Admin
    ↓
Faculties
    ↓
Departments
    ↓
Programmes
    ↓
Courses
    ↓
Staff
    ↓
Applicants
    ↓
Students
    ↓
Graduates
    ↓
Alumni
```
The entire lifecycle must exist inside one platform.

The core lifecycle is:

```
University Application
        ↓
University Configuration
        ↓
Super Admin Approval
        ↓
University Activation
        ↓
Admissions Setup
        ↓
Applicant
        ↓
Application
        ↓
Eligibility
        ↓
Review
        ↓
Admission
        ↓
Enrollment
        ↓
Student ID
        ↓
Student
        ↓
Academic Lifecycle
        ↓
Graduation
        ↓
Alumni
```

---

# 3. CRITICAL PRINCIPLE — UNIVERSITY MUST BE FULLY CONFIGURED BEFORE ACTIVATION
Do NOT create an active university after collecting only:

- university name
- school code
- location
- email
Instead, create the university initially as:

```
DRAFT
```
or:

```
PENDING_SETUP
```
The university becomes:

```
ACTIVE
```
ONLY after all mandatory onboarding/configuration requirements have been completed and the appropriate administrator/super-admin approval has been completed.

---

# 4. UNIVERSITY CREATION WORKFLOW
The workflow should be:

```
Prospective University
        ↓
University Application
        ↓
Application ID Generated
        ↓
University Admin Account / Invitation
        ↓
University Configuration Wizard
        ↓
Complete Required Setup
        ↓
Submit for Review
        ↓
Super Admin Review
        ↓
Approve
        ↓
Provision Tenant
        ↓
Activate University
        ↓
Admissions Portal Goes Live
```
Rejected setup:

```
Submit
   ↓
Super Admin Review
   ↓
Rejected / Changes Required
   ↓
University Admin Corrects Information
   ↓
Resubmits
```

---

# 5. UNIVERSITY APPLICATION ID
Every university onboarding application must receive a unique:

```
University Application ID
```
Example:

```
UAPP-2026-000001
```
This is NOT the tenant ID.

Maintain separate identifiers:

```
university_application_id
tenant_id
university_code
```
Example:

```
University Application ID:
UAPP-2026-000001

Tenant ID:
tenant_8f72a91

School Code:
KNUST
```

---

# 6. UNIVERSITY CONFIGURATION WIZARD
The University Admin must complete a mandatory onboarding wizard.

Do not allow the university to be activated until required sections are complete.

## STEP 1 — University Information
Fields:

- legal university name
- display name
- school code
- institution type
- public/private
- location
- region
- country
- postal address
- official email
- official phone
- website
- logo
- favicon
- description
- academic calendar type
- timezone
- currency

---

# 7. STEP 2 — UNIVERSITY IDENTIFIER CONFIGURATION
The administrator must configure how institutional IDs are generated.

## Student ID
Example:

```
KNUST-2026-000001
```
Allow configurable formats such as:

```
{SCHOOL_CODE}-{YEAR}-{SEQUENCE}
```
or:

```
{SCHOOL_CODE}/{YEAR}/{SEQUENCE}
```
The system must guarantee uniqueness.

## Staff ID
Example:

```
KNUST-STF-000001
```

## Applicant ID
Example:

```
KNUST-APP-2026-000001
```

## University Application ID
Example:

```
UAPP-2026-000001
```
All ID generation must happen server-side.

Never trust IDs supplied by the frontend.

---

# 8. STEP 3 — ACADEMIC YEARS / SESSIONS
University Admin must configure:

- current academic year
- academic sessions
- semesters/terms
- registration periods
- examination periods
- result publication periods
- graduation periods
Example:

```
2026/2027 Academic Year

Semester 1
Start: September 2026
End: December 2026

Semester 2
Start: January 2027
End: May 2027
```

---

# 9. STEP 4 — FACULTIES
The admin must create the university's faculties.

Example:

```
Faculty of Computing
Faculty of Business
Faculty of Engineering
Faculty of Social Sciences
```
Each faculty should have:

- faculty code
- name
- description
- dean
- status

---

# 10. STEP 5 — DEPARTMENTS
Departments belong to faculties.

Example:

```
Faculty of Computing
    ↓
Department of Computer Science
Department of Information Technology
Department of Cybersecurity
```
Each department should have:

- department code
- name
- faculty
- HOD
- description
- status

---

# 11. STEP 6 — PROGRAMMES
The admin must create programmes.

Each programme must contain:

- programme code
- programme name
- faculty
- department
- degree type
- duration
- study mode
- programme status
- admission category
- capacity
- minimum requirements
- required documents
- grading configuration
- credit requirements
Example:

```
BSc Computer Science

Faculty:
Faculty of Computing

Department:
Computer Science

Duration:
4 years

Mode:
Regular

Capacity:
250
```

---

# 12. STEP 7 — COURSES
Programmes must contain courses.

Example:

```
BSc Computer Science

Level 100
    CSC101
    CSC102
    MAT101

Level 200
    CSC201
    CSC202

Level 300
    CSC301
    CSC302

Level 400
    CSC401
    CSC402
```
Configure:

- course code
- title
- credit hours
- level
- semester
- department
- prerequisites
- course type
- grading structure

---

# 13. STEP 8 — ADMISSION CYCLES
University Admin MUST create an admission cycle before applications can open.

Example:

```
2026/2027 Undergraduate Admissions
```
Fields:

- admission cycle
- academic year
- admission type
- opening date
- closing date
- application fee
- application portal status
- acceptance deadline
- enrollment deadline
Possible status:

```
DRAFT
SCHEDULED
OPEN
CLOSED
SUSPENDED
ARCHIVED
```

---

# 14. ADMISSION OPENING AND CLOSING
The frontend must have dedicated configuration pages.

## Admission Opening
The admin sets:

```
Opening Date
Opening Time
```

## Admission Closing
The admin sets:

```
Closing Date
Closing Time
```
The backend must enforce these dates.

Do not rely on the frontend clock.

If:

```
current_time > closing_time
```
applications must not be submitted.

---

# 15. STEP 9 — ADMISSION CATEGORIES
Allow the university to configure:

- Regular
- Fee Paying
- Mature
- International
- Transfer
- Diploma
- HND
- Top-Up
- Distance
- Postgraduate
- Other institution-specific categories
Each category can have different requirements.

---

# 16. STEP 10 — PROGRAMME ADMISSION REQUIREMENTS
Every programme must have configurable requirements.

Example:

```
BSc Computer Science

Mandatory:
English Language
Core Mathematics
Integrated Science

Electives:
Elective Mathematics
Physics
Chemistry
```
The system should NOT hard-code these rules globally.

Each tenant controls its own admission requirements.

---

# 17. STEP 11 — APPLICATION FORM CONFIGURATION
University Admin must determine which applicant fields are required.

Categories:

### Personal

- full name
- date of birth
- gender
- nationality
- phone
- email
- address

### Identification

- Ghana Card
- Passport
- other accepted ID

### Academic

- secondary school
- examination type
- examination year
- index number
- subjects
- grades

### Programme

- first choice
- second choice
- third choice

### Documents

- certificates
- photograph
- identification
- supporting documents

---

# 18. STEP 12 — APPLICATION FEE CONFIGURATION
Admin configures:

- application fee
- currency
- payment provider
- payment deadline
- refund policy
- fee categories
Do not mark a payment successful based solely on frontend state.

Payments must be verified server-side.

---

# 19. STEP 13 — STAFF SETUP
University Admin must create or invite initial staff.

Staff types include:

- Registrar
- Admissions Officer
- Lecturer
- Course Coordinator
- HOD
- Dean
- Finance Officer
- Hostel Administrator
- Librarian
- Examination Officer
- HR Officer
- IT Administrator
- Alumni Officer
- Department Administrator
- Faculty Administrator
- Student Affairs Officer
- Health/Medical Officer
- Other configurable staff roles
Every staff member receives a unique Staff ID.

---

# 20. STEP 14 — ROLE & PERMISSION CONFIGURATION
Do not only use role names.

Implement:

```
Role
+
Permissions
+
Tenant
+
Department
+
Faculty
+
Assigned Resources
```
Example:

```
Lecturer
    ↓
Assigned Courses
    ↓
Assigned Students
```
A lecturer should not automatically see every course.

---

# 21. STEP 15 — STUDENT ID CONFIGURATION
The university must configure:

- Student ID format
- starting sequence
- academic-year inclusion
- faculty/department prefixes where required
- uniqueness rules
The system generates Student IDs automatically after successful admission/enrollment.

Applicants should NOT manually create Student IDs.

---

# 22. STEP 16 — STAFF ID CONFIGURATION
Configure:

- Staff ID format
- sequence
- prefix
- department prefix if required
Example:

```
KNUST-STF-000001
```

---

# 23. STEP 17 — APPLICANT ID CONFIGURATION
Configure:

```
KNUST-APP-2026-000001
```
This must be separate from:

```
Student ID
Staff ID
University Application ID
Tenant ID
```

---

# 24. STEP 18 — HOSTEL CONFIGURATION
If accommodation is enabled:

- halls
- hostels
- blocks
- rooms
- beds
- capacity
- hostel fees
- eligibility
- allocation rules

---

# 25. STEP 19 — FINANCE CONFIGURATION
Configure:

- fee types
- fee structures
- programme fees
- level fees
- acceptance fees
- application fees
- payment methods
- scholarships
- discounts
- penalties
- refund rules

---

# 26. STEP 20 — LIBRARY CONFIGURATION
Configure:

- library branches
- borrowing rules
- borrowing periods
- fines
- categories
- membership rules

---

# 27. STEP 21 — GRADING CONFIGURATION
Configure:

- grading scale
- GPA rules
- CGPA rules
- pass mark
- grade boundaries
- CA/exam weighting
- resit rules
- academic standing rules

---

# 28. STEP 22 — GRADUATION CONFIGURATION
Configure:

- minimum credits
- minimum CGPA
- clearance requirements
- graduation status
- certificate settings
- transcript settings

---

# 29. STEP 23 — UNIVERSITY ADMIN REVIEW
Before submission, display:

```
UNIVERSITY SETUP CHECKLIST

✓ University Information
✓ University IDs
✓ Academic Year
✓ Faculties
✓ Departments
✓ Programmes
✓ Courses
✓ Admission Cycle
✓ Opening Date
✓ Closing Date
✓ Admission Requirements
✓ Application Form
✓ Application Fee
✓ Staff
✓ Student ID Configuration
✓ Staff ID Configuration
✓ Applicant ID Configuration
✓ Finance
✓ Accommodation
✓ Library
✓ Grading
✓ Graduation
```
Show incomplete sections prominently.

---

# 30. FINAL UNIVERSITY SETUP SUBMISSION
The admin clicks:

```
SUBMIT UNIVERSITY FOR APPROVAL
```
After submission:

```
Status:
AWAITING SUPER ADMIN APPROVAL
```
The university cannot open admissions yet.

---

# 31. SUPER ADMIN REVIEW
Super Admin receives:

```
University Applications
```
They can:

- review
- approve
- reject
- request changes
- view setup completeness
- inspect configuration
- review uploaded documents
- review administrator information
- review billing/trial
- provision tenant
Super Admin should NOT need to manually recreate university configuration.

---

# 32. UNIVERSITY ACTIVATION
Only after approval:

```
PENDING
   ↓
APPROVED
   ↓
PROVISIONING
   ↓
ACTIVE
```
When ACTIVE:

- tenant becomes operational
- applicant portal becomes available
- admissions can be opened according to configured dates
- staff can log in
- student lifecycle becomes available

---

# 33. UNIVERSITY APPLICATION URL
The applicant portal should support:

```
app.universityplatform.com/apply/{school_code}
```
Example:

```
app.universityplatform.com/apply/knust
```
The `{school_code}` must resolve to the correct tenant.

Do not allow the frontend to arbitrarily choose another tenant.

The backend must validate the tenant.

---

# 34. APPLICANT PORTAL
Pages:

```
/apply/:schoolCode
/apply/:schoolCode/register
/apply/:schoolCode/login
/apply/:schoolCode/dashboard
/apply/:schoolCode/application
/apply/:schoolCode/personal
/apply/:schoolCode/academic
/apply/:schoolCode/programmes
/apply/:schoolCode/documents
/apply/:schoolCode/payment
/apply/:schoolCode/review
/apply/:schoolCode/submit
/apply/:schoolCode/status
/apply/:schoolCode/offer
/apply/:schoolCode/accept-offer
```
Applicant must only see their own application.

---

# 35. WASSCE VERIFICATION — NO WAEC API CURRENTLY AVAILABLE
There is currently no WAEC API integrated into the platform.

Therefore:

DO NOT pretend that the system is automatically verifying WASSCE results.

Implement a **manual/front-end-assisted verification workflow**.

Applicant enters:

- examination type
- examination year
- index number
- candidate details
- subjects
- grades
Applicant uploads supporting evidence where required.

---

# 36. WASSCE VERIFICATION WORKFLOW
Applicant:

```
Enter WASSCE Details
        ↓
Upload Result Evidence
        ↓
Submit Application
```
Admissions Officer:

```
Open Applicant
        ↓
View Submitted WASSCE Data
        ↓
View Uploaded Result
        ↓
Compare Information
        ↓
Verify Manually
```
Possible status:

```
PENDING_VERIFICATION
VERIFIED
REJECTED
REQUIRES_CORRECTION
```
The admissions officer must record:

```
verified_by
verified_at
verification_notes
verification_status
```

---

# 37. WASSCE VERIFICATION UI
Create a dedicated page:

```
Admissions
 → WASSCE Verification
```
Example:

```
Applicant:
Aliyu Mohammed

Index Number:
1234567890

Examination Year:
2025

Submitted Results:

English              B2
Core Mathematics     A1
Integrated Science   B3
Social Studies       A1
Physics              B2
Chemistry            B3

Uploaded Evidence:
[result document preview]

Verification:

[ Verify Result ]

[ Reject ]

[ Request Correction ]

Notes:
____________________________
```
Do not automatically claim that a result is authentic.

The system records the authorized staff member's verification decision.

---

# 38. FUTURE WAEC INTEGRATION
Design the verification service so that an external verification provider/API can be added later without rewriting admissions.

Create an abstraction such as:

```
ResultVerificationService
```
Current implementation:

```
ManualVerificationService
```
Future implementation:

```
WAECVerificationService
```
The admissions system should not be tightly coupled to one verification mechanism.

---

# 39. APPLICANT APPLICATION STATES
Implement:

```
DRAFT
SUBMITTED
PAYMENT_PENDING
PAYMENT_VERIFIED
DOCUMENT_REVIEW
ELIGIBILITY_CHECK
UNDER_REVIEW
DEPARTMENT_REVIEW
FACULTY_REVIEW
COMMITTEE_REVIEW
MANUAL_REVIEW
ADMITTED
CONDITIONALLY_ADMITTED
WAITLISTED
REJECTED
WITHDRAWN
OFFER_ACCEPTED
ENROLLMENT_PENDING
ENROLLED
```
Not every university needs every state.

The tenant configuration should determine the workflow.

---

# 40. ADMISSIONS OFFICER FRONTEND
Pages:

```
Admissions Dashboard
Applications
Application Queue
Application Details
Applicant Profiles
Document Verification
WASSCE Verification
Eligibility Review
Programme Applications
Department Review
Interview Management
Admission Decisions
Offers
Waitlist
Enrollment
Admission Cycles
Admission Requirements
Application Forms
Application Fees
Admissions Reports
Communication
Audit Logs
```

---

# 41. REGISTRAR FRONTEND
Pages:

```
Registrar Dashboard
Student Records
Academic Records
Programmes
Courses
Course Registration
Academic Sessions
Results
Grade Approval
Transcripts
Certificates
Student Status
Transfers
Deferrals
Withdrawals
Graduation
Academic Standing
Academic Reports
```

---

# 42. LECTURER FRONTEND
Each lecturer gets ONLY their assigned workspace.

Pages:

```
Lecturer Dashboard
My Courses
My Classes
My Schedule
My Students
Attendance
Assignments
Assessments
Gradebook
Examinations
Course Materials
Announcements
Student Performance
Messages
Notifications
```
The lecturer must not see another lecturer's courses unless explicitly assigned/co-assigned.

---

# 43. COURSE COORDINATOR FRONTEND
Pages:

```
Coordinator Dashboard
Assigned Courses
Course Staff
Course Students
Attendance
Assessments
Grade Review
Course Materials
Course Analytics
Course Reports
```

---

# 44. HOD FRONTEND
Pages:

```
HOD Dashboard
Department Overview
Department Staff
Department Students
Programmes
Courses
Course Assignments
Results
Grade Review
Academic Performance
Admission Applications
Department Approvals
Reports
```
Only their department.

---

# 45. DEAN FRONTEND
Pages:

```
Dean Dashboard
Faculty Overview
Departments
Faculty Staff
Faculty Students
Programmes
Admissions
Academic Performance
Results
Approvals
Faculty Reports
```
Only their faculty unless explicitly authorized.

---

# 46. FINANCE OFFICER FRONTEND
Pages:

```
Finance Dashboard
Student Accounts
Fee Structures
Invoices
Payments
Receipts
Outstanding Balances
Scholarships
Discounts
Refunds
Reconciliation
Financial Reports
```
Finance staff should not automatically access grades or private academic information.

---

# 47. HOSTEL ADMIN FRONTEND
Pages:

```
Hostel Dashboard
Hostels
Rooms
Beds
Applications
Allocations
Occupancy
Check-in
Check-out
Hostel Fees
Maintenance
Reports
```

---

# 48. LIBRARY FRONTEND
Pages:

```
Library Dashboard
Books
Categories
Members
Borrowing
Returns
Reservations
Fines
Lost/Damaged Items
Library Reports
```

---

# 49. EXAMINATION OFFICER FRONTEND
Pages:

```
Examinations Dashboard
Exam Schedule
Exam Venues
Candidate Lists
Exam Attendance
Results
Grade Submissions
Result Review
Result Approval
Resits
Examination Reports
```

---

# 50. STUDENT FRONTEND
Every student receives their own Student Portal.

Pages:

```
Student Dashboard
My Profile
My Courses
Course Registration
Timetable
Attendance
Assignments
Examinations
Results
GPA / CGPA
Fees
Payments
Receipts
Scholarships
Accommodation
Library
Announcements
Messages
Documents
Transcript
Graduation
Support
```
The student can only see:

```
their own profile
their own courses
their own results
their own fees
their own attendance
their own documents
```

---

# 51. ALUMNI FRONTEND
After graduation:

```
Alumni Dashboard
Profile
Graduation Information
Certificates
Transcript
Events
Career Opportunities
Announcements
Alumni Directory
Networking
Support
```

---

# 52. TENANT ADMIN FRONTEND
The Tenant Admin gets the largest university-management workspace.

Pages:

```
Admin Dashboard

University Setup
University Profile
Academic Years
Faculties
Departments
Programmes
Courses
Admission Cycles
Admission Requirements
Application Form Builder
Application Fees

Users
Staff
Students
Roles
Permissions

Admissions
Applications
Applicants
Reviews
WASSCE Verification
Offers
Enrollment

Academics
Course Registration
Attendance
Results
Grading

Finance
Fees
Payments
Invoices
Scholarships

Accommodation
Hostels
Rooms
Allocations

Library

Examinations

Graduation

Reports

Notifications

Communication

Audit Logs

Settings
```

---

# 53. SUPER ADMIN FRONTEND
Pages:

```
Super Admin Dashboard

University Applications
Pending Universities
Approved Universities
Active Universities
Suspended Universities
Archived Universities

University Details
University Setup Review
Provisioning
Tenant Management

Billing
Plans
Subscriptions
Trials
Payments

Support
Impersonation
Support Tickets

Global Users

Global Audit Logs

Platform Analytics

System Settings

Security
MFA
Sessions
Login Activity
```

---

# 54. DASHBOARD ISOLATION
This is NON-NEGOTIABLE.

A user must never see another person's dashboard.

Do not solve this only by hiding navigation.

The backend must enforce:

```
Authentication
      ↓
Tenant Membership
      ↓
Role
      ↓
Permission
      ↓
Resource Scope
      ↓
Access
```
For example:

```
Lecturer A
```
can access:

```
Course 101
Course 205
```
but not:

```
Course 500
```
unless explicitly assigned.

A student can access:

```
Student ID = their own ID
```
but not another student.

A finance officer can access financial records within their authorized tenant/scope but not unrestricted academic records.

---

# 55. TENANT ISOLATION
Every tenant-owned record must contain:

```
tenant_id
```
Examples:

```
students
staff
faculties
departments
programmes
courses
applications
payments
hostels
rooms
grades
attendance
audits
```
Every backend query must be tenant-scoped.

NEVER trust:

```
tenant_id
```
sent by the frontend.

Determine the tenant from the authenticated user's context and/or validated tenant membership.

Tenant isolation must be enforced server-side. UI filtering is not a security boundary.

---

# 56. AUTHORIZATION MODEL
Use:

```
RBAC
+
Resource Scoping
+
Tenant Isolation
```
Potentially support ABAC later.

Permission examples:

```
students.view
students.create
students.update
students.delete

applications.view
applications.review
applications.approve

results.view
results.enter
results.approve

fees.view
fees.create
payments.verify

hostels.view
allocations.create
```
Do not scatter hard-coded role checks throughout the application.

Create reusable authorization middleware/services.

---

# 57. FRONTEND ROUTE PROTECTION
Implement route guards.

Examples:

```
/student/*
/staff/*
/admin/*
/super-admin/*
/admissions/*
```
A student navigating manually to:

```
/admin/dashboard
```
must receive an unauthorized state and must not receive admin data.

A lecturer navigating to:

```
/finance
```
must not receive finance data.

---

# 58. BACKEND AUTHORIZATION
Every protected endpoint must validate:

```
authenticated user
tenant
role
permission
resource scope
```
Never rely on React route protection as security.

---

# 59. STAFF ASSIGNMENT MODEL
Staff should be explicitly assigned to their operational scope.

Examples:

```
Lecturer
 → Course A
 → Course B

HOD
 → Department Computer Science

Dean
 → Faculty of Computing

Admissions Officer
 → Admissions Office

Finance Officer
 → Finance Office
```
This allows precise authorization.

---

# 60. SHARED WORK
When multiple staff members legitimately work on the same resource, create explicit assignments.

Example:

```
Course
 ├── Lecturer A
 ├── Lecturer B
 └── Course Coordinator
```
All assigned users can access the course, but only according to their permissions.

---

# 61. STUDENT LIFECYCLE
Implement:

```
Applicant
    ↓
Admitted
    ↓
Offer Accepted
    ↓
Enrollment
    ↓
Student ID Generated
    ↓
Active Student
    ↓
Course Registration
    ↓
Attendance
    ↓
Assessment
    ↓
Results
    ↓
Progression
    ↓
Graduation
    ↓
Graduate
    ↓
Alumni
```

---

# 62. AUDIT LOGGING
Every important action must be logged.

Audit structure:

```
tenant_id
performed_by
actor_type
event_type
resource_type
resource_id
timestamp
ip_address
user_agent
details
```
Events include:

```
university_created
university_submitted
university_approved
university_rejected

staff_created
staff_role_changed
student_created

application_submitted
document_verified
wassce_verified
application_reviewed
admission_approved
admission_rejected

offer_generated
offer_accepted

grade_entered
grade_modified
grade_approved

payment_created
payment_verified

impersonation_started
impersonation_stopped

student_graduated
alumni_activated
```

---

# 63. IMPERSONATION
Super Admin may impersonate a tenant for support.

Requirements:

- short-lived token
- tenant-scoped session
- visible impersonation banner
- start event
- stop event
- reason
- actor
- timestamp
- target tenant
Example banner:

```
⚠ SUPPORT MODE

You are currently viewing:
KNUST

Impersonated by:
Super Admin

[Exit Support Mode]
```
Never silently impersonate users.

---

# 64. UNIVERSITY SETUP COMPLETENESS ENGINE
Create a setup completion service.

Example:

```
University Setup: 87%

University Profile       ✓
IDs                      ✓
Academic Year            ✓
Faculties                ✓
Departments              ✓
Programmes               ✓
Courses                  ✓
Admissions               ✓
Application Form         ✓
Admission Requirements   ✓
Finance                  ✓
Staff                    ✓
Accommodation            ○
Library                  ○
Graduation               ✓
```
The university can only submit for approval if all mandatory sections are complete.

Optional modules should be marked optional.

---

# 65. MODULE ENABLEMENT
Not every university will use every module.

Support:

```
enabled_modules
```
Example:

```
Admissions
Academics
Finance
Accommodation
Library
Examinations
Alumni
```
The tenant admin can enable/disable optional modules during setup.

Do not show disabled modules in the university navigation.

---

# 66. FRONTEND DESIGN
The existing system should receive a modern enterprise redesign.

Use the project's existing stack where possible.

If compatible, use:

- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- Lucide icons
- React Query
- React Hook Form
- Zod
- Recharts
- Framer Motion
Design principles:

- responsive
- mobile-friendly
- desktop optimized
- accessible
- clean enterprise UI
- strong information hierarchy
- command/search functionality
- notification center
- profile menu
- breadcrumbs
- contextual actions
- data tables
- filters
- pagination
- drawers
- dialogs
- confirmation states
- loading skeletons
- empty states
- error states

---

# 67. DASHBOARD STRUCTURE
Each dashboard should contain:

```
Top Navigation
Sidebar
Page Header
Breadcrumbs
Contextual Actions
Metrics
Primary Workspace
Recent Activity
Notifications
```
But DO NOT create one generic dashboard component containing every module.

Create role-specific workspaces.

---

# 68. DATABASE ARCHITECTURE
Maintain clear relationships between:

```
tenants
university_applications
users
staff
students
applicants
applications
admission_cycles
admission_categories
faculties
departments
programmes
courses
course_assignments
enrollments
attendance
assessments
grades
fees
payments
hostels
rooms
library_items
library_transactions
examinations
graduations
alumni
notifications
audits
```
Every tenant-owned collection/table must contain:

```
tenant_id
```
where appropriate.

---

# 69. DO NOT DUPLICATE PEOPLE
Avoid creating separate unrelated user accounts for:

```
Applicant
Student
Alumni
```
where possible.

Maintain a central identity.

Example:

```
users
   ↓
applicant profile
   ↓
student profile
   ↓
alumni profile
```
Similarly:

```
users
   ↓
staff profile
```
The person's institutional identity remains consistent.

---

# 70. APPLICATION → STUDENT CONVERSION
When an applicant accepts an admission offer:

```
application.status = OFFER_ACCEPTED
```
Then enrollment begins.

Only after required enrollment conditions are satisfied:

```
Create student record
Generate Student ID
Create student portal access
Assign programme
Assign academic year
Create financial account
Create academic profile
```
Do not create duplicate student accounts if the process is retried.

This operation should be idempotent.

---

# 71. DATA VALIDATION
Use strong validation on:

- university setup
- IDs
- dates
- application forms
- academic results
- documents
- payments
- admission decisions
- student conversion
Never trust frontend validation alone.

---

# 72. TESTING REQUIREMENTS
Add tests for:

### Authentication

- student login
- staff login
- admin login
- super admin login

### Authorization

- student cannot access staff pages
- lecturer cannot access finance
- finance cannot modify grades
- HOD only sees department
- Dean only sees faculty
- staff cannot cross tenants

### Admissions

- application creation
- application submission
- document verification
- WASSCE manual verification
- eligibility
- review
- admission
- offer
- acceptance
- enrollment
- student ID generation

### University Setup

- incomplete university cannot activate
- completed university can submit
- super admin approval
- rejection
- resubmission
- activation

### Tenant Isolation
Explicitly test:

```
Tenant A user
      ↓
tries Tenant B resource
      ↓
403 Forbidden
```
This negative-path testing is essential for a multi-tenant system.

---

# 73. MIGRATION STRATEGY
Because this is an existing working system:

DO NOT immediately delete old code.

First:

```
Inspect
 ↓
Map
 ↓
Refactor
 ↓
Migrate
 ↓
Test
 ↓
Remove obsolete functionality
```
Create migration scripts where necessary.

Preserve existing production data.

If an old field conflicts with the new architecture, write an explicit migration.

Do not silently destroy records.

---

# 74. IMPLEMENTATION ORDER
Implement in this order:

## Phase 1 — Architecture

- inspect existing system
- establish tenant model
- establish identity model
- establish roles
- establish permissions
- establish authorization middleware
- establish tenant isolation

## Phase 2 — University Onboarding

- university application
- university application ID
- setup wizard
- ID configuration
- academic configuration
- faculties
- departments
- programmes
- courses
- admission cycles
- requirements
- finance
- staff
- modules
- completeness engine

## Phase 3 — Super Admin

- university review
- approval
- rejection
- provisioning
- activation
- billing/trial
- tenant management

## Phase 4 — Admissions

- applicant portal
- application form
- programme selection
- documents
- payment
- WASSCE manual verification
- eligibility
- admissions review
- department review
- decisions
- offers
- acceptance
- enrollment

## Phase 5 — Staff Workspaces

- lecturer
- registrar
- admissions
- finance
- hostel
- library
- examinations
- HOD
- Dean
- other staff

## Phase 6 — Student Portal

- student dashboard
- registration
- courses
- attendance
- results
- fees
- accommodation
- library
- documents
- graduation

## Phase 7 — Alumni

- graduation conversion
- alumni portal
- certificates
- transcripts
- alumni features

## Phase 8 — Hardening

- audit logs
- MFA
- authorization testing
- tenant isolation testing
- performance
- error handling
- monitoring
- backups
- documentation

---

# 75. FINAL NON-NEGOTIABLE REQUIREMENTS

1. Do not rebuild the existing application blindly.
2. Inspect existing code first.
3. Preserve useful working functionality.
4. Every university is a tenant.
5. Every tenant has strict data isolation.
6. Every staff member receives a Staff ID.
7. Every student receives a Student ID.
8. Every applicant receives an Application ID.
9. Every university onboarding request receives a University Application ID.
10. IDs are generated server-side.
11. University activation requires completion of mandatory setup.
12. Faculties must be configured.
13. Departments must be configured.
14. Programmes must be configured.
15. Courses must be configured.
16. Admission cycles must be configured.
17. Admission opening dates must be configured.
18. Admission closing dates must be configured.
19. Admission requirements must be configured.
20. Application forms must be configurable.
21. Application fees must be configurable.
22. Staff must be configured.
23. Student ID generation must be configured.
24. Staff ID generation must be configured.
25. Applicant ID generation must be configured.
26. Optional modules must be configurable.
27. Applicants must have their own portal.
28. Students must have their own portal.
29. Every staff role must have its own workspace.
30. Users must only see authorized pages.
31. Users must only see authorized data.
32. Frontend route protection is required.
33. Backend authorization is mandatory.
34. Tenant isolation must be enforced server-side.
35. Resource-level authorization must be enforced.
36. Lecturers only access assigned courses/students.
37. HODs only access authorized departments.
38. Deans only access authorized faculties.
39. Finance staff only access authorized financial resources.
40. Admissions staff only access authorized admissions resources.
41. Students only access their own student data.
42. WASSCE verification must currently be manual/front-end-assisted because there is no WAEC API.
43. Never falsely claim automatic WAEC verification.
44. WASSCE verification must be auditable.
45. Design the verification layer so a future official API can be integrated.
46. Admissions must support a complete lifecycle.
47. Applicant → Student conversion must be controlled.
48. Student ID must be generated during successful enrollment.
49. Graduation must transition students to alumni.
50. All sensitive operations must be audited.
51. Super Admin impersonation must be short-lived and auditable.
52. No unauthorized dashboard must be accessible by changing URLs.
53. No tenant must be able to access another tenant's records.
54. No role should receive unnecessary permissions.
55. Do not expose sensitive data to staff who do not need it.
56. Build all required frontend pages.
57. Build all required backend endpoints/services.
58. Add validation.
59. Add tests.
60. Document the new architecture.

---

# 76. DEFINITION OF DONE
The transformation is complete only when the following scenario works from beginning to end:

```
Super Admin
      ↓
Receives University Application
      ↓
University Application ID Generated
      ↓
University Admin Invited
      ↓
University Admin Completes Setup
      ↓
University Information
      ↓
ID Configuration
      ↓
Academic Year
      ↓
Faculties
      ↓
Departments
      ↓
Programmes
      ↓
Courses
      ↓
Admission Cycle
      ↓
Opening / Closing Dates
      ↓
Admission Requirements
      ↓
Application Form
      ↓
Application Fee
      ↓
Staff
      ↓
Finance
      ↓
Accommodation
      ↓
Library
      ↓
Grading
      ↓
Graduation
      ↓
Submit Setup
      ↓
Super Admin Reviews
      ↓
Approve
      ↓
Tenant Provisioned
      ↓
University ACTIVE
      ↓
Applicant Portal Opens
      ↓
Applicant Creates Account
      ↓
Application ID Generated
      ↓
Applicant Completes Application
      ↓
WASSCE Information Submitted
      ↓
Documents Uploaded
      ↓
Payment Verified
      ↓
Application Submitted
      ↓
Admissions Officer Reviews
      ↓
WASSCE Manually Verified
      ↓
Eligibility Evaluated
      ↓
Department Review
      ↓
Admission Decision
      ↓
Offer Generated
      ↓
Applicant Accepts
      ↓
Enrollment
      ↓
Student ID Generated
      ↓
Student Portal Activated
      ↓
Student Registers Courses
      ↓
Lecturers Manage Assigned Courses
      ↓
Attendance
      ↓
Assessments
      ↓
Grades
      ↓
Finance
      ↓
Examinations
      ↓
Graduation
      ↓
Alumni Portal
```
At every stage, enforce:

```
WHO IS THIS USER?
        ↓
WHICH TENANT?
        ↓
WHAT ROLE?
        ↓
WHAT PERMISSIONS?
        ↓
WHAT RESOURCE?
        ↓
IS THIS USER ASSIGNED TO IT?
        ↓
ALLOW / DENY
```
The final product should feel like **one unified university operating system**, not a collection of disconnected dashboards.

Do not implement fake functionality merely to make screens appear complete. If a backend operation does not exist, implement the required API/service and database changes. If an external integration is unavailable, create an honest manual workflow and a clean integration abstraction for future use.

Finally, provide:

1. Architecture changes made.
2. Database/schema changes.
3. API changes.
4. Frontend routes/pages added.
5. Roles and permissions added.
6. University onboarding workflow.
7. Admissions workflow.
8. WASSCE verification workflow.
9. Student/staff ID generation design.
10. Tenant isolation implementation.
11. Tests added.
12. Migration steps.
13. Any existing functionality that was replaced.
14. Any remaining TODOs or external integrations required.

can you do this yes or no?



HIGH PRIORITY (Items 16-18, 34, 46-48, 51-52, 61-67, 71-75)

Payment & document integrations
Security hardening
Critical tests
Deployment documentation
MEDIUM PRIORITY (Items 19-26, 28-31, 35-41, 53-60)

Notifications, analytics
Workflow automation
Academic enhancements
Data management
LOW PRIORITY (Items 27, 33, 42-45, 49-50, 76)

Research, counseling systems
Multi-language/currency
Non-critical features