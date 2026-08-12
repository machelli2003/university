from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime

class Workflow(Document):
    tenant_id: str
    name: str
    description: str

    workflow_type: str

    steps: List[dict] = []

    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "workflows"

class WorkflowInstance(Document):
    tenant_id: str
    workflow_id: str
    initiator_id: str

    related_entity_id: str
    related_entity_type: str

    current_step: int = 0
    status: str = "pending"

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "workflow_instances"

class ApprovalTask(Document):
    tenant_id: str
    workflow_instance_id: str

    step_order: int
    approver_id: str

    status: str = "pending"
    comments: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None

    class Settings:
        name = "approval_tasks"
        indexes = [
            [("approver_id", 1), ("status", 1)],
        ]
