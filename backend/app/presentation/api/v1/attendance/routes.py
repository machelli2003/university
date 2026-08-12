from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user, get_student_repo, get_attendance_repo
from app.infrastructure.models.user import User
from app.infrastructure.database.repositories.student_repository import StudentRepository
from datetime import datetime

router = APIRouter()

@router.post("/mark/{course_id}/{session_id}")
async def mark_attendance_via_qr(course_id: str, session_id: str, current_user: User = Depends(get_current_user), student_repo: StudentRepository = Depends(lambda: StudentRepository()), attendance_repo=Depends(get_attendance_repo)):
    # Only students may mark their own attendance via QR
    if current_user.role.value != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can mark attendance via QR")

    student = await student_repo.get_by_user_id(current_user.tenant_id or "default", str(current_user.id))
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    # Create attendance record
    record = await attendance_repo.create({
        "tenant_id": current_user.tenant_id,
        "student_id": student.student_id,
        "course_id": course_id,
        "session_date": datetime.utcnow(),
        "is_present": True,
        "marked_by": str(current_user.id),
        "method": "qr",
        "qr_session_id": session_id,
    })

    return {"id": str(record.id), "status": "recorded"}


@router.post("/mark/{course_id}/{session_id}/public")
async def mark_attendance_public(course_id: str, session_id: str, payload: dict, student_repo: StudentRepository = Depends(lambda: StudentRepository()), attendance_repo=Depends(get_attendance_repo)):
    # payload expected: {"student_id": "S12345"}
    student_id = payload.get("student_id") if isinstance(payload, dict) else None
    if not student_id:
        raise HTTPException(status_code=400, detail="student_id required")

    student = await student_repo.get_by_student_id("default", student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    record = await attendance_repo.create({
        "tenant_id": student.tenant_id,
        "student_id": student.student_id,
        "course_id": course_id,
        "session_date": datetime.utcnow(),
        "is_present": True,
        "marked_by": "public_form",
        "method": "public",
        "qr_session_id": session_id,
    })

    return {"id": str(record.id), "status": "recorded"}
