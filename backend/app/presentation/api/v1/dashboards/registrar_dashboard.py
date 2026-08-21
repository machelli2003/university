"""
Registrar dashboard: live aggregates from student, programme, and applicant records.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.dependencies import get_current_user
from app.domain.academics import AcademicStandingService
from app.infrastructure.models.academic import Program
from app.infrastructure.models.applicant import Applicant, ApplicationStatusEnum
from app.infrastructure.models.student import Student, StudentStatusEnum

router = APIRouter()

ENROLLED_STATUSES = [
    StudentStatusEnum.REGISTERED,
    StudentStatusEnum.ACTIVE,
    StudentStatusEnum.ADMITTED,
]
PENDING_STUDENT_STATUSES = [StudentStatusEnum.APPLICANT]


class StudentEnrollmentSummary(BaseModel):
    applicant_id: str
    student_id: str
    full_name: str
    email: str
    phone: str
    programme: str
    enrolled_date: datetime
    academic_standing: str
    status: str


class EnrollmentStats(BaseModel):
    total_enrolled: int
    enrolled_this_month: int
    pending_enrollment: int
    verified_enrollment: int
    unverified_enrollment: int


class RegistrarDashboardResponse(BaseModel):
    enrollment_stats: EnrollmentStats
    students_by_academic_standing: dict
    students_by_level: dict
    recent_enrollments: List[StudentEnrollmentSummary]
    pending_enrollment_verification: List[StudentEnrollmentSummary]
    students_on_probation: List[StudentEnrollmentSummary]
    graduation_eligible: List[StudentEnrollmentSummary]
    monthly_enrollment_rate: float
    verification_completion_rate: float


def _status_value(status) -> str:
    return status.value if hasattr(status, "value") else str(status or "")


def _normalize_level(entry_level: Optional[str]) -> str:
    raw = str(entry_level or "100").strip()
    digits = "".join(ch for ch in raw if ch.isdigit())
    if digits in {"100", "200", "300", "400", "500", "600"}:
        return digits
    if digits in {"1", "2", "3", "4", "5", "6"}:
        return f"{digits}00"
    return "100"


def _has_assessed_gpa(student: Student) -> bool:
    cgpa = student.cgpa
    current = student.current_gpa
    if student.is_on_probation:
        return True
    return bool((cgpa and cgpa > 0) or (current and current > 0))


def _standing_for(student: Student, standing_service: AcademicStandingService) -> str:
    if not _has_assessed_gpa(student):
        return "unassessed"
    cgpa = float(student.cgpa or student.current_gpa or 0.0)
    return standing_service.calculate_standing(cgpa).value


async def _programme_names(query: Optional[dict] = None) -> dict:
    if query:
        programmes = await Program.find(query).to_list()
    else:
        programmes = await Program.find_all().to_list()
    names = {}
    for programme in programmes:
        name = programme.name or programme.code or "Unknown programme"
        names[str(programme.id)] = name
        if programme.code:
            names[programme.code] = name
    return names


def _to_summary(
    student: Student,
    programme_names: dict,
    standing_service: AcademicStandingService,
    status_override: Optional[str] = None,
) -> StudentEnrollmentSummary:
    programme_id = student.programme_id or ""
    return StudentEnrollmentSummary(
        applicant_id=student.applicant_id or str(student.id),
        student_id=student.student_id or "N/A",
        full_name=f"{student.first_name or ''} {student.last_name or ''}".strip() or "Unknown",
        email=student.email or "",
        phone=student.phone or "",
        programme=programme_names.get(programme_id, programme_id or "Not assigned"),
        enrolled_date=student.created_at or student.updated_at or datetime.utcnow(),
        academic_standing=_standing_for(student, standing_service),
        status=status_override or _status_value(student.status),
    )


@router.get(
    "/officer/dashboard/registrar",
    response_model=RegistrarDashboardResponse,
    tags=["registrar-dashboard"],
    summary="Registrar Dashboard Data",
)
async def get_registrar_dashboard(
    current_user=Depends(get_current_user),
    days: int = Query(30, ge=1, le=90, description="Number of days to look back"),
):
    user_role = _status_value(getattr(current_user, "role", None))
    if user_role not in ["registrar", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Only registrars can access this")

    tenant_id = str(getattr(current_user, "tenant_id", None) or "single-university")
    standing_service = AcademicStandingService()
    single_institution = tenant_id in {"", "single-university", "None"}

    try:
        enrolled_query: dict = {
            "status": {"$in": [status.value for status in ENROLLED_STATUSES]},
        }
        pending_student_query: dict = {
            "status": {"$in": [status.value for status in PENDING_STUDENT_STATUSES]},
        }
        pending_applicant_query: dict = {
            "status": ApplicationStatusEnum.ENROLLMENT_PENDING.value,
        }
        programme_query: dict = {}
        if not single_institution:
            enrolled_query["tenant_id"] = tenant_id
            pending_student_query["tenant_id"] = tenant_id
            pending_applicant_query["tenant_id"] = tenant_id
            programme_query["tenant_id"] = tenant_id

        enrolled_students = await Student.find(enrolled_query).to_list()
        pending_students = await Student.find(pending_student_query).to_list()
        pending_applicants = await Applicant.find(pending_applicant_query).to_list()
        programme_names = await _programme_names(programme_query)
        now = datetime.utcnow()
        month_ago = now - timedelta(days=30)
        cutoff = now - timedelta(days=days)

        standing_counts = {
            "excellent": 0,
            "good": 0,
            "satisfactory": 0,
            "warning": 0,
            "probation": 0,
            "at_risk": 0,
            "suspended": 0,
            "unassessed": 0,
        }
        level_counts: dict = {}

        enrolled_this_month = 0
        verified = 0
        unverified = 0
        recent = []
        probation = []
        graduation_eligible = []

        for student in enrolled_students:
            standing = _standing_for(student, standing_service)
            standing_counts[standing] = standing_counts.get(standing, 0) + 1

            level = _normalize_level(student.entry_level)
            level_counts[level] = level_counts.get(level, 0) + 1

            enrolled_at = student.created_at or student.updated_at
            if enrolled_at and enrolled_at >= month_ago:
                enrolled_this_month += 1
            if enrolled_at and enrolled_at >= cutoff:
                recent.append(student)

            status_value = _status_value(student.status)
            if status_value == StudentStatusEnum.ACTIVE.value:
                verified += 1
            else:
                unverified += 1

            if student.is_on_probation or standing in {"probation", "at_risk", "suspended"}:
                probation.append(student)

            if level in {"400", "500", "600"} and standing in {"excellent", "good", "satisfactory"}:
                graduation_eligible.append(student)

        recent.sort(key=lambda s: s.created_at or s.updated_at or now, reverse=True)

        pending_summaries = [
            _to_summary(student, programme_names, standing_service, "enrollment_pending")
            for student in pending_students[:20]
        ]
        for applicant in pending_applicants[:20]:
            pending_summaries.append(
                StudentEnrollmentSummary(
                    applicant_id=str(applicant.id),
                    student_id=getattr(applicant, "student_id", None) or "Pending",
                    full_name=f"{applicant.first_name or ''} {applicant.last_name or ''}".strip() or "Unknown",
                    email="",
                    phone=getattr(applicant, "phone", "") or "",
                    programme=programme_names.get(
                        getattr(applicant, "allocated_programme_id", None) or "",
                        getattr(applicant, "allocated_programme_id", None) or "Not assigned",
                    ),
                    enrolled_date=getattr(applicant, "updated_at", None) or now,
                    academic_standing="unassessed",
                    status=ApplicationStatusEnum.ENROLLMENT_PENDING.value,
                )
            )

        total_enrolled = len(enrolled_students)
        pending_count = len(pending_students) + len(pending_applicants)
        monthly_rate = (enrolled_this_month / total_enrolled * 100) if total_enrolled else 0.0
        verification_rate = (verified / total_enrolled * 100) if total_enrolled else 0.0

        for level in ("100", "200", "300", "400"):
            level_counts.setdefault(level, 0)

        return RegistrarDashboardResponse(
            enrollment_stats=EnrollmentStats(
                total_enrolled=total_enrolled,
                enrolled_this_month=enrolled_this_month,
                pending_enrollment=pending_count,
                verified_enrollment=verified,
                unverified_enrollment=unverified,
            ),
            students_by_academic_standing=standing_counts,
            students_by_level=level_counts,
            recent_enrollments=[
                _to_summary(student, programme_names, standing_service)
                for student in recent[:20]
            ],
            pending_enrollment_verification=pending_summaries[:20],
            students_on_probation=[
                _to_summary(student, programme_names, standing_service, "probation")
                for student in probation[:50]
            ],
            graduation_eligible=[
                _to_summary(student, programme_names, standing_service, "eligible_for_graduation")
                for student in graduation_eligible[:50]
            ],
            monthly_enrollment_rate=round(monthly_rate, 2),
            verification_completion_rate=round(verification_rate, 2),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard: {exc}") from exc
