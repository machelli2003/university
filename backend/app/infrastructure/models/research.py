from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime

class ResearchProposal(Document):
    tenant_id: str
    researcher_id: str

    title: str
    description: str
    status: str = "draft"

    submitted_date: Optional[datetime] = None
    approved_date: Optional[datetime] = None

    class Settings:
        name = "research_proposals"

class Grant(Document):
    tenant_id: str
    researcher_id: str

    title: str
    amount: float
    status: str = "pending"

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "grants"

class Publication(Document):
    tenant_id: str
    researcher_id: str

    title: str
    journal: str
    publication_date: datetime
    doi: Optional[str] = None

    class Settings:
        name = "publications"
