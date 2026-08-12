from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from app.presentation.api.v1.workflow.schemas import (
    CreateWorkflowRequest, InitiateWorkflowRequest, ApprovalActionRequest
)
from app.infrastructure.database.repositories.workflow_repository import (
    WorkflowRepository, WorkflowInstanceRepository, ApprovalTaskRepository
)
from app.dependencies import get_current_user, require_roles
from app.infrastructure.models.user import User

router = APIRouter()

def get_workflow_repo() -> WorkflowRepository:
    return WorkflowRepository()

def get_workflow_instance_repo() -> WorkflowInstanceRepository:
    return WorkflowInstanceRepository()

def get_approval_task_repo() -> ApprovalTaskRepository:
    return ApprovalTaskRepository()

@router.post("/definitions")
async def create_workflow(
    request: CreateWorkflowRequest,
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    workflow_repo=Depends(get_workflow_repo),
):
    workflow = await workflow_repo.create({"tenant_id": current_user.tenant_id or "default", **request.dict()})
    return {"id": str(workflow.id)}

@router.post("/initiate")
async def initiate_workflow(
    request: InitiateWorkflowRequest,
    current_user: User = Depends(get_current_user),
    workflow_repo=Depends(get_workflow_repo),
    instance_repo=Depends(get_workflow_instance_repo),
    task_repo=Depends(get_approval_task_repo),
):
    workflow = await workflow_repo.get_by_id(request.workflow_id)
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    instance = await instance_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "workflow_id": request.workflow_id,
        "initiator_id": str(current_user.id),
        "related_entity_id": request.related_entity_id,
        "related_entity_type": request.related_entity_type,
    })

    if workflow.steps:
        first_step = workflow.steps[0]
        await task_repo.create({
            "tenant_id": current_user.tenant_id or "default",
            "workflow_instance_id": str(instance.id),
            "step_order": 0,
            "approver_id": first_step.get("approver_role", ""),
        })

    return {"instance_id": str(instance.id), "status": "pending"}

@router.get("/my-tasks")
async def get_my_approval_tasks(
    current_user: User = Depends(get_current_user),
    task_repo=Depends(get_approval_task_repo),
):
    tasks = await task_repo.get_by_approver(str(current_user.id))
    return [{"id": str(t.id), "step_order": t.step_order, "status": t.status} for t in tasks]

@router.post("/approve")
async def process_approval(
    request: ApprovalActionRequest,
    current_user: User = Depends(get_current_user),
    task_repo=Depends(get_approval_task_repo),
    instance_repo=Depends(get_workflow_instance_repo),
):
    status_value = "approved" if request.approved else "rejected"

    await task_repo.update(request.task_id, {
        "status": status_value,
        "comments": request.comments,
        "approved_at": datetime.utcnow(),
    })

    return {"task_id": request.task_id, "status": status_value}
