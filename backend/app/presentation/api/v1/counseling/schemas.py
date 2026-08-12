from pydantic import BaseModel
from typing import Optional

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
    status: str
