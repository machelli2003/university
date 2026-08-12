from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.presentation.api.v1.exam.schemas import SubmitGradeRequest, GradeResponse
from app.application.exam.submit_grades import SubmitGradesUseCase, ApproveGradesUseCase
from app.dependencies import get_current_user, get_grade_repo, get_grade_calculator, get_audit_repo, require_roles
from app.infrastructure.database.repositories.audit_repository import AuditRepository
from app.infrastructure.models.user import User

router = APIRouter()

@router.post("/grades/submit", response_model=GradeResponse)
async def submit_grade(
    request: SubmitGradeRequest,
    current_user: User = Depends(require_roles("lecturer", "head_of_department", "dean")),
    grade_repo=Depends(get_grade_repo),
    grade_calculator=Depends(get_grade_calculator),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    use_case = SubmitGradesUseCase(grade_repo, grade_calculator)
    result = await use_case.execute(
        tenant_id=current_user.tenant_id or "default",
        submitted_by=str(current_user.id),
        **request.dict()
    )
    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "grade_submitted",
        "entity_type": "grade",
        "entity_id": result.get("id"),
        "action": "submit_grade",
        "performed_by": str(current_user.id),
        "details": {"course_id": result.get("course_id"), "student_id": result.get("student_id")},
    })
    return GradeResponse(**result)

@router.post("/grades/{grade_id}/approve")
async def approve_grade(
    grade_id: str,
    current_user: User = Depends(require_roles("head_of_department", "dean", "registrar", "university_admin")),
    grade_repo=Depends(get_grade_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
):
    use_case = ApproveGradesUseCase(grade_repo)
    res = await use_case.approve(grade_id, str(current_user.id))
    await audit_repo.create({
        "tenant_id": current_user.tenant_id,
        "event_type": "grade_approved",
        "entity_type": "grade",
        "entity_id": grade_id,
        "action": "approve_grade",
        "performed_by": str(current_user.id),
        "details": {"result": res},
    })
    return res

@router.get("/grades/mine")
async def get_my_grades(
    current_user: User = Depends(require_roles("lecturer")),
    grade_repo=Depends(get_grade_repo),
):
    grades = await grade_repo.get_by_submitter(current_user.tenant_id or "default", str(current_user.id))
    return [
        {
            "id": str(g.id),
            "student_id": g.student_id,
            "course_id": g.course_id,
            "total_score": g.total_score,
            "letter_grade": g.letter_grade,
            "status": g.status,
            "submitted_date": g.submitted_date.isoformat() if g.submitted_date else None,
            "approved_date": g.approved_date.isoformat() if g.approved_date else None,
        }
        for g in grades
    ]


@router.get("/grades/pending")
async def get_pending_grades(
    current_user: User = Depends(require_roles("head_of_department", "dean", "registrar", "university_admin")),
    grade_repo=Depends(get_grade_repo),
):
    use_case = ApproveGradesUseCase(grade_repo)
    return await use_case.get_pending_approvals(current_user.tenant_id or "default")
