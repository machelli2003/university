# EUMP Frontend

React + TypeScript + Tailwind frontend for the Enterprise University Management Platform.

## Stack
- Vite + React 18 + TypeScript
- Tailwind CSS (cocoa/brass/paper design tokens)
- TanStack Query (server state)
- Zustand (auth + local app state, persisted)
- React Hook Form + Zod (forms/validation)
- Axios (API client with auto token-refresh interceptor)

## Setup

```bash
npm install
cp .env.example .env
# edit .env: set VITE_API_BASE_URL to your running backend, e.g. http://localhost:8000/api/v1

npm run dev
```

Runs at `http://localhost:5173`. Requires the EUMP backend running (see backend README) and seeded
with test data (`python -m scripts.seed_data` in the backend).

## What's implemented

**Auth**
- Login / Register pages
- JWT access + refresh token flow with automatic silent refresh on 401
- Persisted session (Zustand + localStorage)
- Role-based route guarding (`PrivateRoute`)

**Applicant flow** (`/apply/status`)
- Create application
- Submit programme choice + index number
- Manually enter WASSCE results (since there's no live WAEC API yet — matches backend's
  manual-entry-then-admin-approval workflow)
- View live application status
- Accept admission offer

**Manual verification note**
- Admissions officers review manually submitted applicant results via `/officer/pending-results`
- This is the current verification queue until an external WAEC API is integrated

**SMS note**
- SMS integration is currently paused and stubbed; email/SMS stubs are used for development only

**Admissions Officer flow** (role-gated: `admissions_officer`, `registrar`, `university_admin`, `super_admin`)
- `/officer/pending-results` — review and approve/reject manually submitted results
- `/officer/applicants` — browse/filter all applicants by status
- `/officer/processing` — run the pipeline: bulk eligibility check → rank by programme → allocate → publish offers

This mirrors the backend's tested end-to-end flow (see backend README's "Full Admissions Test Flow").

## Test credentials (after seeding the backend)

| Role | Email | Password |
|---|---|---|
| Admissions Officer | officer@test.com | Officer123! |
| Applicant | applicant@test.com | Applicant123! |

Register a fresh applicant via `/register`, or use the seeded one above.

## Still to build

- Dashboards/UI for the other 20 backend modules (Finance/Paystack checkout, Academic course
  registration, Exam grading, Accommodation, Library, HR, Health, Research, Alumni,
  Communication, Documents, Workflow, Inventory, Analytics)
- University tenant onboarding flows for super-admin and university-admin workflows
- Student portal (post-enrollment) — course registration, grades, transcripts, fee payment
- Admin dashboards with charts (Recharts)
- File uploads (documents, profile photos) — backend currently stubs S3
- Real-time notifications (backend has no WebSocket layer yet)

## Design system

Colors: `ink` (near-black text), `cocoa` (primary brand scale), `brass` (accent/warning), `paper`
(background). Fonts: Fraunces (display/headings), Public Sans (UI/body), IBM Plex Mono (data/codes).
Matches the palette used across Machelli's other Ghana-context platforms (school management system,
CHED portal).
