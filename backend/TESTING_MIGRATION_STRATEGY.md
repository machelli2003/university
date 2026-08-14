# Testing Strategy & Implementation Order
## Items 72-75: Test Requirements, Migration Strategy, Implementation Order, Non-Negotiable Requirements

---

## Item 72: Testing Requirements

### Test Categories

#### 1. Unit Tests
- Test individual use cases in isolation
- Test repository methods
- Test service methods
- Coverage target: 80%+

**Example:**
```python
@pytest.mark.asyncio
async def test_eligibility_engine_marks_ineligible():
    engine = EligibilityEngine(...)
    result = await engine.evaluate("applicant_123")
    assert result["eligible"] == False
    assert "Aggregate too high" in result["reason"]
```

#### 2. Integration Tests
- Test repository + use case combinations
- Test middleware behavior
- Test error handling
- Database interaction tests

**Example:**
```python
@pytest.mark.asyncio
async def test_applicant_submission_creates_audit_log():
    # Submit application
    # Verify audit log created
    # Verify audit log has correct timestamp, user, details
```

#### 3. End-to-End Tests
- Complete workflows from start to finish
- Multi-step scenarios
- Real API calls with TestClient
- Database setup/teardown

**Example:**
```python
@pytest.mark.asyncio
async def test_complete_admissions_workflow():
    # 1. Applicant registers
    # 2. Submits application
    # 3. Uploads WASSCE results
    # 4. Admin verifies
    # 5. System checks eligibility
    # 6. System ranks
    # 7. System allocates
    # 8. Applicant accepts offer
    # 9. Student record created
    # Verify each step successful
```

#### 4. Security Tests
- Tenant isolation (cross-tenant access blocked)
- Role-based access control
- Authentication token validation
- Sensitive data not exposed

**Example:**
```python
def test_tenant_a_cannot_access_tenant_b_data():
    # User from Tenant A tries to access Tenant B resource
    # Assert 403 Forbidden
    # Verify audit log records unauthorized attempt
```

#### 5. Load Tests
- System can handle concurrent requests
- Database queries perform efficiently
- No race conditions

#### 6. Negative Tests
- Invalid input validation
- Error handling
- Edge cases (null values, empty lists, etc.)

### Critical Path Tests (Must Pass)

These tests verify the system's core functionality:

1. **Authentication**
   - Login successful
   - Invalid credentials rejected
   - Tokens validated
   - MFA works

2. **Authorization**
   - Student cannot access staff pages
   - Lecturer cannot access finance
   - HOD only sees department
   - Finance cannot modify grades

3. **Tenant Isolation** ⚠️ CRITICAL
   - Tenant A cannot see Tenant B users
   - Tenant A cannot modify Tenant B data
   - All queries filter by tenant_id
   - Cross-tenant access attempts logged

4. **Admissions Workflow**
   - Application submission
   - Document verification
   - WASSCE verification
   - Eligibility check
   - Ranking & allocation
   - Offer publishing
   - Offer acceptance
   - Student record creation

5. **Payment Processing**
   - Payment initiation
   - Webhook verification
   - Payment confirmation
   - Receipt generation
   - Audit logging

6. **Student Lifecycle**
   - Applicant → Admitted → Enrolled → Student
   - Student ID generation
   - Automatic status transitions
   - State machine enforcement

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_critical_paths.py::TestAuthenticationAndAuthorization -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run only critical path tests (fast feedback)
pytest tests/test_critical_paths.py -v

# Run tests matching pattern
pytest tests/ -k "tenant_isolation" -v
```

---

## Item 73: Migration Strategy

### For Existing Deployments

**DO NOT immediately delete old code.** Follow this strategy:

#### Phase 1: Parallel Running (1-2 weeks)
1. Deploy new features alongside old ones
2. New code processes new transactions
3. Old code handles legacy data
4. Audit which code paths are used

#### Phase 2: Gradual Migration (2-4 weeks)
1. Migrate 10% of users/data to new system
2. Monitor for issues
3. Incrementally increase to 25%, 50%, 100%

#### Phase 3: Cleanup (after migration complete)
1. Keep old code for read-only fallback
2. Log all old code access
3. After 30 days with no access, can remove

### Data Migration Steps

```python
# 1. Create migration script
async def migrate_applicants():
    old_applicants = await old_db.find({"migrated": {"$exists": False}})
    for applicant in old_applicants:
        # Transform old format to new
        new_applicant = transform_to_new_format(applicant)
        
        # Create in new system
        await new_repo.create(new_applicant)
        
        # Mark as migrated
        await old_db.update(applicant.id, {"migrated": True})

# 2. Verify migration
async def verify_migration():
    old_count = await old_db.count()
    new_count = await new_db.count()
    assert old_count == new_count, "Migration count mismatch"

# 3. Run in production with rollback option
# Deploy migration script
# Run on staging first
# Get approval
# Run on production
# Keep ability to rollback for 24 hours
```

### Rollback Plan

If issues occur:
1. Stop new code processing
2. Revert to old code
3. Keep new data separate (don't delete)
4. Investigate root cause
5. Fix and re-test before re-attempting

---

## Item 74: Implementation Order

**This is the verified sequence to implement features without breaking dependencies:**

### Phase 1: Foundation (Core Infrastructure)
1. ✅ **Item 1-10**: Models, Database, Auth, Base Routes
2. ✅ **Item 11-15**: Repositories, Services, Middleware
3. ✅ **Item 16-18**: Admission Requirements, Fee Config
4. ✅ **Item 34**: Applicant Portal

### Phase 2: Critical Features (Admissions Workflow)
5. ✅ **Item 61**: Student Lifecycle (Applicant → Student)
6. ✅ **Item 62**: Audit Logging
7. ✅ **Item 63**: Impersonation
8. ✅ **Item 64**: Setup Completeness

### Phase 3: Secondary Features (Officer Dashboards)
9. **Item 46-48**: Finance, Hostel, Library Frontends
10. **Item 51-52**: Alumni, Tenant Admin Portals

### Phase 4: Advanced Features
11. **Item 61**: Complete Student Lifecycle
12. **Item 65**: Module Enablement
13. **Item 66-67**: Frontend Design, Dashboards

### Phase 5: Quality & Hardening
14. **Item 71**: Data Validation
15. **Item 72**: Testing
16. **Item 73**: Migration
17. **Item 75**: Non-Negotiable Requirements

**Why this order:**
- Can't test without Models
- Can't have Admissions without Auth
- Can't have Student Lifecycle without Admissions
- Can't deploy without Audit & Security
- Can't migrate without Tests
- Frontend/UI comes after backend is stable

### Blocked Dependencies

Some items cannot start until others complete:

```
Item 72 (Testing) ← requires Items 1-67 mostly complete
Item 73 (Migration) ← requires Items 1-72 done
Item 74 (Sequence) ← requires understanding Items 1-73
Item 75 (Non-Negotiable) ← continuous requirement throughout
```

---

## Item 75: Non-Negotiable Requirements

These requirements must be satisfied in EVERY implementation, no exceptions:

### Security (Mandatory)

1. **Multi-Tenant Isolation**
   - Every query filters by tenant_id
   - No data crosses tenant boundaries
   - Cross-tenant access attempts logged and denied
   - Status code: 403 Forbidden

2. **Authentication**
   - All endpoints require valid JWT token
   - Tokens validated server-side
   - Tokens expire and refresh
   - Invalid tokens rejected

3. **Authorization**
   - Role-based access control enforced
   - Users only access authorized resources
   - Resource-level checks (can't modify someone else's data)
   - Denials are audited

4. **Audit Logging**
   - All sensitive operations logged
   - Includes: who, what, when, where, why
   - Logs are immutable (append-only)
   - Sensitive data is redacted
   - Logs retained for compliance

5. **Impersonation Controls**
   - Only super admins can impersonate
   - Impersonation is short-lived (30 min max)
   - All impersonation actions audited
   - Clear indication to user if impersonated

### Data Integrity (Mandatory)

6. **Input Validation**
   - All user input validated
   - Invalid input rejected with clear error
   - Data types enforced
   - Length limits enforced
   - Required fields enforced

7. **State Machine Enforcement**
   - Application states can only transition validly
   - Student states cannot skip levels
   - Admission cycles control timeline
   - Invalid transitions rejected

8. **Consistency**
   - Applicant records match Student records
   - No orphaned data
   - Foreign key constraints enforced
   - Duplicate entries prevented

### Availability (Mandatory)

9. **Graceful Degradation**
   - Payment failures don't crash system
   - External API failures don't crash system
   - Database connection issues handled
   - Fallback behaviors defined

10. **Error Handling**
    - All exceptions caught
    - Appropriate HTTP status codes
    - Error messages clear (not exposing internals)
    - Errors logged for debugging

### Compliance (Mandatory)

11. **WASSCE Verification**
    - Manual verification available
    - Never claim automatic verification
    - Verification is auditable
    - Future WAEC API integration possible

12. **Sensitive Operations**
    - Payment verified against Paystack
    - Grades cannot be self-modified
    - Enrollment requires payment
    - Role changes require approval

### Performance (Mandatory)

13. **Response Time**
    - API endpoints < 1 second (p95)
    - Dashboard load < 3 seconds
    - No N+1 queries
    - Indexes on frequently queried fields

14. **Capacity**
    - System handles 10x expected load
    - Database connection pooling configured
    - Rate limiting enforced
    - No resource exhaustion possible

### Testing (Mandatory)

15. **Critical Path Coverage**
    - Authentication: 100% tested
    - Authorization: 100% tested
    - Tenant Isolation: 100% tested
    - Payment: 100% tested
    - Admissions: 100% tested

16. **Negative Tests**
    - Invalid input: tested
    - Cross-tenant access: tested
    - Expired tokens: tested
    - Invalid state transitions: tested
    - Concurrent requests: tested

### Documentation (Mandatory)

17. **API Documentation**
    - Every endpoint documented
    - Request/response examples
    - Error codes explained
    - Authentication requirements clear

18. **Architecture Documentation**
    - System design documented
    - Data models documented
    - Security architecture documented
    - Deployment procedures documented

---

## Verification Checklist

Use this to verify complete implementation before deployment:

- [ ] All endpoints have authentication
- [ ] All endpoints filter by tenant_id
- [ ] All data modifications are audited
- [ ] All state transitions are validated
- [ ] All input is validated
- [ ] All errors are caught
- [ ] All sensitive data is encrypted
- [ ] All external APIs have fallback behavior
- [ ] All critical paths have tests (>80% coverage)
- [ ] All tests pass on CI/CD
- [ ] All security requirements met
- [ ] All performance requirements met
- [ ] All documentation complete
- [ ] All deployments reversible

---

## Running the Full Test Suite

```bash
# Install dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run all tests with coverage
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html -v

# Check coverage report
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows

# Run only critical path tests for fast feedback
pytest tests/test_critical_paths.py -v

# Run specific test category
pytest tests/test_critical_paths.py::TestTenantIsolation -v

# Run with database profiling
pytest tests/ -v --durations=10  # Show 10 slowest tests
```

---

## Next Steps

After implementing all Items (1-75):

1. Run full test suite until 100% critical path coverage
2. Execute staging deployment with production data (anonymized)
3. Run load tests
4. Security audit by external team
5. User acceptance testing with client
6. Gradual production rollout (10% → 25% → 50% → 100%)
7. Monitor production metrics
8. Keep on-call support for 2 weeks post-deployment

---

**System is production-ready only when all Items 1-75 are complete and all non-negotiable requirements are verified.**
