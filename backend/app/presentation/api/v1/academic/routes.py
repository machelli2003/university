from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.presentation.api.v1.academic.schemas import (
    CreateFacultyRequest, CreateDepartmentRequest, CreateProgramRequest,
    CreateCourseRequest, RegisterCoursesRequest, CourseResponse, ProgramResponse,
    CreateAcademicCalendarRequest, UpdateAcademicCalendarRequest,
)
from app.application.academic.register_courses import RegisterCoursesUseCase
from app.dependencies import (
    get_current_user, get_course_repo, get_program_repo,
    get_student_repo, get_registration_repo, get_academic_calendar_repo,
    require_roles
)
from app.infrastructure.database.repositories.course_repository import (
    FacultyRepository, DepartmentRepository
)
from app.infrastructure.database.repositories.academic_calendar_repository import AcademicCalendarRepository
from app.infrastructure.models.user import User

router = APIRouter()

def get_faculty_repo() -> FacultyRepository:
    return FacultyRepository()

def get_department_repo() -> DepartmentRepository:
    return DepartmentRepository()

@router.post("/faculties")
async def create_faculty(
    request: CreateFacultyRequest,
    current_user: User = Depends(require_roles("university_admin", "super_admin", "registrar", "dean")),
    faculty_repo=Depends(get_faculty_repo),
):
    faculty = await faculty_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        **request.dict()
    })
    return {"id": str(faculty.id), "name": faculty.name, "code": faculty.code}

@router.get("/faculties")
async def list_faculties(
    current_user: User = Depends(get_current_user),
    faculty_repo=Depends(get_faculty_repo),
):
    faculties = await faculty_repo.get_all(tenant_id=current_user.tenant_id or "default")
    return [{"id": str(f.id), "name": f.name, "code": f.code} for f in faculties]

@router.post("/departments")
async def create_department(
    request: CreateDepartmentRequest,
    current_user: User = Depends(require_roles("university_admin", "super_admin", "registrar")),
    department_repo=Depends(get_department_repo),
):
    department = await department_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        **request.dict()
    })
    return {"id": str(department.id), "name": department.name, "code": department.code}

@router.get("/departments/faculty/{faculty_id}")
async def list_departments(
    faculty_id: str,
    current_user: User = Depends(get_current_user),
    department_repo=Depends(get_department_repo),
):
    departments = await department_repo.get_by_faculty(faculty_id)
    return [{"id": str(d.id), "name": d.name, "code": d.code} for d in departments]

@router.post("/programmes", response_model=ProgramResponse)
async def create_programme(
    request: CreateProgramRequest,
    current_user: User = Depends(require_roles("university_admin", "super_admin", "registrar", "dean")),
    program_repo=Depends(get_program_repo),
):
    program = await program_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        **request.dict()
    })
    return ProgramResponse(
        id=str(program.id), name=program.name, code=program.code,
        duration_years=program.duration_years,
        capacity_planned=program.capacity_planned,
        capacity_current=program.capacity_current,
        description=getattr(program, "description", None),
        required_subjects=getattr(program, "required_subjects", []),
        minimum_grades=getattr(program, "minimum_grades", {}),
        aggregate_threshold=getattr(program, "aggregate_threshold", None),
    )

@router.get("/programmes", response_model=List[ProgramResponse])
async def list_programmes(
    current_user: User = Depends(get_current_user),
    program_repo=Depends(get_program_repo),
):
    programmes = await program_repo.get_all(tenant_id=current_user.tenant_id or "default")
    return [
        ProgramResponse(
            id=str(p.id), name=p.name, code=p.code,
            duration_years=p.duration_years,
            capacity_planned=p.capacity_planned,
            capacity_current=p.capacity_current,
            description=getattr(p, "description", None),
            required_subjects=getattr(p, "required_subjects", []),
            minimum_grades=getattr(p, "minimum_grades", {}),
            aggregate_threshold=getattr(p, "aggregate_threshold", None),
        )
        for p in programmes
    ]

@router.get("/programmes/{programme_id}", response_model=ProgramResponse)
async def get_programme(
    programme_id: str,
    current_user: User = Depends(get_current_user),
    program_repo=Depends(get_program_repo),
):
    program = await program_repo.get_by_id(programme_id)
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programme not found")
    return ProgramResponse(
        id=str(program.id), name=program.name, code=program.code,
        duration_years=program.duration_years,
        capacity_planned=program.capacity_planned,
        capacity_current=program.capacity_current,
        description=getattr(program, "description", None),
        required_subjects=getattr(program, "required_subjects", []),
        minimum_grades=getattr(program, "minimum_grades", {}),
        aggregate_threshold=getattr(program, "aggregate_threshold", None),
    )


@router.put("/programmes/{programme_id}", response_model=ProgramResponse)
async def update_programme(
    programme_id: str,
    request: CreateProgramRequest,
    current_user: User = Depends(require_roles("university_admin", "super_admin", "registrar", "dean")),
    program_repo=Depends(get_program_repo),
):
    programme = await program_repo.get_by_id(programme_id)
    if not programme or programme.tenant_id != (current_user.tenant_id or "default"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programme not found")

    update_data = {k: v for k, v in request.dict().items() if v is not None}
    updated = await program_repo.update(programme_id, update_data)
    return ProgramResponse(
        id=str(updated.id), name=updated.name, code=updated.code,
        duration_years=updated.duration_years,
        capacity_planned=updated.capacity_planned,
        capacity_current=updated.capacity_current,
        description=getattr(updated, "description", None),
        required_subjects=getattr(updated, "required_subjects", []),
        minimum_grades=getattr(updated, "minimum_grades", {}),
        aggregate_threshold=getattr(updated, "aggregate_threshold", None),
    )

@router.post("/courses", response_model=CourseResponse)
async def create_course(
    request: CreateCourseRequest,
    current_user: User = Depends(require_roles("university_admin", "super_admin", "registrar", "head_of_department")),
    course_repo=Depends(get_course_repo),
):
    course = await course_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        **request.dict()
    })
    return CourseResponse(
        id=str(course.id), code=course.code, name=course.name,
        credit_hours=course.credit_hours, course_type=course.course_type,
    )

@router.get("/courses", response_model=List[CourseResponse])
async def list_courses(
    current_user: User = Depends(get_current_user),
    course_repo=Depends(get_course_repo),
):
    courses = await course_repo.get_all(tenant_id=current_user.tenant_id or "default")
    return [
        CourseResponse(
            id=str(c.id), code=c.code, name=c.name,
            credit_hours=c.credit_hours, course_type=c.course_type,
        )
        for c in courses
    ]

def get_academic_calendar_repo() -> AcademicCalendarRepository:
    return AcademicCalendarRepository()


@router.post("/registration/register")
async def register_courses(
    request: RegisterCoursesRequest,
    current_user: User = Depends(get_current_user),
    course_repo=Depends(get_course_repo),
    student_repo=Depends(get_student_repo),
    registration_repo=Depends(get_registration_repo),
):
    use_case = RegisterCoursesUseCase(course_repo, student_repo, registration_repo)
    try:
        result = await use_case.execute(
            tenant_id=current_user.tenant_id or "default",
            **request.dict()
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/calendar", response_model=dict)
async def create_academic_calendar(
    request: CreateAcademicCalendarRequest,
    current_user: User = Depends(require_roles("registrar", "university_admin", "super_admin")),
    calendar_repo=Depends(get_academic_calendar_repo),
):
    calendar = await calendar_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        **request.dict(),
    })
    return {"id": str(calendar.id), "academic_year": calendar.academic_year, "semester": calendar.semester}


@router.get("/calendar", response_model=List[dict])
async def list_academic_calendars(
    current_user: User = Depends(get_current_user),
    calendar_repo=Depends(get_academic_calendar_repo),
):
    calendars = await calendar_repo.get_all_for_tenant(current_user.tenant_id or "default")
    return [
        {
            "id": str(c.id),
            "academic_year": c.academic_year,
            "semester": c.semester,
            "registration_open": c.registration_open,
            "registration_close": c.registration_close,
            "exam_period_start": c.exam_period_start,
            "exam_period_end": c.exam_period_end,
        }
        for c in calendars
    ]


@router.put("/calendar/{calendar_id}", response_model=dict)
async def update_academic_calendar(
    calendar_id: str,
    request: UpdateAcademicCalendarRequest,
    current_user: User = Depends(require_roles("registrar", "university_admin", "super_admin")),
    calendar_repo=Depends(get_academic_calendar_repo),
):
    calendar = await calendar_repo.get_by_id(calendar_id)
    if not calendar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic calendar not found")

    update_data = {k: v for k, v in request.dict().items() if v is not None}
    calendar = await calendar_repo.update(calendar_id, update_data)
    return {"id": str(calendar.id), "academic_year": calendar.academic_year, "semester": calendar.semester}
