from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CounselingCreateRequest(BaseModel):
    student_id: str
    subject: str
    message: str

class CounselingReplyRequest(BaseModel):
    response: str

class CounselingResponse(BaseModel):
    id: str
    subject: str
    message: str
    topic: Optional[str] = None
    status: str
    response: Optional[str] = None
    responder_id: Optional[str] = None
    request_date: Optional[datetime] = None
    responded_at: Optional[datetime] = None
