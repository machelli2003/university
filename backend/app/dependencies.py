from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.application.auth.login import AuthService
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.applicant_repository import (
    ApplicantRepository, ApplicantResultRepository
)
from app.infrastructure.database.repositories.student_repository import StudentRepository
from app.infrastructure.database.repositories.course_repository import (
    CourseRepository, ProgramRepository, FacultyRepository, DepartmentRepository
)
from app.infrastructure.database.repositories.payment_repository import PaymentRepository, ScholarshipRepository, FeeStructureRepository
from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.infrastructure.database.repositories.grade_repository import GradeRepository
from app.infrastructure.database.repositories.attendance_repository import AttendanceRepository
from app.infrastructure.database.repositories.registration_repository import RegistrationRepository
from app.infrastructure.database.repositories.academic_calendar_repository import AcademicCalendarRepository
from app.infrastructure.database.repositories.document_repository import DigitalSignatureRepository
from app.domain.admissions.eligibility_engine import EligibilityEngine
from app.domain.admissions.merit_ranking import MeritRankingEngine
from app.domain.admissions.allocation_engine import AllocationEngine
from app.domain.admissions.waec_service import ManualResultsEntryService, WAECService
from app.domain.exam.grade_calculator import GradeCalculator
from app.infrastructure.external_services.email_service import EmailService, SMSService
from app.infrastructure.external_services.s3_service import S3Service
from app.infrastructure.database.repositories.audit_repository import AuditRepository
from app.infrastructure.database.repositories.university_application_repository import UniversityApplicationRepository, IdentifierSequenceRepository
from app.application.identifiers.identifier_service import IdentifierService
from app.infrastructure.models.user import User
from app.infrastructure.database.connection import get_db

security = HTTPBearer()

# --- Repository providers ---
def get_user_repo() -> UserRepository:
    return UserRepository()

def get_applicant_repo() -> ApplicantRepository:
    return ApplicantRepository()

def get_applicant_result_repo() -> ApplicantResultRepository:
    return ApplicantResultRepository()

def get_student_repo() -> StudentRepository:
    return StudentRepository()

def get_course_repo() -> CourseRepository:
    return CourseRepository()

def get_program_repo() -> ProgramRepository:
    return ProgramRepository()

def get_payment_repo() -> PaymentRepository:
    return PaymentRepository()

def get_fee_structure_repo() -> FeeStructureRepository:
    return FeeStructureRepository()

# Backward-compatible alias for older finance dashboard imports.
def get_fee_repo() -> FeeStructureRepository:
    return FeeStructureRepository()

def get_scholarship_repo() -> ScholarshipRepository:
    return ScholarshipRepository()

def get_tenant_repo() -> TenantRepository:
    return TenantRepository()

def get_grade_repo() -> GradeRepository:
    return GradeRepository()

def get_registration_repo() -> RegistrationRepository:
    return RegistrationRepository()

def get_academic_calendar_repo() -> AcademicCalendarRepository:
    return AcademicCalendarRepository()


def get_application_fee_repo() -> "ApplicationFeeRepository":
    from app.infrastructure.database.repositories.application_fee_repository import ApplicationFeeRepository
    return ApplicationFeeRepository()

def get_attendance_repo() -> AttendanceRepository:
    return AttendanceRepository()

def get_digital_signature_repo() -> DigitalSignatureRepository:
    return DigitalSignatureRepository()

# --- Service providers ---
def get_auth_service(user_repo: UserRepository = Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo)

def get_eligibility_engine() -> EligibilityEngine:
    return EligibilityEngine()

def get_ranking_engine() -> MeritRankingEngine:
    return MeritRankingEngine()

def get_allocation_engine() -> AllocationEngine:
    return AllocationEngine()

def get_manual_results_service() -> ManualResultsEntryService:
    return ManualResultsEntryService()

def get_waec_service() -> WAECService:
    return WAECService()

def get_email_service() -> EmailService:
    return EmailService()

def get_sms_service() -> SMSService:
    return SMSService()

def get_s3_service() -> S3Service:
    return S3Service()

def get_audit_repo() -> AuditRepository:
    return AuditRepository()


def get_university_application_repo() -> UniversityApplicationRepository:
    return UniversityApplicationRepository()


def get_identifier_sequence_repo() -> IdentifierSequenceRepository:
    return IdentifierSequenceRepository()


def get_identifier_service(
    sequence_repo: IdentifierSequenceRepository = Depends(get_identifier_sequence_repo),
    tenant_repo: TenantRepository = Depends(get_tenant_repo),
) -> IdentifierService:
    return IdentifierService(sequence_repo, tenant_repo)


def get_grade_calculator() -> GradeCalculator:
    return GradeCalculator()

# --- Auth dependencies ---
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repo),
    request: Request = None,
) -> User:
    token = credentials.credentials
    payload = auth_service.decode_token(token)

    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("sub")
    user = await user_repo.get_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    # If token contains an explicit tenant_id (impersonation), and the
    # authenticated user is a super_admin, override the in-memory tenant_id
    # so downstream handlers operate in the acting tenant context.
    token_tenant = payload.get("tenant_id")
    try:
        if token_tenant and user.role.value == "super_admin":
            setattr(user, "impersonating", True)
            setattr(user, "impersonated_tenant_id", token_tenant)
            user.tenant_id = token_tenant
    except Exception:
        pass

    if request is not None:
        request.state.user_id = str(user.id)
        request.state.tenant_id = getattr(user, "tenant_id", None)

    return user

def require_roles(*allowed_roles: str):
    """Dependency factory for role-based access control"""
    async def role_checker(current_user: User = Depends(get_current_user), request: Request = None) -> User:
        # Auditor is a read-only compliance role: allow for safe (GET) requests only
        if current_user.role.value == "auditor":
            if request is None or request.method != "GET":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Auditor role is read-only"
                )
            return current_user

        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker
