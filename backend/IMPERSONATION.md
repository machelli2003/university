# Impersonation (Acting-Tenant) Flow

Overview

This project provides a controlled impersonation (acting-tenant) flow that lets `super_admin` users temporarily assume a tenant context. The flow is explicit, audited, and time-limited.

Frontend behavior

- The sidebar hides tenant-scoped pages for `super_admin` until a tenant is selected via the `TenantSwitcher` (frontend component).
- When a `super_admin` selects a tenant, the frontend calls `POST /api/v1/admin/impersonate?tenant_id=<id>` to request a short-lived tenant-scoped access token.
- The frontend stores the original tokens, replaces the access token with the impersonation token, and sets `selectedTenantId` in `authStore`.
- When the `super_admin` clears the tenant selection ("All tenants"), the frontend calls `POST /api/v1/admin/impersonate/stop` to end impersonation, restore original tokens, and clear `selectedTenantId`.

Backend behavior

- `POST /api/v1/admin/impersonate?tenant_id=<id>` (requires `super_admin`):
  - Validates tenant existence.
  - Returns a short-lived JWT with `tenant_id` claim and `exp` (30 minutes by default).
  - Creates an audit event `impersonation_started` with details and `performed_by` the super_admin.
  - Increments a Redis metric `impersonation:started` (if Redis configured).

- `POST /api/v1/admin/impersonate/stop` (requires `super_admin`):
  - Creates an audit event `impersonation_stopped`.
  - Increments a Redis metric `impersonation:stopped` (if Redis configured).

- `GET /api/v1/admin/impersonations?limit=100` (requires `super_admin`):
  - Returns recent impersonation audit events for monitoring and review.

Token handling

- Access tokens issued via impersonation include a `tenant_id` claim.
- The `get_current_user` dependency will respect the `tenant_id` claim for `super_admin` users and override the returned `User.tenant_id` for the request scope only (does not persist to DB).
- Impersonation tokens are intentionally short-lived (30 minutes). Refresh tokens are not issued for impersonation tokens.

Security & Audit

- All impersonation actions are audited in the `audits` collection (`impersonation_started` and `impersonation_stopped`).
- For production, ensure Redis is available and configure Prometheus/alerts to watch `impersonation:started` and `impersonation:stopped` metrics.
- Consider additional policies:
  - Require MFA for `super_admin` to start impersonation.
  - Implement time-limited admin sessions and re-confirmation dialogs before impersonation.
  - Restrict IP ranges or add Just-In-Time (JIT) approvals for highly sensitive tenants.

Operational recommendations

- Add Prometheus exporter or push metrics to your monitoring system where the Redis counters are incremented. Alternatively, emit metrics directly from the API layer to a monitoring client.
- Create alerting rules for unusual impersonation activity (e.g., many impersonations in short time, impersonation of sensitive tenants).
- Regularly review impersonation audit logs and restrict access to audit listing endpoints.

Files changed

- Backend: `app/presentation/api/v1/admin/routes.py` — added impersonation endpoints and Redis metric increments.
- Backend: `app/dependencies.py` — respect `tenant_id` claim in tokens for `super_admin` impersonation context.
- Frontend: `src/components/layout/AppShell.tsx` — hide tenant pages until tenant selected.
- Frontend: `src/components/ui/TenantSwitcher.tsx` — requests impersonation and stops impersonation.
- Frontend: `src/store/authStore.ts` — supports storing original tokens and impersonation helpers.

Usage example (curl)

1. Login as super_admin:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' -d '{"email":"super@example.com","password":"Secret"}'
```

2. Start impersonation:

```bash
curl -X POST "http://localhost:8000/api/v1/admin/impersonate?tenant_id=<tenantId>" -H "Authorization: Bearer <SUPER_ADMIN_TOKEN>"
```

3. Use returned `access_token` for tenant-scoped requests.

4. Stop impersonation:

```bash
curl -X POST "http://localhost:8000/api/v1/admin/impersonate/stop" -H "Authorization: Bearer <SUPER_ADMIN_TOKEN>"
```
