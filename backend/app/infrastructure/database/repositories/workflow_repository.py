from app.infrastructure.models.workflow import Workflow, WorkflowInstance, ApprovalTask
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional

class WorkflowRepository(BaseRepository[Workflow]):
    def __init__(self):
        super().__init__(Workflow)

    async def get_by_type(self, tenant_id: str, workflow_type: str) -> Optional[Workflow]:
        return await self.model.find_one({
            "tenant_id": tenant_id, "workflow_type": workflow_type, "is_active": True
        })

class WorkflowInstanceRepository(BaseRepository[WorkflowInstance]):
    def __init__(self):
        super().__init__(WorkflowInstance)

    async def get_by_entity(self, entity_id: str, entity_type: str) -> Optional[WorkflowInstance]:
        return await self.model.find_one({
            "related_entity_id": entity_id, "related_entity_type": entity_type
        })

class ApprovalTaskRepository(BaseRepository[ApprovalTask]):
    def __init__(self):
        super().__init__(ApprovalTask)

    async def get_by_approver(self, approver_id: str) -> List[ApprovalTask]:
        return await self.model.find({"approver_id": approver_id, "status": "pending"}).to_list(None)

    async def get_by_instance(self, instance_id: str) -> List[ApprovalTask]:
        return await self.model.find({"workflow_instance_id": instance_id}).sort([("step_order", 1)]).to_list(None)
