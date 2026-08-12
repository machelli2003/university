from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from app.presentation.api.v1.counseling.schemas import (
    CounselingCreateRequest, CounselingResponse, CounselingReplyRequest
)
from app.infrastructure.database.repositories.counseling_repository import CounselingRepository
from app.dependencies import get_current_user, require_roles
from app.infrastructure.models.user import User

router = APIRouter()

def get_counsel_repo() -> CounselingRepository:
    return CounselingRepository()


@router.post("/counseling", response_model=CounselingResponse)
async def create_counsel_message(
    request: CounselingCreateRequest,
    current_user: User = Depends(get_current_user),
    repo=Depends(get_counsel_repo),
):
    msg = await repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "student_id": request.student_id,
        "subject": request.subject,
        "message": request.message,
    })
    return CounselingResponse(id=str(msg.id), subject=msg.subject, message=msg.message, status=msg.status)


@router.get("/counseling/pending", response_model=List[CounselingResponse])
async def list_pending(
    current_user: User = Depends(require_roles("counselor", "university_admin", "super_admin")),
    repo=Depends(get_counsel_repo),
):
    items = await repo.get_pending_for_tenant(current_user.tenant_id or "default")
    return [CounselingResponse(id=str(i.id), subject=i.subject, message=i.message, status=i.status) for i in items]


@router.post("/counseling/{id}/reply")
async def reply_counsel(
    id: str,
    request: CounselingReplyRequest,
    current_user: User = Depends(require_roles("counselor", "university_admin", "super_admin")),
    repo=Depends(get_counsel_repo),
):
    msg = await repo.get_by_id(id)
    if not msg or getattr(msg, 'tenant_id', None) != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    updated = await repo.update(id, {"response": request.response, "responder_id": str(current_user.id), "status": "responded", "responded_at": datetime.utcnow()})
    return {"id": str(updated.id), "status": updated.status}


@router.get("/counseling/student/{student_id}", response_model=List[CounselingResponse])
async def get_student_messages(
    student_id: str,
    current_user: User = Depends(get_current_user),
    repo=Depends(get_counsel_repo),
):
    msgs = await repo.get_for_student(current_user.tenant_id or "default", student_id)
    return [CounselingResponse(id=str(m.id), subject=m.subject, message=m.message, status=m.status) for m in msgs]
