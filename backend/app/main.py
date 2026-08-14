import logging
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.config import get_settings
from app.infrastructure.database.connection import init_db, close_db
from app.infrastructure.middleware.authorization_middleware import TenantIsolationMiddleware
from app.infrastructure.middleware.rate_limit import RateLimitMiddleware
from app.infrastructure.middleware.distributed_rate_limit import (
    DistributedRateLimitMiddleware, SessionCleanupMiddleware
)
from app.exceptions import DomainException, domain_exception_handler

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # read body for logging (safe for downstream in Starlette/FastAPI)
        try:
            body_bytes = await request.body()
        except Exception:
            body_bytes = b""

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        client_host = request.client.host if request.client else None
        logging.getLogger("audit").info(
            f"{request_id} {request.method} {request.url.path} from {client_host or 'unknown'}"
        )

        # Persist an audit record (best-effort, do not block response on failure)
        try:
            from app.infrastructure.database.repositories.audit_repository import AuditRepository
            import json

            repo = AuditRepository()
            details = {
                "method": request.method,
                "path": request.url.path,
                "query": dict(request.query_params),
            }
            if body_bytes:
                try:
                    details["body"] = json.loads(body_bytes.decode("utf-8"))
                except Exception:
                    details["body"] = body_bytes.decode("utf-8", errors="replace")[:2000]

            # write minimal audit entry; performed_by/tenant may be unset here
            await repo.create({
                "tenant_id": getattr(request.state, "tenant_id", None),
                "event_type": "http_request",
                "entity_type": "request",
                "entity_id": request_id,
                "action": f"{request.method} {request.url.path}",
                "performed_by": getattr(request.state, "user_id", None),
                "details": details,
                "ip_address": client_host,
                "request_id": request_id,
            })
        except Exception:
            logging.getLogger("audit").exception("Failed to persist audit log")

        return response

from app.presentation.api.v1.auth import routes as auth_routes
from app.presentation.api.v1.admissions import routes as admissions_routes
from app.presentation.api.v1.finance import routes as finance_routes
from app.presentation.api.v1.exam import routes as exam_routes
from app.presentation.api.v1.admin import routes as admin_routes
from app.presentation.api.v1.admin.setup_activation_routes import router as setup_activation_router
from app.presentation.api.v1.admissions.admissions_workflow_routes import router as admissions_workflow_router
from app.presentation.api.v1.admissions.officer_dashboards_routes import router as officer_dashboards_router
from app.presentation.api.v1.onboarding import routes as onboarding_routes
from app.presentation.api.v1.academic import routes as academic_routes
from app.presentation.api.v1.accommodation import routes as accommodation_routes
from app.presentation.api.v1.library import routes as library_routes
from app.presentation.api.v1.hr import routes as hr_routes
from app.presentation.api.v1.health import routes as health_routes
from app.presentation.api.v1.research import routes as research_routes
from app.presentation.api.v1.alumni import routes as alumni_routes
from app.presentation.api.v1.communication import routes as communication_routes
from app.presentation.api.v1.document import routes as document_routes
from app.presentation.api.v1.workflow import routes as workflow_routes
from app.presentation.api.v1.inventory import routes as inventory_routes
from app.presentation.api.v1.analytics import routes as analytics_routes
from app.presentation.api.v1.student import routes as student_routes
from app.presentation.api.v1.lecturer import routes as lecturer_routes
from app.presentation.api.v1.lecturer import course_materials as lecturer_course_materials
from app.presentation.api.v1.attendance import routes as attendance_routes
from app.presentation.api.v1.parents import routes as parents_routes
from app.presentation.api.v1.counseling import routes as counseling_routes
from app.presentation.api.v1.applicant_portal import routes as applicant_portal_routes
from app.presentation.api.v1.admissions import wassce_verification_routes as wassce_verification
from app.presentation.api.v1.staff import staff_assignment_routes as staff_assignment_routes
from app.presentation.api.v1.dashboards import admissions_officer_dashboard as admissions_officer_dashboard
from app.presentation.api.v1.dashboards import registrar_dashboard as registrar_dashboard
from app.presentation.api.v1.dashboards import lecturer_dashboard as lecturer_dashboard
from app.presentation.api.v1.dashboards import hod_dashboard as hod_dashboard
from app.presentation.api.v1.dashboards import dean_dashboard as dean_dashboard
from app.presentation.api.v1.dashboards import finance_dashboard as finance_dashboard
from app.presentation.api.v1.dashboards import hostel_dashboard as hostel_dashboard
from app.presentation.api.v1.dashboards import librarian_dashboard as librarian_dashboard
from app.presentation.api.v1.dashboards import exam_dashboard as exam_dashboard
from app.presentation.api.v1.dashboards import student_dashboard as student_dashboard
from app.presentation.api.v1.dashboards import alumni_dashboard as alumni_dashboard
from app.presentation.api.v1.dashboards import tenant_admin_dashboard as tenant_admin_dashboard
from app.presentation.api.v1.dashboards import super_admin_dashboard as super_admin_dashboard
from app.presentation.api.v1.audit import audit_routes as audit_routes
from app.presentation.api.v1.officer import finance_dashboard as finance_dashboard_routes
from app.presentation.api.v1.officer import dashboards as officer_dashboards_routes

app = FastAPI(
    title="EUMP API",
    description="Enterprise University Management Platform",
    version="1.0.0"
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuditMiddleware)
app.add_middleware(TenantIsolationMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(DistributedRateLimitMiddleware)  # Item 75: Distributed rate limiting
app.add_middleware(SessionCleanupMiddleware)  # Item 75: Session cleanup
app.add_exception_handler(DomainException, domain_exception_handler)

@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(onboarding_routes.router, prefix="/api/v1/onboarding", tags=["onboarding"])
app.include_router(admissions_routes.router, prefix="/api/v1/admissions", tags=["admissions"])
app.include_router(finance_routes.router, prefix="/api/v1/finance", tags=["finance"])
app.include_router(exam_routes.router, prefix="/api/v1/exam", tags=["exam"])
app.include_router(admin_routes.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(setup_activation_router, tags=["Setup & Activation"])
app.include_router(admissions_workflow_router, tags=["Admissions Workflow"])
app.include_router(officer_dashboards_router, tags=["Officer Dashboards"])
app.include_router(academic_routes.router, prefix="/api/v1/academic", tags=["academic"])
app.include_router(accommodation_routes.router, prefix="/api/v1/accommodation", tags=["accommodation"])
app.include_router(library_routes.router, prefix="/api/v1/library", tags=["library"])
app.include_router(hr_routes.router, prefix="/api/v1/hr", tags=["hr"])
app.include_router(health_routes.router, prefix="/api/v1/health-services", tags=["health"])
app.include_router(research_routes.router, prefix="/api/v1/research", tags=["research"])
app.include_router(alumni_routes.router, prefix="/api/v1/alumni", tags=["alumni"])
app.include_router(communication_routes.router, prefix="/api/v1/communication", tags=["communication"])
app.include_router(document_routes.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(workflow_routes.router, prefix="/api/v1/workflow", tags=["workflow"])
app.include_router(inventory_routes.router, prefix="/api/v1/inventory", tags=["inventory"])
app.include_router(analytics_routes.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(student_routes.router, prefix="/api/v1/students", tags=["students"])
app.include_router(lecturer_routes.router, prefix="/api/v1/lecturer", tags=["lecturer"])
app.include_router(lecturer_course_materials.router, prefix="/api/v1/lecturer", tags=["lecturer"])
app.include_router(attendance_routes.router, prefix="/api/v1/attendance", tags=["attendance"])
app.include_router(parents_routes.router, prefix="/api/v1", tags=["parents"])
app.include_router(counseling_routes.router, prefix="/api/v1", tags=["counseling"])
app.include_router(applicant_portal_routes.router, prefix="/api/v1", tags=["applicant-portal"])
app.include_router(wassce_verification.router, prefix="/api/v1", tags=["wassce-verification"])
app.include_router(staff_assignment_routes.router, tags=["staff-assignments"])
app.include_router(admissions_officer_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(registrar_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(lecturer_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(hod_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(dean_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(finance_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(hostel_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(librarian_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(exam_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(student_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(alumni_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(tenant_admin_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(super_admin_dashboard.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(audit_routes.router, prefix="/api/v1", tags=["audit"])
app.include_router(finance_dashboard_routes.router, prefix="/api/v1", tags=["dashboards"])
app.include_router(officer_dashboards_routes.router, prefix="/api/v1", tags=["dashboards"])

@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.ENVIRONMENT}

@app.get("/api/v1/health")
async def api_health():
    return {"status": "ok", "environment": settings.ENVIRONMENT}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
