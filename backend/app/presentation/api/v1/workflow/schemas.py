from pydantic import BaseModel
from typing import List, Dict, Optional

class CreateWorkflowRequest(BaseModel):
    name: str
    description: str
    workflow_type: str
    steps: List[Dict]

class InitiateWorkflowRequest(BaseModel):
    workflow_id: str
    related_entity_id: str
    related_entity_type: str

class ApprovalActionRequest(BaseModel):
    task_id: str
    approved: bool
    comments: Optional[str] = None
