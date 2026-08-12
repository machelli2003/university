# EUMP Backend - Enterprise University Management Platform

Multi-tenant university management backend for Ghanaian/African universities.

## Stack
- Python 3.11+, FastAPI
- MongoDB (via Motor + Beanie ODM)
- Redis + Celery (background jobs)
- Paystack (payments, test keys)
- Clean Architecture: domain → application → infrastructure → presentation

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
