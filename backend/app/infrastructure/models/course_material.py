from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class CourseMaterial(Document):
    tenant_id: str
    course_id: str
    uploaded_by: str
    title: str
    description: Optional[str] = None
    file_url: str
    material_type: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "course_materials"
