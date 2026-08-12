from fastapi import APIRouter, HTTPException, status, Depends
from app.presentation.api.v1.health.schemas import (
    CreateHealthRecordRequest, BookAppointmentRequest, CounselingRequestSchema
)
from app.infrastructure.database.repositories.health_repository import (
    HealthRecordRepository, ClinicAppointmentRepository, CounselingRepository
)
from app.dependencies import get_current_user, require_roles, get_student_repo
from app.infrastructure.models.user import User

router = APIRouter()

def get_health_record_repo() -> HealthRecordRepository:
    return HealthRecordRepository()

def get_appointment_repo() -> ClinicAppointmentRepository:
    return ClinicAppointmentRepository()

def get_counseling_repo() -> CounselingRepository:
    return CounselingRepository()

@router.post("/records")
async def create_health_record(
    request: CreateHealthRecordRequest,
    current_user: User = Depends(get_current_user),
    health_repo=Depends(get_health_record_repo),
):
    record = await health_repo.create({"tenant_id": current_user.tenant_id or "default", **request.dict()})
    return {"id": str(record.id)}

@router.get("/records/{student_id}")
async def get_health_record(
    student_id: str,
    current_user: User = Depends(get_current_user),
    health_repo=Depends(get_health_record_repo),
):
    record = await health_repo.get_by_student(current_user.tenant_id or "default", student_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    return {
        "id": str(record.id), "blood_group": record.blood_group,
        "allergies": record.allergies, "medical_conditions": record.medical_conditions,
    }

@router.post("/appointments")
async def book_appointment(
    request: BookAppointmentRequest,
    current_user: User = Depends(get_current_user),
    appointment_repo=Depends(get_appointment_repo),
):
    appointment = await appointment_repo.create({"tenant_id": current_user.tenant_id or "default", **request.dict()})
    return {"id": str(appointment.id), "status": "scheduled"}

@router.get("/appointments/upcoming")
async def list_upcoming_appointments(
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    appointment_repo=Depends(get_appointment_repo),
):
    appointments = await appointment_repo.get_upcoming(current_user.tenant_id or "default")
    return [{"id": str(a.id), "student_id": a.student_id, "appointment_date": a.appointment_date} for a in appointments]

@router.post("/counseling/request")
async def request_counseling(
    request: CounselingRequestSchema,
    current_user: User = Depends(get_current_user),
    counseling_repo=Depends(get_counseling_repo),
    student_repo=Depends(get_student_repo),
):
    from datetime import datetime
    student = await student_repo.get_by_user_id(current_user.tenant_id or "default", str(current_user.id))
    student_id = student.student_id if student else str(current_user.id)
    counseling = await counseling_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "student_id": student_id,
        "requested_by": str(current_user.id),
        "request_date": datetime.utcnow(),
        **request.dict(),
    })
    return {"id": str(counseling.id), "status": "pending"}
