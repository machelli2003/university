from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CreateApplicantRequest(BaseModel):
    first_name: str
    last_name: str
    phone: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    region: Optional[str] = None

class ProgrammeChoice(BaseModel):
    programme_id: str
    choice_order: int

class SubmitApplicationRequest(BaseModel):
    index_number: str
    exam_year: int
    exam_type: str
    programme_choices: List[ProgrammeChoice]

class SubmitResultsRequest(BaseModel):
    results: Dict[str, str]

class WAECVerifyRequest(BaseModel):
    pin: str

class ApproveResultsRequest(BaseModel):
    aggregate: Optional[int] = None

class RejectResultsRequest(BaseModel):
    reason: str

class RejectOfferRequest(BaseModel):
    reason: Optional[str] = None

class ApplicantResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    phone: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    nationality: Optional[str] = None
    status: str
    index_number: Optional[str] = None
    exam_year: Optional[int] = None
    exam_type: Optional[str] = None
    results: Dict[str, Any] = {}
    programme_choices: Optional[List[Dict[str, Any]]] = None
    statement_of_purpose: Optional[str] = None
    special_needs: Optional[str] = None
    disability_declaration: Optional[str] = None
    aggregate: Optional[int] = None
    is_eligible: bool = True
    merit_score: Optional[float] = None
    merit_rank: Optional[int] = None
    allocated_programme_id: Optional[str] = None
    student_id: Optional[str] = None
    created_at: datetime

class RankingResultItem(BaseModel):
    applicant_id: str
    merit_score: float
    merit_rank: int
    aggregate: Optional[int]

class AllocationSummaryResponse(BaseModel):
    total_processed: int
    allocated: int
    waitlisted: int

class ProcessAdmissionsSummaryResponse(BaseModel):
    eligible: int
    ineligible: int
    ranked: int
    allocated: int
    waitlisted: int
    offers_published: int

# --- New models for Admissions Officer features ---
class OverrideRequest(BaseModel):
    merit_score: Optional[float] = None
    is_eligible: Optional[bool] = None
    eligibility_reason: Optional[str] = None

class PromoteWaitlistRequest(BaseModel):
    programme_id: str
    count: Optional[int] = 1

class ProgramCapacityResponse(BaseModel):
    programme_id: str
    capacity_planned: int
    capacity_current: int
    capacity_reserved: int
    available: int

class WaitlistItem(BaseModel):
    id: str
    first_name: str
    last_name: str
    merit_rank: Optional[int]
    allocated_programme_id: Optional[str]
    created_at: datetime
