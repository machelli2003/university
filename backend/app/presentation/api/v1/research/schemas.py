from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateProposalRequest(BaseModel):
    title: str
    description: str

class CreateGrantRequest(BaseModel):
    title: str
    amount: float

class CreatePublicationRequest(BaseModel):
    title: str
    journal: str
    publication_date: datetime
    doi: Optional[str] = None
