from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.presentation.api.v1.parents.schemas import LinkStudentRequest, GuardianStudentResponse
from app.infrastructure.database.repositories.guardian_repository import GuardianRepository
from app.infrastructure.database.repositories.student_repository import StudentRepository
from app.dependencies import get_current_user, get_student_repo, require_roles
from app.infrastructure.models.user import User

router = APIRouter()

def get_guardian_repo() -> GuardianRepository:
    return GuardianRepository()


@router.post("/parents/link")
async def link_student(
    request: LinkStudentRequest,
    current_user: User = Depends(require_roles("parent_guardian", "university_admin", "super_admin")),
    guardian_repo=Depends(get_guardian_repo),
    student_repo=Depends(get_student_repo),
):
    # verify student exists
    s = await student_repo.get_by_student_id(current_user.tenant_id or "default", request.student_id)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    g = await guardian_repo.add_student(current_user.tenant_id or "default", str(current_user.id), request.student_id)
    return {"guardian_id": str(g.id), "student_ids": g.student_ids}


@router.get("/parents/students", response_model=List[GuardianStudentResponse])
async def list_linked_students(
    current_user: User = Depends(require_roles("parent_guardian", "university_admin", "super_admin")),
    guardian_repo=Depends(get_guardian_repo),
    student_repo=Depends(get_student_repo),
):
    ids = await guardian_repo.get_students(current_user.tenant_id or "default", str(current_user.id))
    students = []
    for sid in ids:
        s = await student_repo.get_by_student_id(current_user.tenant_id or "default", sid)
        if s:
            students.append(GuardianStudentResponse(student_id=s.student_id, first_name=s.first_name, last_name=s.last_name, email=getattr(s, 'email', None)))
    return students
