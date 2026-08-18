from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from app.dependencies import get_current_user, get_student_repo, get_grade_repo, get_payment_repo, get_registration_repo, get_course_repo
from app.infrastructure.models.user import User
from app.infrastructure.models.student import StudentStatusEnum, Student
from app.presentation.api.v1.student import schemas as student_schemas
from app.application.finance.fee_calculation import FeeCalculatorUseCase
from app.infrastructure.database.repositories.grade_repository import TranscriptRepository
from app.infrastructure.database.repositories.registration_repository import RegistrationRepository

router = APIRouter()


async def get_or_create_student_for_user(current_user: User, tenant_id: str, student_repo) -> Optional[Student]:
    # 1. Check by user_id
    student = await student_repo.get_by_user_id(tenant_id, str(current_user.id))
    if student:
        return student

    # 2. Check by email
    if getattr(current_user, "email", None):
        students_by_email = await student_repo.model.find({
            "tenant_id": tenant_id,
            "email": current_user.email
        }).to_list(None)
        if students_by_email:
            student = students_by_email[0]
            student.user_id = str(current_user.id)
            await student.save()
            return student

    # 3. Auto-provision if user is a student
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role == "student":
        student_id_str = f"STD-{datetime.utcnow().year}-{str(current_user.id)[-4:].upper()}"
        first_name = getattr(current_user, "first_name", "Student") or "Student"
        last_name = getattr(current_user, "last_name", "User") or "User"
        
        student = await student_repo.create({
            "tenant_id": tenant_id,
            "user_id": str(current_user.id),
            "student_id": student_id_str,
            "first_name": first_name,
            "last_name": last_name,
            "email": current_user.email,
            "phone": getattr(current_user, "phone", "") or "+233000000000",
            "programme_id": "BSc Computer Science",
            "faculty_id": "Faculty of Science",
            "department_id": "Computer Science",
            "entry_level": "100",
            "entry_semester": "1",
            "entry_year": datetime.utcnow().year,
            "status": StudentStatusEnum.ACTIVE,
            "registered_courses": [],
            "fee_balance": 0.0,
            "cgpa": 0.0,
            "current_gpa": 0.0,
        })
        return student

    return None


def _entry_level_label(entry_level: str) -> str:
    """Convert entry_level to a display string like 'Level 200'."""
    level_map = {
        "100": "Level 100", "200": "Level 200",
        "300": "Level 300", "400": "Level 400",
        "level_100": "Level 100", "level_200": "Level 200",
        "level_300": "Level 300", "level_400": "Level 400",
    }
    return level_map.get(str(entry_level).lower(), f"Level {entry_level}")


def _current_academic_year(entry_year: int) -> str:
    """Build an academic year string from the student's entry year."""
    from datetime import datetime
    now = datetime.utcnow()
    academic_year = now.year if now.month >= 8 else now.year - 1
    return f"{academic_year}/{academic_year + 1}"


def build_student_response(student):
    return {
        "id": str(student.id),
        "student_id": student.student_id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "email": student.email,
        "programme_id": student.programme_id,
        "faculty_id": student.faculty_id,
        "department_id": student.department_id,
        "status": student.status,
        "registered_courses": student.registered_courses,
    }


@router.get("/", response_model=List[student_schemas.StudentProfile])
async def list_students(
    status: Optional[str] = None,
    programme_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    student_repo=Depends(get_student_repo),
):
    if current_user.role.value not in ["registrar", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Requires registrar or admin role")

    filters = {"tenant_id": current_user.tenant_id or "default"}
    if status:
        filters["status"] = status
    if programme_id:
        filters["programme_id"] = programme_id

    students = await student_repo.get_all(**filters)
    return [
        student_schemas.StudentProfile(
            id=str(s.id),
            student_id=s.student_id,
            first_name=s.first_name,
            last_name=s.last_name,
            email=s.email,
            programme_id=s.programme_id,
            faculty_id=s.faculty_id,
            department_id=s.department_id,
            fee_balance=s.fee_balance,
            cgpa=s.cgpa,
            current_gpa=s.current_gpa,
            level=_entry_level_label(s.entry_level),
            status=s.status.value if hasattr(s.status, "value") else str(s.status),
        )
        for s in students
    ]


@router.put("/{student_id}/status")
async def update_student_status(
    student_id: str,
    status_update: student_schemas.StudentStatusUpdate,
    current_user: User = Depends(get_current_user),
    student_repo=Depends(get_student_repo),
):
    if current_user.role.value not in ["registrar", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Requires registrar or admin role")

    student = await student_repo.get_by_student_id(current_user.tenant_id or "default", student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student = await student_repo.update(str(student.id), {
        "status": status_update.status,
        "status_changes": student.status_changes + [{
            "from": student.status,
            "to": status_update.status,
            "changed_by": str(current_user.id),
            "changed_at": student.updated_at,
        }],
    })

    return {"status": "updated", "student_id": student_id}


@router.post("/{student_id}/generate-transcript")
async def generate_student_transcript(
    student_id: str,
    current_user: User = Depends(get_current_user),
    student_repo=Depends(get_student_repo),
    grade_repo=Depends(get_grade_repo),
):
    if current_user.role.value not in ["registrar", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Requires registrar or admin role")

    student = await student_repo.get_by_student_id(current_user.tenant_id or "default", student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    transcript_repo = TranscriptRepository()
    grades = await grade_repo.get_by_student_semester(
        current_user.tenant_id or "default", student_id,
        str(student.entry_year), student.entry_semester
    )
    course_entries = [
        {
            "course_id": g.course_id,
            "letter_grade": g.letter_grade,
            "gpa_points": g.gpa_points,
            "final_score": g.total_score,
        }
        for g in grades
    ]

    transcript = await transcript_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "student_id": student_id,
        "academic_year": str(student.entry_year),
        "semester": student.entry_semester,
        "gpa": student.current_gpa or 0.0,
        "cgpa": student.cgpa or 0.0,
        "courses_taken": course_entries,
        "signed": False,
    })

    return {"transcript_id": str(transcript.id), "signed": transcript.signed}


@router.get("/{student_id}/registrations")
async def get_student_registrations(
    student_id: str,
    current_user: User = Depends(get_current_user),
    registration_repo=Depends(get_registration_repo),
):
    if current_user.role.value not in ["registrar", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Requires registrar or admin role")

    registrations = await registration_repo.get_by_student(current_user.tenant_id or "default", student_id)
    return [
        {
            "id": str(r.id),
            "student_id": r.student_id,
            "course_ids": r.course_ids,
            "academic_year": r.academic_year,
            "semester": r.semester,
            "total_credits": r.total_credits,
            "status": r.status,
        }
        for r in registrations
    ]


@router.get("/registrations")
async def list_registrations(
    academic_year: Optional[str] = None,
    semester: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    registration_repo=Depends(get_registration_repo),
):
    if current_user.role.value not in ["registrar", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Requires registrar or admin role")

    if academic_year and semester:
        registrations = await registration_repo.get_by_period(current_user.tenant_id or "default", academic_year, semester)
    else:
        registrations = await registration_repo.get_all_for_tenant(current_user.tenant_id or "default")

    return [
        {
            "id": str(r.id),
            "student_id": r.student_id,
            "course_ids": r.course_ids,
            "academic_year": r.academic_year,
            "semester": r.semester,
            "total_credits": r.total_credits,
            "status": r.status,
        }
        for r in registrations
    ]


@router.get("/me", response_model=student_schemas.StudentDashboardResponse)
async def get_my_student_dashboard(
    current_user: User = Depends(get_current_user),
    student_repo=Depends(get_student_repo),
    grade_repo=Depends(get_grade_repo),
    payment_repo=Depends(get_payment_repo),
    course_repo=Depends(get_course_repo),
):
    tenant_id = current_user.tenant_id or "default"

    # Fetch or auto-provision/link the student record for this user
    student = await get_or_create_student_for_user(current_user, tenant_id, student_repo)
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    # --- Courses: look up Course documents for each registered course ID ---
    course_items: List[student_schemas.CourseItem] = []
    grade_by_course: dict = {}

    # Fetch all grades to show grade alongside each course
    all_grades = await grade_repo.get_by_student(tenant_id, student.student_id)
    for g in all_grades:
        if g.letter_grade:
            grade_by_course[g.course_id] = g.letter_grade

    for course_id in (student.registered_courses or []):
        try:
            course_doc = await course_repo.get_by_id(course_id)
            if course_doc:
                course_items.append(
                    student_schemas.CourseItem(
                        course_id=str(course_doc.id),
                        code=course_doc.code,
                        name=course_doc.name,
                        credit_hours=course_doc.credit_hours,
                        lecturer_id=course_doc.lecturer_id,
                        grade=grade_by_course.get(course_id),
                    )
                )
            else:
                # Course not found in DB — include a minimal placeholder
                course_items.append(
                    student_schemas.CourseItem(
                        course_id=course_id,
                        code=course_id,
                        name="Unknown Course",
                        credit_hours=3,
                        grade=grade_by_course.get(course_id),
                    )
                )
        except Exception:
            pass

    # --- Timetable: simple daily slots derived from registered courses ---
    # Since there is no dedicated schedule store yet, we build a placeholder
    # from course data. When a proper timetable model exists this can be replaced.
    DAYS_CYCLE = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    timetable_slots: List[student_schemas.TimetableSlot] = []
    for idx, item in enumerate(course_items):
        day = DAYS_CYCLE[idx % len(DAYS_CYCLE)]
        timetable_slots.append(
            student_schemas.TimetableSlot(
                day=day,
                time="08:00 - 10:00",
                course=item.code,
                course_name=item.name,
                room="TBA",
                lecturer=item.lecturer_id,
            )
        )

    # --- Transcripts ---
    transcripts: List[student_schemas.TranscriptItem] = []
    try:
        transcript_repo = TranscriptRepository()
        raw_transcripts = await transcript_repo.get_by_student(tenant_id, student.student_id)
        transcripts = [
            student_schemas.TranscriptItem(
                academic_year=t.academic_year,
                semester=t.semester,
                courses=t.courses_taken if hasattr(t, "courses_taken") else (t.courses if hasattr(t, "courses") else []),
                cgpa=getattr(t, "cgpa", None),
                created_at=getattr(t, "generated_date", None) or getattr(t, "created_at", None),
            )
            for t in raw_transcripts
        ]
    except Exception:
        transcripts = []

    # --- Fees ---
    fee_calc = FeeCalculatorUseCase(payment_repo=payment_repo)
    try:
        fee_summary = await fee_calc.calculate_balance(tenant_id, student.student_id)
    except Exception:
        fee_summary = {"balance": student.fee_balance or 0.0}

    # --- Payments ---
    try:
        raw_payments = await payment_repo.get_by_student(tenant_id, student.student_id)
        payments = [
            {
                "id": str(p.id),
                "amount": p.amount,
                "status": p.status.value if hasattr(p.status, "value") else str(p.status),
                "payment_date": str(p.payment_date) if p.payment_date else None,
            }
            for p in raw_payments
        ]
    except Exception:
        payments = []

    return student_schemas.StudentDashboardResponse(
        profile=student_schemas.StudentProfile(
            id=str(student.id),
            student_id=student.student_id,
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            programme_id=student.programme_id,
            faculty_id=student.faculty_id,
            department_id=student.department_id,
            fee_balance=fee_summary.get("balance", student.fee_balance or 0.0),
            cgpa=student.cgpa or 0.0,
            current_gpa=student.current_gpa or 0.0,
            level=_entry_level_label(student.entry_level),
            academic_year=_current_academic_year(student.entry_year),
            status=student.status.value if hasattr(student.status, "value") else str(student.status),
        ),
        courses=course_items,
        timetable=timetable_slots,
        transcripts=transcripts,
        outstanding_fees=fee_summary.get("balance", 0.0),
        payments=payments,
    )


@router.get("/{student_id}/transcripts", response_model=list[student_schemas.TranscriptItem])
async def get_student_transcripts(student_id: str, grade_repo=Depends(get_grade_repo)):
    transcript_repo = TranscriptRepository()
    transcripts = await transcript_repo.get_by_student("default", student_id)
    return [
        student_schemas.TranscriptItem(
            academic_year=t.academic_year,
            semester=t.semester,
            courses=t.courses_taken if hasattr(t, "courses_taken") else [],
            cgpa=getattr(t, "cgpa", None),
            created_at=getattr(t, "generated_date", None),
        )
        for t in transcripts
    ]


@router.get("/me/timetable", response_model=student_schemas.StudentTimetable)
async def get_my_timetable(
    current_user: User = Depends(get_current_user),
    student_repo=Depends(get_student_repo),
    course_repo=Depends(get_course_repo),
    registration_repo=Depends(get_registration_repo),
):
    """Get the current student's timetable based on registered courses."""
    tenant_id = current_user.tenant_id or "default"

    student = await get_or_create_student_for_user(current_user, tenant_id, student_repo)
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    # Determine current academic year/semester
    from datetime import datetime
    now = datetime.utcnow()
    academic_year = str(now.year if now.month >= 8 else now.year - 1)
    semester = "1" if now.month >= 8 or now.month <= 1 else "2"

    # Try to get the latest registration
    registrations = await registration_repo.get_by_student(tenant_id, student.student_id)
    latest_reg = registrations[0] if registrations else None
    course_ids = latest_reg.course_ids if latest_reg else (student.registered_courses or [])
    if latest_reg:
        academic_year = latest_reg.academic_year
        semester = latest_reg.semester

    DAYS_CYCLE = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    entries: List[student_schemas.TimetableEntry] = []
    for idx, course_id in enumerate(course_ids):
        try:
            course_doc = await course_repo.get_by_id(course_id)
            if not course_doc:
                continue
            day = DAYS_CYCLE[idx % len(DAYS_CYCLE)]
            hour_start = 8 + (idx % 5) * 2
            entries.append(
                student_schemas.TimetableEntry(
                    course_id=str(course_doc.id),
                    course_code=course_doc.code,
                    course_name=course_doc.name,
                    credits=course_doc.credit_hours,
                    schedule=[
                        student_schemas.TimeSlot(
                            day=day,
                            start_time=f"{hour_start:02d}:00",
                            end_time=f"{hour_start + 2:02d}:00",
                            room="TBA",
                            lecturer=course_doc.lecturer_id or "TBA",
                        )
                    ],
                )
            )
        except Exception:
            pass

    return student_schemas.StudentTimetable(
        academic_year=academic_year,
        semester=semester,
        courses=entries,
    )


@router.get("/me/results", response_model=student_schemas.StudentResults)
async def get_my_results(
    current_user: User = Depends(get_current_user),
    student_repo=Depends(get_student_repo),
    grade_repo=Depends(get_grade_repo),
    course_repo=Depends(get_course_repo),
):
    """Get the current student's exam results across all semesters."""
    tenant_id = current_user.tenant_id or "default"

    student = await get_or_create_student_for_user(current_user, tenant_id, student_repo)
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    # Fetch all grades (not hardcoded to a single year)
    all_grades = await grade_repo.get_by_student(tenant_id, student.student_id)

    # Determine the most recent semester from grades (or use student entry data)
    academic_year = str(student.entry_year) if student.entry_year else "N/A"
    semester = student.entry_semester or "1"
    if all_grades:
        academic_year = all_grades[0].academic_year
        semester = all_grades[0].semester

    course_results: List[student_schemas.CourseResult] = []
    for g in all_grades:
        # Attempt to enrich with course name
        course_code = g.course_id
        course_name = "Unknown Course"
        credits = 3
        try:
            course_doc = await course_repo.get_by_id(g.course_id)
            if course_doc:
                course_code = course_doc.code
                course_name = course_doc.name
                credits = course_doc.credit_hours
        except Exception:
            pass

        course_results.append(
            student_schemas.CourseResult(
                course_id=g.course_id,
                course_code=course_code,
                course_name=course_name,
                credits=credits,
                score=g.total_score or 0.0,
                grade=g.letter_grade or "N/A",
                gpa_points=g.gpa_points or 0.0,
            )
        )

    return student_schemas.StudentResults(
        academic_year=academic_year,
        semester=semester,
        courses=course_results,
        gpa=student.current_gpa or 0.0,
        cgpa=student.cgpa or 0.0,
    )


@router.get("/me/academic-standing", response_model=student_schemas.AcademicStanding)
async def get_my_academic_standing(
    current_user: User = Depends(get_current_user),
    student_repo=Depends(get_student_repo),
    grade_repo=Depends(get_grade_repo),
):
    """Get the current student's academic standing."""
    tenant_id = current_user.tenant_id or "default"

    student = await get_or_create_student_for_user(current_user, tenant_id, student_repo)
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    cgpa = student.cgpa or 0.0
    if cgpa >= 2.0:
        standing_status = "good_standing"
    elif cgpa >= 1.5:
        standing_status = "academic_probation"
    else:
        standing_status = "suspension"

    all_grades = await grade_repo.get_by_student(tenant_id, student.student_id)

    courses_passed = sum(1 for g in all_grades if (g.letter_grade and g.letter_grade not in ["F", "E"]))
    courses_failed = sum(1 for g in all_grades if (g.letter_grade and g.letter_grade in ["F", "E"]))
    credits_earned = sum(
        3 for g in all_grades
        if g.letter_grade and g.letter_grade not in ["F", "E"]
    )

    return student_schemas.AcademicStanding(
        status=standing_status,
        current_cgpa=cgpa,
        current_gpa=student.current_gpa or 0.0,
        total_credits_earned=getattr(student, "credits_earned", credits_earned),
        total_courses_attempted=len(all_grades),
        courses_passed=courses_passed,
        courses_failed=courses_failed,
        last_updated=student.updated_at,
    )
