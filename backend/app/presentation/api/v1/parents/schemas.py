from pydantic import BaseModel
from typing import Optional

class LinkStudentRequest(BaseModel):
    student_id: str


class GuardianStudentResponse(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
