from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.dependencies import get_current_user, get_student_repo, get_grade_repo, get_payment_repo, get_registration_repo
from app.infrastructure.models.user import User
from app.presentation.api.v1.student import schemas as student_schemas
from app.application.finance.fee_calculation import FeeCalculatorUseCase
from app.infrastructure.database.repositories.grade_repository import TranscriptRepository
from app.infrastructure.database.repositories.registration_repository import RegistrationRepository

router = APIRouter()


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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires registrar or admin role")

    filters = {"tenant_id": current_user.tenant_id or "default"}
    if status:
        filters["status"] = status
    if programme_id:
        filters["programme_id"] = programme_id

    students = await student_repo.get_all(**filters)
    return [student_schemas.StudentProfile(
        id=str(s.id), student_id=s.student_id,
        first_name=s.first_name, last_name=s.last_name,
        email=s.email, programme_id=s.programme_id,
        faculty_id=s.faculty_id, department_id=s.department_id,
        fee_balance=s.fee_balance,
    ) for s in students]


@router.put("/{student_id}/status")
async def update_student_status(
    student_id: str,
    status_update: student_schemas.StudentStatusUpdate,
    current_user: User = Depends(get_current_user),
    student_repo=Depends(get_student_repo),
):
    if current_user.role.value not in ["registrar", "university_admin", "super_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires registrar or admin role")

    student = await student_repo.get_by_student_id(current_user.tenant_id or "default", student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires registrar or admin role")

    student = await student_repo.get_by_student_id(current_user.tenant_id or "default", student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    transcript_repo = TranscriptRepository()
    grades = await grade_repo.get_by_student_semester(current_user.tenant_id or "default", student_id, student.entry_year, student.entry_semester)
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
        "academic_year": student.entry_year,
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires registrar or admin role")

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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires registrar or admin role")

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
):
    # find student record by linked user id
    student = await student_repo.get_by_user_id(current_user.tenant_id or "default", str(current_user.id))
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    # transcripts
    transcript_repo = grade_repo.__class__.__module__.replace('grade_repository', 'grade_repository')
    # use grade and transcript repositories via grade_repo's module imports
    try:
        from app.infrastructure.database.repositories.grade_repository import TranscriptRepository
        transcript_repo = TranscriptRepository()
        transcripts = await transcript_repo.get_by_student(current_user.tenant_id or "default", student.student_id)
    except Exception:
        transcripts = []

    # payments and outstanding fees (calculate using fee calculator)
    fee_calc = FeeCalculatorUseCase(payment_repo=payment_repo)
    fee_summary = await fee_calc.calculate_balance(current_user.tenant_id or "default", student.student_id)

    payments = await payment_repo.get_by_student(current_user.tenant_id or "default", student.student_id)

    return student_schemas.StudentDashboardResponse(
        profile=student_schemas.StudentProfile(
            id=str(student.id), student_id=student.student_id,
            first_name=student.first_name, last_name=student.last_name,
            email=student.email, programme_id=student.programme_id,
            faculty_id=student.faculty_id, department_id=student.department_id,
            fee_balance=fee_summary.get("balance", student.fee_balance),
        ),
        transcripts=[
            student_schemas.TranscriptItem(
                academic_year=t.academic_year,
                semester=t.semester,
                courses=t.courses,
                cgpa=getattr(t, 'cgpa', None),
                created_at=t.created_at,
            )
            for t in transcripts
        ],
        outstanding_fees=fee_summary.get("balance", 0.0),
        payments=[{"id": str(p.id), "amount": p.amount, "status": p.status, "payment_date": p.payment_date} for p in payments]
    )


@router.get("/{student_id}/transcripts", response_model=list[student_schemas.TranscriptItem])
async def get_student_transcripts(student_id: str, grade_repo=Depends(get_grade_repo)):
    from app.infrastructure.database.repositories.grade_repository import TranscriptRepository
    transcript_repo = TranscriptRepository()
    transcripts = await transcript_repo.get_by_student("default", student_id)
    return [
        student_schemas.TranscriptItem(
            academic_year=t.academic_year,
            semester=t.semester,
            courses=t.courses,
            cgpa=getattr(t, 'cgpa', None),
            created_at=t.created_at,
        ) for t in transcripts
    ]


@router.get("/me/timetable", response_model=student_schemas.StudentTimetable)
async def get_my_timetable(
    current_user: User = Depends(get_current_user),
    student_repo=Depends(get_student_repo),
):
    """Get the current student's timetable"""
    student = await student_repo.get_by_user_id(current_user.tenant_id or "default", str(current_user.id))
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    # TODO: Integrate with timetable/schedule management system
    # For now, return a sample timetable based on registered courses
    return student_schemas.StudentTimetable(
        academic_year="2026",
        semester="1",
        courses=[
            student_schemas.TimetableEntry(
                course_id="CS101",
                course_code="CS101",
                course_name="Introduction to Computer Science",
                credits=3,
                schedule=[
                    student_schemas.TimeSlot(
                        day="Monday",
                        start_time="09:00",
                        end_time="10:30",
                        room="A201",
                        lecturer="Dr. Smith"
                    ),
                    student_schemas.TimeSlot(
                        day="Wednesday",
                        start_time="09:00",
                        end_time="10:30",
                        room="A201",
                        lecturer="Dr. Smith"
                    ),
                ]
            ),
            student_schemas.TimetableEntry(
                course_id="CS102",
                course_code="CS102",
                course_name="Data Structures",
                credits=4,
                schedule=[
                    student_schemas.TimeSlot(
                        day="Tuesday",
                        start_time="14:00",
                        end_time="15:30",
                        room="B102",
                        lecturer="Prof. Johnson"
                    ),
                    student_schemas.TimeSlot(
                        day="Thursday",
                        start_time="14:00",
                        end_time="15:30",
                        room="B102",
                        lecturer="Prof. Johnson"
                    ),
                ]
            ),
        ]
    )


@router.get("/me/results", response_model=student_schemas.StudentResults)
async def get_my_results(
    current_user: User = Depends(get_current_user),
    student_repo=Depends(get_student_repo),
    grade_repo=Depends(get_grade_repo),
):
    """Get the current student's exam results"""
    student = await student_repo.get_by_user_id(current_user.tenant_id or "default", str(current_user.id))
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    # Fetch grades for the current academic year and semester
    # TODO: Determine current academic year and semester from system config
    grades = await grade_repo.get_by_student_semester(
        current_user.tenant_id or "default",
        student.student_id,
        "2026",
        "1"
    )

    course_results = [
        student_schemas.CourseResult(
            course_id=g.course_id,
            course_code=getattr(g, 'course_code', 'UNKNOWN'),
            course_name=getattr(g, 'course_name', 'Unknown Course'),
            credits=getattr(g, 'credits', 3),
            score=g.total_score or 0.0,
            grade=g.letter_grade or "N/A",
            gpa_points=g.gpa_points or 0.0,
        )
        for g in grades
    ]

    return student_schemas.StudentResults(
        academic_year="2026",
        semester="1",
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
    """Get the current student's academic standing"""
    student = await student_repo.get_by_user_id(current_user.tenant_id or "default", str(current_user.id))
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    # Determine standing based on CGPA
    # Typical rules: Good standing >= 2.0, Probation >= 1.5, Suspension < 1.5
    cgpa = student.cgpa or 0.0
    if cgpa >= 2.0:
        standing_status = "good_standing"
    elif cgpa >= 1.5:
        standing_status = "academic_probation"
    else:
        standing_status = "suspension"

    # Get all grades for statistics
    all_grades = await grade_repo.get_by_student(
        current_user.tenant_id or "default",
        student.student_id
    )

    courses_passed = sum(1 for g in all_grades if (g.letter_grade and g.letter_grade not in ['F', 'E']))
    courses_failed = sum(1 for g in all_grades if (g.letter_grade and g.letter_grade in ['F', 'E']))

    return student_schemas.AcademicStanding(
        status=standing_status,
        current_cgpa=cgpa,
        current_gpa=student.current_gpa or 0.0,
        total_credits_earned=getattr(student, 'credits_earned', 0),
        total_courses_attempted=len(all_grades),
        courses_passed=courses_passed,
        courses_failed=courses_failed,
        last_updated=student.updated_at,
    )
