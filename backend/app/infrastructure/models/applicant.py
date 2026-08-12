from beanie import Document, Indexed
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ApplicationStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    AWAITING_RESULTS = "awaiting_results"
    RESULTS_UPLOADED = "results_uploaded"
    RESULTS_APPROVED = "results_approved"
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    RANKED = "ranked"
    ALLOCATED = "allocated"
    WAITLISTED = "waitlisted"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Applicant(Document):
    tenant_id: str
    user_id: str

    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    nationality: str = "Ghana"

    status: ApplicationStatusEnum = ApplicationStatusEnum.DRAFT
    application_date: datetime = Field(default_factory=datetime.utcnow)

    index_number: Optional[str] = None
    exam_year: Optional[int] = None
    exam_type: Optional[str] = None

    results: dict = {}
    aggregate: Optional[int] = None
    results_approved_by: Optional[str] = None
    results_approved_at: Optional[datetime] = None

    programme_choices: List[dict] = []
    allocated_programme_id: Optional[str] = None

    is_eligible: bool = False
    eligibility_reason: Optional[str] = None
    merit_score: Optional[float] = None
    merit_rank: Optional[int] = None

    offer_letter_id: Optional[str] = None
    offer_accepted: bool = False
    offer_accepted_at: Optional[datetime] = None

    student_id: Optional[str] = None

    documents: List[str] = []

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "applicants"
        indexes = [
            [("tenant_id", 1), ("user_id", 1)],
            [("tenant_id", 1), ("status", 1)],
            [("tenant_id", 1), ("index_number", 1)],
            [("merit_rank", 1)],
        ]

class ApplicantResult(Document):
    tenant_id: str
    applicant_id: str

    subject: str
    grade: str
    score: Optional[int] = None

    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

    class Settings:
        name = "applicant_results"
