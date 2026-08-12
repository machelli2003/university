from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, get_course_repo, get_attendance_repo
from app.infrastructure.models.user import User
from app.presentation.api.v1.lecturer import schemas as lecturer_schemas
from app.infrastructure.database.repositories.student_repository import StudentRepository
from app.infrastructure.external_services.qr_code_service import QRCodeService
from datetime import datetime
import uuid

def get_qr_service() -> QRCodeService:
    return QRCodeService()

router = APIRouter()


@router.get("/courses", response_model=list[lecturer_schemas.CourseItem])
async def my_courses(current_user: User = Depends(get_current_user), course_repo=Depends(get_course_repo)):
    if current_user.role.value != "lecturer":
        raise HTTPException(status_code=403, detail="Requires lecturer role")

    courses = await course_repo.get_by_lecturer(str(current_user.id))
    return [lecturer_schemas.CourseItem(id=str(c.id), code=c.code, title=c.title) for c in courses]


@router.post("/courses/{course_id}/attendance")
async def mark_attendance(course_id: str, request: lecturer_schemas.AttendanceMarkRequest,
                          current_user: User = Depends(get_current_user), attendance_repo=Depends(get_attendance_repo), course_repo=Depends(get_course_repo)):
    if current_user.role.value != "lecturer":
        raise HTTPException(status_code=403, detail="Requires lecturer role")

    # verify lecturer owns the course or is admin
    course = await course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role.value not in ("university_admin", "super_admin") and course.lecturer_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized for this course")

    record = await attendance_repo.create({
        "tenant_id": current_user.tenant_id,
        "student_id": request.student_id,
        "course_id": request.course_id,
        "session_date": request.session_date,
        "is_present": request.is_present,
        "marked_by": str(current_user.id),
        "method": "manual",
    })

    return {"id": str(record.id), "status": "ok"}


@router.get("/courses/{course_id}/attendance")
async def get_course_attendance(course_id: str, session_date: str = None, attendance_repo=Depends(get_attendance_repo)):
    # session_date is ISO string expected; repository expects datetime — simple filter by course_id if date missing
    from app.dependencies import get_course_repo
    course_repo = get_course_repo()
    course = await course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Only lecturer owner or admins should view detailed attendance
    current_user = None
    # Attempt to get current user via dependency (best effort)
    try:
        from app.dependencies import get_current_user as _gcu
        current_user = await _gcu()
    except Exception:
        pass

    if current_user and current_user.role.value not in ("university_admin", "super_admin") and course.lecturer_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized for this course")

    if session_date:
        from datetime import datetime
        sd = datetime.fromisoformat(session_date)
        records = await attendance_repo.get_by_course_and_date(course_id, sd)
    else:
        # fallback: query directly via repo model
        records = await attendance_repo.model.find({"course_id": course_id}).to_list(None)

    return [
        {
            "student_id": r.student_id,
            "course_id": r.course_id,
            "session_date": r.session_date,
            "is_present": r.is_present,
            "marked_by": r.marked_by,
        }
        for r in records
    ]


@router.get("/courses/{course_id}/roster")
async def get_course_roster(course_id: str, current_user: User = Depends(get_current_user), student_repo=Depends(lambda: StudentRepository())):
    # Only lecturers assigned to the course or admin can fetch roster
    # Authorization: verify course ownership
    course = await get_course_repo().get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role.value != "super_admin" and current_user.role.value != "university_admin" and course.lecturer_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized for this course")

    students = await student_repo.get_by_registered_course(current_user.tenant_id or "default", course_id)
    return [{"id": str(s.id), "student_id": s.student_id, "name": f"{s.first_name} {s.last_name}", "email": s.email} for s in students]


@router.get("/courses/{course_id}/attendance/qr")
async def generate_attendance_qr(course_id: str, base_url: str = "http://localhost:3000", qr_service: QRCodeService = Depends(get_qr_service)):
    # create a session id for this attendance session
    session_id = uuid.uuid4().hex
    # verify course and ownership
    course = await get_course_repo().get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Only lecturer owner or admins may generate QR
    try:
        from app.dependencies import get_current_user as _gcu
        cu = await _gcu()
        if cu.role.value not in ("university_admin", "super_admin") and course.lecturer_id != str(cu.id):
            raise HTTPException(status_code=403, detail="Not authorized to generate QR for this course")
    except HTTPException:
        raise
    except Exception:
        # if unable to resolve current user, prevent generation
        raise HTTPException(status_code=401, detail="Authentication required")

    qr_data = qr_service.generate_attendance_qr(course_id, session_id, base_url)
    attendance_url = f"{base_url}/attendance/mark/{course_id}/{session_id}"
    return {"session_id": session_id, "attendance_url": attendance_url, "qr_image": qr_data}


@router.get("/courses/{course_id}/attendance/report")
async def attendance_report(course_id: str, start: str, end: str, attendance_repo=Depends(get_attendance_repo)):
    # expects ISO date strings for start/end
    try:
        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format; use ISO string")

    records = await attendance_repo.get_by_course_and_range(course_id, s, e)
    # compute per-student attendance counts
    stats = {}
    sessions = set((r.session_date.isoformat() for r in records))
    total_sessions = len(sessions)
    for r in records:
        stats.setdefault(r.student_id, {"present": 0, "total": 0})
        stats[r.student_id]["total"] += 1
        if r.is_present:
            stats[r.student_id]["present"] += 1

    report = []
    for student_id, v in stats.items():
        percent = (v["present"] / v["total"] * 100) if v["total"] > 0 else 0.0
        report.append({"student_id": student_id, "present": v["present"], "total": v["total"], "percent": percent})

    return {"course_id": course_id, "start": s, "end": e, "total_sessions": total_sessions, "report": report}
