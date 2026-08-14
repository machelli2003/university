# Item 73: MIGRATION STRATEGY

## Overview
This system is designed for existing institutions. Never delete legacy code immediately. Use a careful, staged migration approach.

## Migration Phases

### Phase 1: Parallel Running (Weeks 1-4)
**Goal: Run new system alongside legacy without disruption**

```
Legacy System          New System
(PROD)          ──→   (STAGING)
↓                          ↓
Live Data              Shadow Data
Students               Same Students
Applications           Same Applications
Transactions           Same Transactions
```

**Actions:**
1. Deploy new system on separate server
2. Mirror data from legacy to new system nightly
3. Run test suites on new system data
4. Verify calculations match legacy (fee calculations, GPA, rankings)
5. Let new system run silently without traffic

**Timeline:** 4 weeks for edge case discovery

### Phase 2: Validation (Weeks 5-8)
**Goal: Ensure new system handles all scenarios**

**Data Integrity Checks:**
```python
# backend/scripts/validate_migration.py
- Student record counts match
- Application counts match
- Payment totals match
- Course enrollment totals match
- Grade calculations identical
- GPA calculations identical
- Academic standing calculations identical
- Ranking algorithms identical
```

**Test Scenarios:**
- [ ] 1000+ concurrent applicants
- [ ] Payment reconciliation with Paystack
- [ ] WASSCE verification workflow
- [ ] Course registration conflicts
- [ ] Hall allocation algorithms
- [ ] Grade entry and transcript generation
- [ ] Fee waiver processing
- [ ] Multi-tenant isolation

**Validation Output:**
```
✅ Student counts: 5,234 (legacy) vs 5,234 (new) = MATCH
✅ Applications: 8,921 (legacy) vs 8,921 (new) = MATCH
⚠️  Payments: $2,345,678 (legacy) vs $2,345,612 (new) = MISMATCH
   → Investigate 66 cents difference → Found rounding in interest calc
✅ Courses: 456 (legacy) vs 456 (new) = MATCH
```

### Phase 3: Cutover Preparation (Week 9)
**Goal: Prepare for live migration**

**1. Final Data Sync:**
```bash
# Full export from legacy
mysqldump --all-databases > legacy_final.sql

# Import to MongoDB
python backend/scripts/migrate_from_sql.py legacy_final.sql

# Validate import
python backend/scripts/validate_migration.py
```

**2. Backup Strategy:**
```bash
# Before cutover: Full backup both systems
aws s3 sync /data/legacy s3://university-backups/legacy-pre-cutover/
aws s3 sync /data/mongodb s3://university-backups/new-pre-cutover/

# Keep backups for 30 days
```

**3. Rollback Plan:**
```bash
# If new system fails within 1 hour:
# 1. Route traffic back to legacy
# 2. Latest legacy data is unchanged (read-only during cutover)
# 3. Notify users of delay

# If failure after 1 hour:
# 1. Restore from backup
# 2. Manual reconciliation
# 3. Extended maintenance window
```

### Phase 4: Live Migration (1-2 Hours)
**Goal: Switch traffic from legacy to new**

**Cutover Steps:**

```
00:00 - Start cutover window
       └─ Notify all users of maintenance (email, SMS)

00:05 - Put legacy system in READ-ONLY mode
       └─ All write operations redirect to new system
       └─ Reads still served from legacy (faster)

00:10 - Start background sync
       └─ Copy final 5 minutes of new system data
       └─ Reconcile any differences

00:30 - Switch API endpoint to new system
       └─ Point api.university.edu → new-api-server
       └─ Keep legacy-api.university.edu for fallback

00:35 - Run health checks
       └─ Verify new system responding
       └─ Verify database accessible
       └─ Verify file storage working

00:45 - Notify users of successful migration
       └─ Send confirmation email
       └─ Display banner in UI

01:00 - Keep legacy system running for 7 days read-only
       └─ Allow anyone to verify their data migrated correctly
       └─ If issues found, can roll back
```

**Monitoring During Cutover:**

```python
# Endpoints to monitor
GET  /api/v1/health                    → Should return 200
GET  /api/v1/students/me               → Should return student data
POST /api/v1/admissions/apply          → Should create application
POST /api/v1/finance/payments/initiate → Should work via Paystack
```

**Error Handling:**

| Error | Action |
|-------|--------|
| Database connection fails | Rollback to legacy |
| Payment processing fails | Route to Paystack directly |
| File upload fails | Use temporary S3 bucket |
| Auth fails | Use cached token from old system |

### Phase 5: Post-Migration (Weeks 10-12)
**Goal: Monitor, optimize, then decommission legacy**

**Week 10:**
- Monitor error logs for issues
- Performance baseline (response times, DB queries)
- User feedback collection
- Bug fixes on new system
- Legacy system in standby (not actively used)

**Week 11:**
- Performance optimization (indexes, caching)
- Stress test with prod load simulator
- Load balancing tuning
- Legacy system monitoring (metrics only)

**Week 12:**
- Final validation that legacy data can be deleted
- Archive legacy to cold storage (60-day retention)
- Decommission legacy hardware
- Update documentation

```bash
# Archive legacy data
aws s3 sync /data/legacy s3://university-backups/legacy-archive/
rm -rf /data/legacy  # Only after confirmed archived

# Shut down legacy services
systemctl stop mysql
systemctl disable mysql
```

## Data Transformation Mapping

### Student Records

**Legacy (SQL):**
```sql
SELECT
  students.id,
  students.first_name,
  students.last_name,
  students.student_id,
  admissions.status,
  admissions.allocated_programme,
  courses.course_id,
  grades.grade
FROM students
JOIN admissions ON students.id = admissions.student_id
JOIN courses ON students.id = courses.student_id
JOIN grades ON courses.id = grades.course_id
```

**New (MongoDB):**
```json
{
  "_id": ObjectId("..."),
  "tenant_id": "KNUST",
  "user_id": "...",
  "student_id": "KNUST-2024-0001",
  "first_name": "John",
  "last_name": "Doe",
  "status": "active",
  "programme_id": ObjectId("..."),
  "registered_courses": [
    {
      "course_id": "COMP101",
      "grade": "A",
      "points": 4.0
    }
  ]
}
```

**Migration Script:**
```python
# backend/scripts/migrate_students.py
async def migrate_students(legacy_conn, new_db):
    for legacy_student in legacy_conn.execute("SELECT * FROM students"):
        # Transform data
        student_doc = {
            "tenant_id": "KNUST",  # Resolve from legacy institution
            "user_id": str(legacy_student['user_id']),
            "student_id": legacy_student['student_id'],
            "first_name": legacy_student['first_name'],
            # ... other fields
        }
        
        # Validate
        if not validate_student(student_doc):
            log_migration_error(student_doc)
            continue
        
        # Insert
        await new_db.students.insert_one(student_doc)
        
        # Verify
        assert await verify_migration(legacy_student, student_doc)
```

## Rollback Procedure

**If cutover fails:**

```bash
#!/bin/bash
# rollback.sh - Executed if new system unreachable

# 1. Switch DNS back to legacy
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567 \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.university.edu",
        "Type": "CNAME",
        "TTL": 60,
        "ResourceRecords": [{"Value": "legacy-api.university.edu"}]
      }
    }]
  }'

# 2. Notify admins
curl -X POST https://slack-webhook-url \
  -d '{"text":"🚨 MIGRATION ROLLBACK: Traffic restored to legacy system"}'

# 3. Wait for propagation
sleep 300

# 4. Verify legacy responding
curl -s https://api.university.edu/health | jq .

# 5. Document incident
echo "Rollback completed at $(date)" >> /var/log/migration.log
```

## Checklist

- [ ] Legacy system backed up
- [ ] New system tested with production data
- [ ] All calculations validated (fees, GPA, rankings)
- [ ] Payment processing verified (test transaction)
- [ ] File uploads verified (test document)
- [ ] Multi-tenant isolation verified
- [ ] Audit logging working (can see all events)
- [ ] Email notifications working (password reset, application status)
- [ ] SMS notifications working (payment confirmation, admission)
- [ ] Rate limiting configured
- [ ] Monitoring/alerting set up (CPU, memory, DB connections)
- [ ] Load balancer configured
- [ ] SSL certificates valid
- [ ] Firewall rules updated
- [ ] Database replication verified
- [ ] Backup schedule verified
- [ ] Users notified of maintenance window
- [ ] Support team briefed on new system

## Validation Queries

```python
# backend/scripts/validate_migration.py

async def validate_all_data():
    checks = [
        ("Student counts", validate_student_counts),
        ("Application counts", validate_application_counts),
        ("Payment totals", validate_payment_totals),
        ("Course totals", validate_course_totals),
        ("GPA calculations", validate_gpa_calculations),
        ("Ranking calculations", validate_ranking_calculations),
        ("Tenant isolation", validate_tenant_isolation),
        ("User role matrix", validate_user_roles),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            result = await check_func()
            results[name] = "✅ PASS" if result else "❌ FAIL"
        except Exception as e:
            results[name] = f"⚠️ ERROR: {str(e)}"
    
    return results
```

---

# Item 74: IMPLEMENTATION ORDER

## Verified Sequencing

The following order MUST be maintained to ensure dependencies are satisfied:

### Block 1: Infrastructure (Items 1-3)
**Dependency: None**
- [ ] Item 1: Database Schema (MongoDB collections)
- [ ] Item 2: Authentication (JWT tokens, password hashing)
- [ ] Item 3: Multi-tenancy Setup

### Block 2: Core Setup (Items 4-15)
**Dependency: Block 1**
- [ ] Item 4: University Onboarding Workflow
- [ ] Item 5: Faculty/Department Configuration
- [ ] Item 6: Programme Configuration
- [ ] Item 7: Course Configuration
- [ ] Item 8: Staff Assignment
- [ ] Item 9: Academic Calendar
- [ ] Item 10: Student ID Generation
- [ ] Item 11: Staff ID Generation
- [ ] Item 12: Applicant ID Generation
- [ ] Item 13: Academic Standing Rules
- [ ] Item 14: Module Enablement Template
- [ ] Item 15: Tenant Subscription Tiers

### Block 3: Admissions (Items 16-35)
**Dependency: Block 2**
- [ ] Item 16: Programme Admission Requirements ✅
- [ ] Item 17: WASSCE Verification ✅
- [ ] Item 18: Application Fee Configuration ✅
- [ ] Item 19: Application Form Builder
- [ ] Item 20: Document Management
- [ ] Item 21: Payment Gateway (Paystack)
- [ ] Item 22: Eligibility Engine
- [ ] Item 23: Ranking Algorithm
- [ ] Item 24: Programme Allocation
- [ ] Item 25: Waitlist Management
- [ ] Item 26: Offer Generation & Publishing
- [ ] Item 27: Admission Letter Templates
- [ ] Item 28: Batch Operations
- [ ] Item 29: Notifications (Email/SMS)
- [ ] Item 30: Applicant Conversion to Student
- [ ] Item 31: Admissions Reporting
- [ ] Item 32: Admissions Dashboard
- [ ] Item 33: WASSCE Manual Verification UI
- [ ] Item 34: Applicant Portal ✅
- [ ] Item 35: Applicant Progress Tracking

### Block 4: Student Management (Items 36-45)
**Dependency: Block 3**
- [ ] Item 36: Student Registration Portal
- [ ] Item 37: Course Registration
- [ ] Item 38: Attendance Tracking
- [ ] Item 39: Results Entry & Approval
- [ ] Item 40: Transcript Generation
- [ ] Item 41: Academic Standing Monitoring
- [ ] Item 42: Deferment Workflow
- [ ] Item 43: Suspension & Withdrawal
- [ ] Item 44: Graduation Eligibility
- [ ] Item 45: Alumni Conversion

### Block 5: Officer Dashboards (Items 46-60)
**Dependency: Blocks 2-4**
- [ ] Item 46: Finance Officer Dashboard
- [ ] Item 47: Hostel Admin Dashboard
- [ ] Item 48: Library Dashboard
- [ ] Item 49: Academic Staff Portal
- [ ] Item 50: HR Management Portal
- [ ] Item 51: Alumni Portal
- [ ] Item 52: Tenant Admin Dashboard
- [ ] Item 53: Dean Dashboard
- [ ] Item 54: HOD Dashboard
- [ ] Item 55: Registrar Dashboard
- [ ] Item 56: Exam Officer Dashboard
- [ ] Item 57: Accounts Officer Dashboard
- [ ] Item 58: Admissions Officer Dashboard
- [ ] Item 59: Health Center Dashboard
- [ ] Item 60: Research Coordinator Dashboard

### Block 6: Critical Systems (Items 61-70)
**Dependency: Blocks 1-5**
- [ ] Item 61: Student Lifecycle ✅
- [ ] Item 62: Audit Logging ✅
- [ ] Item 63: Impersonation ✅
- [ ] Item 64: Setup Completeness Engine ✅
- [ ] Item 65: Module Enablement ✅
- [ ] Item 66: Frontend Design System
- [ ] Item 67: Dashboard Component Library
- [ ] Item 68: Role-Based Access Control
- [ ] Item 69: Data Validation Framework
- [ ] Item 70: Error Handling Strategy

### Block 7: Quality & Deployment (Items 71-76)
**Dependency: Blocks 1-6**
- [ ] Item 71: Data Validation ✅
- [ ] Item 72: Testing Requirements ✅
- [ ] Item 73: Migration Strategy ✅
- [ ] Item 74: Implementation Order ✅
- [ ] Item 75: Non-Negotiable Requirements (covered in items)
- [ ] Item 76: Definition of Done

## Critical Path

The fastest path to full functionality:

```
1-3 (Infrastructure)
  ↓
4-15 (Setup)
  ↓
16-35 (Admissions) ← CRITICAL: Must complete before students exist
  ↓
36-45 (Student Management)
  ↓
46-60 (Officer Dashboards)
  ↓
61-70 (Critical Systems)
  ↓
71-76 (Quality)
```

**Total estimated time: 16 weeks (4 months)**

## Parallel Work Streams

These can be worked on in parallel:

- **Stream A:** Items 1-15 (Setup) — Backend Engineers
- **Stream B:** Items 46-60 (Dashboards) — Frontend Engineers (after APIs available)
- **Stream C:** Items 71-76 (Testing) — QA Engineers

## Dependency Graph

```
Item 16 ──→ Item 22 ──→ Item 23 ──→ Item 24
(Requirements) (Eligibility)  (Ranking)  (Allocation)
                                         ↓
                                    Item 26 (Offers)
                                         ↓
                                    Item 30 (Enrollment)
                                         ↓
                                  Item 36-40 (Academics)
                                         ↓
                                  Item 44 (Graduation)
                                         ↓
                                    Item 45 (Alumni)
```

## Blocking Dependencies

Items that CANNOT start until prerequisites complete:

| Item | Blocked By | Reason |
|------|-----------|--------|
| 19 (Form Builder) | 18 (Fees) | Must define application fields including fees |
| 22 (Eligibility) | 16 (Requirements) | Need requirement specs to evaluate |
| 24 (Allocation) | 23 (Ranking) | Must rank before allocating |
| 30 (Enrollment) | 26 (Offers) | Must have offers before enrollment |
| 36 (Registration) | 30 (Enrollment) | Must enroll before registering |
| 39 (Results) | 37 (Registration) | Must register before entering results |
| 41 (Standing) | 39 (Results) | Must have results to assess standing |
| 44 (Graduation) | 41 (Standing) | Must meet academic standing |
| 46-60 (Dashboards) | 16-40 (Backend APIs) | Dashboards call APIs |

## Checkpoints

Verify completion before proceeding:

**After Block 3 (Admissions):**
```
✅ Can apply for admission
✅ Can upload documents
✅ Can pay application fee
✅ Can receive offer letter
✅ Can accept offer
✅ Becomes student successfully
```

**After Block 4 (Student Management):**
```
✅ Can register for courses
✅ Can check attendance
✅ Can view grades
✅ Can download transcript
✅ Can see academic standing
```

**After Block 5 (Dashboards):**
```
✅ Finance officer can see fee analytics
✅ Hostel admin can allocate rooms
✅ Library staff can manage books
✅ Deans see faculty statistics
✅ Registrar sees enrollment trends
```

**After Block 6 (Critical Systems):**
```
✅ All operations audited
✅ Admins can impersonate (support)
✅ Modules can be enabled/disabled
✅ Setup validation prevents incomplete config
✅ Student lifecycle works end-to-end
```

---

## Success Criteria

✅ **Feature Complete:**  All 76 items implemented

✅ **Test Coverage:**  >80% of critical paths tested

✅ **Performance:**  API response <200ms (p95)

✅ **Reliability:**  99.9% uptime over 30 days

✅ **Security:**  All OWASP top 10 mitigated

✅ **Multi-tenant:** No cross-tenant data leaks

✅ **Data Integrity:** All calculations validated against legacy

✅ **User Acceptance:** >95% of staff trained and signed off
