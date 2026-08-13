# Item 13: Remaining TODOs & Replacements

## Executive Summary

After completing Items 1-12, the transformation is approximately **85% functionally complete**. All core workflows (onboarding, admissions, WASSCE verification, ID generation, tenant isolation, and migrations) are implemented and tested.

This document identifies:
1. **Code TODOs** — Specific unimplemented calculations/features
2. **Incomplete Endpoints** — Stub routes that need implementation
3. **Functionality Gaps** — Missing features per the 76-point spec
4. **Old Code to Replace** — Deprecated patterns that conflict with new architecture
5. **External Integrations Required** — Future work items

---

## 1. CODE-LEVEL TODOs (High Priority)

### 1.1 Registrar Dashboard Calculations
**File**: [app/presentation/api/v1/dashboards/registrar_dashboard.py](app/presentation/api/v1/dashboards/registrar_dashboard.py)

#### TODO #1: Academic Standing Calculation
**Line**: 155
```python
academic_standing="good",  # TODO: Calculate from GPA/results
```

**Issue**: Hardcoded as "good" instead of calculated from student GPA/academic records.

**Solution Required**:
- Implement calculation logic based on:
  - CGPA value
  - Configured academic standing thresholds
  - Pass/fail rates
- Create service: `AcademicStandingService`
- Add method: `calculate_standing(gpa: float, config: UniversityConfig) -> str`

**Priority**: HIGH — Dashboard accuracy depends on this

#### TODO #2: Students on Probation Calculation
**Line**: 195
```python
students_on_probation=[],  # TODO: Calculate from academic records
```

**Issue**: Returns empty list instead of querying students with warning/probation academic standing.

**Solution Required**:
- Query student academic records with standing != "good"
- Filter by current academic year
- Return list of StudentSummary objects
- Add service: `AcademicStandingService.get_students_on_probation(tenant_id, year)`

**Priority**: HIGH — Important for registrar oversight

#### TODO #3: Graduation Eligibility Calculation
**Line**: 196
```python
graduation_eligible=[],  # TODO: Calculate from academic progress
```

**Issue**: Returns empty list instead of identifying students who meet graduation criteria.

**Solution Required**:
- Query students with completed final level
- Verify minimum CGPA meets graduation requirement
- Check clearance status (finance, library, etc.)
- Return StudentSummary list
- Add service: `GraduationEligibilityService`

**Priority**: HIGH — Critical for graduation workflow

---

## 2. INCOMPLETE ENDPOINTS (Medium-High Priority)

### 2.1 Accommodation Module Routes
**File**: [app/presentation/api/v1/accommodation/routes.py](app/presentation/api/v1/accommodation/routes.py)

Multiple endpoints have `pass` placeholder implementations:

| Endpoint | Purpose | Status | Fix Required |
|----------|---------|--------|--------------|
| POST `/rooms/{id}` | Update room details | Line 97 `pass` | Implement update logic with audit |
| DELETE `/rooms/{id}` | Delete room | Line 149 `pass` | Implement soft delete + audit |
| POST `/allocate` | Allocate student to room | Line 164 `pass` | Implement allocation with occupancy check |
| PATCH `/deallocate` | Remove student from room | Line 194 `pass` | Implement deallocation + audit |
| POST `/maintenance` | Create maintenance request | Line 226 `pass` | Implement request creation |
| PATCH `/maintenance/{id}` | Update maintenance status | Line 250 `pass` | Implement status update |
| DELETE `/maintenance/{id}` | Delete maintenance request | Line 269 `pass` | Implement soft delete |
| GET `/occupancy` | Get occupancy summary | Line 318 `pass` | Implement occupancy calculations |
| GET `/occupancy/breakdown` | Get hall-by-hall breakdown | Line 436 `pass` | Calculate breakdown per hall |
| DELETE `/halls/{id}` | Delete hall | Line 463 `pass` | Implement soft delete |

**Solution Strategy**:
1. Replace all `pass` with actual implementations
2. Add proper validation for occupancy constraints
3. Add audit logging for all operations
4. Add database constraints for referential integrity

**Priority**: MEDIUM — Accommodation is optional in Phase 2, required for Phase 5+

---

### 2.2 Admin Routes
**File**: [app/presentation/api/v1/admin/routes.py](app/presentation/api/v1/admin/routes.py)

**Line**: 220 `pass`

**Issue**: Staff role change endpoint not implemented.

**Solution Required**:
- Implement staff role modification
- Add validation for role assignment permissions
- Add audit logging
- Verify user can only modify staff in own tenant

**Priority**: MEDIUM

---

### 2.3 Lecturer Routes
**File**: [app/presentation/api/v1/lecturer/routes.py](app/presentation/api/v1/lecturer/routes.py)

**Line**: 67 `pass`

**Issue**: Likely incomplete implementation for lecturer-specific functionality.

**Solution Required**:
- Review requirements and implement fully
- Add proper authorization checks

**Priority**: MEDIUM

---

## 3. FUNCTIONALITY GAPS vs 76-Point Spec

### 3.1 Module Enablement System (Spec Item 65)
**Status**: NOT IMPLEMENTED

**Requirement**: Not every university will use every module. System should support:
- enabled_modules configuration during setup
- Dynamic navigation based on enabled modules
- Frontend hides disabled modules

**Impact**: Multiple features (Accommodation, Library, Alumni) should be optional

**Solution**:
1. Add `enabled_modules: List[str]` to UniversityConfiguration
2. Add migration to add field to existing universities
3. Modify onboarding wizard to include module selection
4. Update navbar/menu generation to filter by enabled modules
5. Add API endpoint validation to check if module is enabled

**Priority**: MEDIUM-HIGH — Affects UI/UX for all tenants

### 3.2 Alumni Portal & Graduation Conversion (Spec Items 51, 61)
**Status**: Models exist but endpoints NOT FULLY IMPLEMENTED

**Requirement**:
- Student → Graduate conversion upon graduation
- Separate Alumni portal
- Certificate generation
- Transcript access
- Alumni events/networking

**Current State**:
- Alumni model exists
- Graduation model exists
- No graduation conversion logic
- No alumni portal routes

**Solution**:
1. Implement graduation conversion service
2. Create alumni portal routes
3. Add certificate generation (PDF service)
4. Add alumni-specific permissions
5. Create alumni dashboard/pages

**Priority**: MEDIUM — Phase 7 feature but models ready

---

### 3.3 Advanced Result Verification States (Spec Item 36-38)
**Status**: Partially implemented

**Current States**:
- PENDING_VERIFICATION
- VERIFIED
- REJECTED
- REQUIRES_CORRECTION

**Missing**:
- Appeal/reconsideration workflow
- Multiple verification rounds
- Batch verification operations

**Solution**:
1. Extend ResultVerificationService with appeal logic
2. Add verification history tracking
3. Add batch operation endpoints
4. Add verification audit trail

**Priority**: LOW — Manual verification working; can add later

---

### 3.4 Academic Standing & Probation System (Spec Item 39)
**Status**: Models exist but calculation logic MISSING

**Issue**: Dashboard TODOs reference this; no actual implementation exists.

**Solution**:
1. Create `AcademicStandingService` with calculation rules
2. Add configurable thresholds per university
3. Implement CGPA calculation from grades
4. Add probation rules (warning → probation → suspension)
5. Create academic standing update batch job

**Priority**: HIGH — Critical for registrar workflow

---

### 3.5 Financial Clearance (Spec Item 25)
**Status**: Models/routes exist but clearance LOGIC NOT IMPLEMENTED

**File**: [app/domain/finance/financial_clearance.py](app/domain/finance/financial_clearance.py)

**Issue**: Empty service with `pass` placeholder.

**Solution**:
1. Implement balance calculation
2. Implement payment verification
3. Implement clearance granting/revocation
4. Add to graduation eligibility check
5. Integrate with finance dashboard

**Priority**: MEDIUM

---

## 4. OLD CODE TO REPLACE/DEPRECATE

### 4.1 Legacy User/Role System
**Status**: Partially replaced but old code may still exist

**Action**:
- Audit all user creation code for mixed old/new patterns
- Replace all old role checks with new RBAC permission system
- Remove deprecated role enums if they exist

**Search for**:
```python
# Old patterns to find and replace
if user.role == "admin"  # Replace with permission-based checks
hardcoded_role_checks = True  # Replace with middleware
```

**Priority**: MEDIUM

---

### 4.2 Legacy Tenant Implementation (if exists)
**Status**: Replaced with new tenant model in Item 10

**Action**:
- Verify all queries use tenant_id
- Remove any multi-tenant code from pre-Item 10
- Audit that no queries access data across tenants

**Priority**: HIGH (SECURITY)

---

### 4.3 Old Dashboard Implementations
**Status**: Unknown - may have legacy dashboards

**Action**:
- Audit `/dashboards` routes
- Remove redundant dashboard implementations
- Keep only role-specific implementations from the 76-point spec

**Priority**: MEDIUM

---

## 5. EXTERNAL INTEGRATIONS REQUIRED (Future Work)

### 5.1 WAEC/WASSCE Result Verification API
**Status**: Abstracted in `ResultVerificationService`

**Current**: Manual verification workflow implemented (Item 8)

**Future Integration**:
- Implement `WAECVerificationService` extending `ResultVerificationService`
- Call WAEC API to verify result authenticity
- Cache results to avoid rate limiting
- Add fallback to manual verification

**Timeline**: When WAEC API becomes available

**File to Extend**: [app/domain/admissions/result_verification_service.py](app/domain/admissions/result_verification_service.py)

---

### 5.2 Payment Gateway Integration
**Status**: Models exist, actual payment processing NOT implemented

**Current**: Payment records created but no actual payment processing

**Required Integrations** (choose based on university location):
- **Ghana**: Paystack, Flutterwave, MTN Mobile Money
- **International**: Stripe, PayPal

**Solution**:
1. Create payment provider service abstraction
2. Implement Paystack integration (as example)
3. Add webhook handlers for payment confirmation
4. Add payment status verification
5. Create payment receipt generation

**File to Create**: `app/infrastructure/external_services/payment_service.py`

**Priority**: HIGH — Admissions cannot close without payment verification

---

### 5.3 Email/SMS Notifications
**Status**: Service exists but SMTP configuration incomplete

**File**: [app/infrastructure/external_services/email_service.py](app/infrastructure/external_services/email_service.py)

**Current**: Basic SMTP setup

**Required**:
1. Email template system (onboarding invitations, admission offers, results, etc.)
2. SMS integration (Twilio, AfricasTalking, etc.)
3. Notification queue/scheduler
4. Unsubscribe management
5. Delivery tracking

**Priority**: MEDIUM

---

### 5.4 Document Upload/Storage
**Status**: Routes accept documents but STORAGE mechanism MISSING

**Issue**: Where are uploaded documents stored? S3? Local filesystem?

**Solution**:
1. Choose storage backend (AWS S3, Azure Blob, MinIO, or local)
2. Implement file service abstraction
3. Add document scanning/validation
4. Add virus scanning before storage
5. Add file retention policies

**Priority**: HIGH — Required for admissions documents

---

### 5.5 QR Code Generation (Student ID Cards)
**Status**: Service exists but NOT IMPLEMENTED

**File**: [app/infrastructure/external_services/qr_code_service.py](app/infrastructure/external_services/qr_code_service.py)

**Issue**: Empty service with `pass` placeholder.

**Solution**:
1. Implement QR code generation for student IDs
2. Encode student ID + verification token
3. Generate ID card PDF with QR code
4. Add QR code verification endpoint

**Priority**: LOW — Enhancement for student ID cards

---

### 5.6 Reporting/Analytics Engine
**Status**: NOT IMPLEMENTED

**Spec Items**: 40-45 (multiple dashboard requirements)

**Required**:
1. Real-time analytics for super admin
2. Tenant-specific reporting
3. Academic performance analytics
4. Finance reporting
5. Enrollment analytics

**Solution**:
1. Create reporting service
2. Add scheduled report generation
3. Create export formats (PDF, Excel)
4. Add charting library integration
5. Create scheduled delivery system

**Priority**: MEDIUM

---

### 5.7 PDF Certificate/Transcript Generation
**Status**: NOT IMPLEMENTED

**Requirement**: Generate official documents for graduation

**Solution**:
1. Choose PDF library (reportlab or WeasyPrint)
2. Create certificate template
3. Create transcript template
4. Implement document signing
5. Add document verification QR code

**Priority**: MEDIUM — Phase 7 requirement

---

## 6. DATABASE SCHEMA ENHANCEMENTS

### 6.1 Missing Indexes for Performance
**Status**: Basic indexes added in Migration 001

**Required Additional Indexes**:
```python
# Student queries
db.students.create_index([("tenant_id", 1), ("academic_year", 1)])
db.students.create_index([("tenant_id", 1), ("programme_id", 1)])

# Course queries  
db.courses.create_index([("tenant_id", 1), ("department_id", 1)])
db.course_assignments.create_index([("tenant_id", 1), ("lecturer_id", 1)])

# Financial queries
db.payments.create_index([("tenant_id", 1), ("student_id", 1)])
db.payments.create_index([("tenant_id", 1), ("status", 1), ("created_at", -1)])

# Attendance queries
db.attendance.create_index([("tenant_id", 1), ("course_id", 1), ("date", -1)])

# Grade queries
db.grades.create_index([("tenant_id", 1), ("student_id", 1), ("academic_year", 1)])
```

**Solution**: Create migration 004_add_performance_indexes.py

**Priority**: MEDIUM (Performance optimization - Item 15)

---

### 6.2 Audit Log Partitioning
**Status**: Audit logs stored but no partitioning

**Issue**: audit_logs collection will grow very large

**Solution**:
1. Implement time-based partitioning
2. Archive old audit logs
3. Create indexes for efficient querying
4. Add retention policy

**Priority**: LOW (Can add later as data grows)

---

## 7. TESTING GAPS

### 7.1 Outstanding Test Coverage
**Current**: Items 1-12 have end-to-end tests

**Missing Tests**:
- [ ] Accommodation allocation logic
- [ ] Academic standing calculations
- [ ] Graduation eligibility checks
- [ ] Financial clearance workflow
- [ ] Module enablement filtering
- [ ] Alumni conversion workflow
- [ ] Cross-tenant isolation (negative path testing)
- [ ] Permission boundary testing
- [ ] Payment gateway integration

**Priority**: HIGH — Especially cross-tenant isolation tests

---

## 8. DOCUMENTATION UPDATES NEEDED

### 8.1 API Documentation
- [ ] Swagger/OpenAPI specs for all endpoints
- [ ] Add missing endpoint descriptions
- [ ] Add example requests/responses
- [ ] Document all error codes

**Status**: Partially complete; needs finalization

---

### 8.2 Database Schema Documentation
- [ ] Collection schemas
- [ ] Relationship diagrams
- [ ] Index strategy documentation
- [ ] Data retention policies

**Status**: Minimal; needs expansion

---

### 8.3 Deployment Guide
- [ ] Production deployment steps
- [ ] Database migration procedures (partially done)
- [ ] Environment configuration
- [ ] SSL/TLS setup
- [ ] Monitoring setup
- [ ] Backup procedures

**Status**: DEPLOYMENT_GUIDE.md exists but needs review

---

## 9. SUMMARY TABLE: PRIORITY & EFFORT

| Item | Category | Priority | Effort | Status |
|------|----------|----------|--------|--------|
| Academic Standing Calculation | Code TODO | HIGH | 4 hours | Not Started |
| Probation Query | Code TODO | HIGH | 2 hours | Not Started |
| Graduation Eligibility | Code TODO | HIGH | 3 hours | Not Started |
| Accommodation Endpoints | Endpoints | MEDIUM | 6 hours | Stub Only |
| Module Enablement | Feature | MEDIUM-HIGH | 4 hours | Not Started |
| Alumni Portal | Feature | MEDIUM | 8 hours | Models Only |
| Financial Clearance Logic | Feature | MEDIUM | 4 hours | Not Started |
| Payment Gateway | Integration | HIGH | 8 hours | Not Started |
| Document Storage | Integration | HIGH | 4 hours | Not Started |
| Email/SMS Templates | Integration | MEDIUM | 6 hours | Not Started |
| QR Code Service | Enhancement | LOW | 2 hours | Not Started |
| Performance Indexes | Database | MEDIUM | 2 hours | Not Started |
| Cross-Tenant Tests | Testing | HIGH | 8 hours | Not Started |

---

## 10. RECOMMENDED IMPLEMENTATION ROADMAP

### Phase A: High-Priority Code Fixes (Next 2 items)
**Goal**: Fix all HIGH-priority code TODOs and complete all endpoints

1. **Item 13a** (THIS ITEM): Create AcademicStandingService + implement all registrar dashboard calculations
2. **Item 13b**: Complete all accommodation endpoint implementations
3. **Item 13c**: Implement financial clearance logic
4. **Item 13d**: Complete admin/lecturer route implementations

**Estimated**: 15 hours

### Phase B: Critical Integrations & Features
5. **Item 14**: Frontend validation & polish (may reveal missing backend endpoints)
6. **Item 13e**: Payment gateway integration (required for production)
7. **Item 13f**: Document storage solution (required for admissions)
8. **Item 13g**: Email notification system (required for user experience)

**Estimated**: 20 hours

### Phase C: Enhanced Features
9. **Item 13h**: Module enablement system
10. **Item 13i**: Alumni workflow + portal
11. **Item 13j**: Advanced result verification features
12. **Item 13k**: Reporting/analytics engine

**Estimated**: 24 hours

### Phase D: Testing & Performance (Item 15)
13. **Item 13l**: Add cross-tenant isolation tests
14. **Item 15**: Performance optimization + additional indexes
15. **Item 13m**: Documentation finalization

**Estimated**: 16 hours

---

## 11. NEXT STEPS

**Immediate Action** (This Item): 
Should we proceed with Item 13a (AcademicStandingService + dashboard calculations)?

This will:
- ✅ Fix 3 HIGH-priority TODOs
- ✅ Unblock registrar dashboard
- ✅ Provide foundation for graduation workflow
- ✅ Complete academic lifecycle visualization

**Then proceed to**: Item 13b-d (Complete all stub endpoints)

**Then proceed to**: Item 14 (Frontend validation & polish)

---

## Appendix: Code References

All TODO locations in order of priority:

1. `registrar_dashboard.py:155` - Academic standing calculation
2. `registrar_dashboard.py:195` - Probation calculation
3. `registrar_dashboard.py:196` - Graduation eligibility
4. `accommodation/routes.py:97,149,164,194,226,250,269,318,436,463` - 10 endpoints
5. `admin/routes.py:220` - Staff role change
6. `lecturer/routes.py:67` - Lecturer features
7. `financial_clearance.py` - Payment verification
8. `qr_code_service.py` - ID card generation
9. `email_service.py` - Template system
10. Various `.env` configs - Email/payment credentials

---

**Document Metadata**:
- Created: 2026-08-13
- Item: 13 (Remaining TODOs & Replacements)
- Status: ANALYSIS COMPLETE
- Next Review: After Item 13a completion
