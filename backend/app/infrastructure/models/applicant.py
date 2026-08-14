from beanie import Document, Indexed
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ApplicationStatusEnum(str, Enum):
    """
    Section 39: Complete 20-State Application Lifecycle Workflow
    
    State Transition Flow:
    
    INITIAL PHASE (Applicant Entry):
    - DRAFT → SUBMITTED (applicant completes and submits)
    - SUBMITTED → PAYMENT_PENDING (payment required before processing)
    
    PAYMENT & DOCUMENT PHASE:
    - PAYMENT_PENDING → PAYMENT_VERIFIED (payment confirmed)
    - PAYMENT_VERIFIED → DOCUMENT_REVIEW (admin reviews supporting docs)
    - DOCUMENT_REVIEW → ELIGIBILITY_CHECK (prereq validation)
    
    ELIGIBILITY & REVIEW PHASE:
    - ELIGIBILITY_CHECK → ELIGIBLE (meets prerequisites)
    - ELIGIBILITY_CHECK → INELIGIBLE (doesn't meet prerequisites)
    - ELIGIBLE → UNDER_REVIEW (application enters review queue)
    - UNDER_REVIEW → DEPARTMENT_REVIEW (department evaluates)
    - DEPARTMENT_REVIEW → FACULTY_REVIEW (faculty head reviews)
    - FACULTY_REVIEW → COMMITTEE_REVIEW (admissions committee meets)
    - COMMITTEE_REVIEW → MANUAL_REVIEW (edge cases requiring manual input)
    - MANUAL_REVIEW → COMMITTEE_REVIEW (after manual processing)
    
    DECISION PHASE:
    - COMMITTEE_REVIEW → OFFERED (admission approved unconditionally)
    - COMMITTEE_REVIEW → CONDITIONALLY_ADMITTED (approved with conditions)
    - COMMITTEE_REVIEW → RANKED (placed in ranking pool)
    - RANKED → ALLOCATED (offered via ranking)
    - RANKED → WAITLISTED (placed on waitlist)
    - COMMITTEE_REVIEW → REJECTED (not admitted)
    - INELIGIBLE → REJECTED (automatically rejected)
    
    ENROLLMENT PHASE:
    - OFFERED → ENROLLMENT_PENDING (awaiting enrollment)
    - CONDITIONALLY_ADMITTED → ENROLLMENT_PENDING (conditions accepted)
    - ALLOCATED → ENROLLMENT_PENDING (allocated in ranking)
    - ENROLLMENT_PENDING → ENROLLED (completed enrollment & registration)
    
    TERMINAL STATES (No further transitions):
    - REJECTED (permanent rejection)
    - ENROLLED (successfully enrolled)
    - WAITLISTED (permanent for this admissions cycle)
    """
    
    # Initial Phase
    DRAFT = "draft"
    SUBMITTED = "submitted"
    AWAITING_RESULTS = "awaiting_results"
    RESULTS_UPLOADED = "results_uploaded"
    RESULTS_APPROVED = "results_approved"
    
    # Payment & Document Phase
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_VERIFIED = "payment_verified"
    DOCUMENT_REVIEW = "document_review"
    
    # Eligibility & Review Phase
    ELIGIBILITY_CHECK = "eligibility_check"
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    UNDER_REVIEW = "under_review"
    DEPARTMENT_REVIEW = "department_review"
    FACULTY_REVIEW = "faculty_review"
    COMMITTEE_REVIEW = "committee_review"
    MANUAL_REVIEW = "manual_review"
    
    # Decision Phase
    RANKED = "ranked"
    ALLOCATED = "allocated"
    OFFERED = "offered"
    CONDITIONALLY_ADMITTED = "conditionally_admitted"
    WAITLISTED = "waitlisted"
    REJECTED = "rejected"
    
    # Enrollment Phase
    ENROLLMENT_PENDING = "enrollment_pending"
    ENROLLED = "enrolled"

class VerificationStatusEnum(str, Enum):
    """WASSCE verification status (Section 36)."""
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    REJECTED = "rejected"
    REQUIRES_CORRECTION = "requires_correction"

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

    # WASSCE Verification Fields (Section 36)
    verification_status: VerificationStatusEnum = VerificationStatusEnum.PENDING_VERIFICATION
    verified_by: Optional[str] = None  # Staff member ID who verified
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None  # Officer's notes on verification

    programme_choices: List[dict] = []
    allocated_programme_id: Optional[str] = None

    is_eligible: bool = False
    eligibility_reason: Optional[str] = None
    merit_score: Optional[float] = None
    merit_rank: Optional[int] = None

    # Offer Management (Item 61: Student Lifecycle)
    offer_id: Optional[str] = None
    offer_letter_id: Optional[str] = None
    offer_accepted: bool = False
    offer_accepted_at: Optional[datetime] = None
    offer_acceptance_date: Optional[datetime] = None
    offer_rejected: bool = False
    offer_rejected_at: Optional[datetime] = None
    offer_rejection_date: Optional[datetime] = None
    offer_rejection_reason: Optional[str] = None

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
            [("verification_status", 1)],
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
