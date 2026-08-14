from pydantic import BaseModel, EmailStr
from typing import Optional, List


class RegisterApplicantRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None


class ApplicantDashboardResponse(BaseModel):
    applicant_id: str
    full_name: str
    application_status: str
    overall_progress: int
    sections_completed: int
    total_sections: int
    current_step: str
    can_submit: bool
    submission_deadline: Optional[str] = None
    has_application: bool


class ApplicationFormRequest(BaseModel):
    """Application form submission from applicant portal."""
    # Academic Information
    wassce_year: int
    wassce_index_number: str
    wassce_center: str
    subjects_and_grades: dict  # {"Core Mathematics": "A", "English": "B", ...}
    aggregate: float  # WASSCE aggregate score
    
    # Programme Choices
    choice_1_programme_code: str
    choice_2_programme_code: Optional[str] = None
    choice_3_programme_code: Optional[str] = None
    
    # Additional Information
    statement_of_purpose: Optional[str] = None
    special_needs: Optional[str] = None
    disability_declaration: Optional[str] = None


class ApplicationSubmissionResponse(BaseModel):
    """Response after application submission."""
    status: str  # "success"
    application_id: str
    applicant_id: str
    message: str
    next_steps: str  # e.g., "Please proceed to payment"


class ApplicationStatusResponse(BaseModel):
    """Current status of applicant's application."""
    applicant_id: str
    application_id: Optional[str] = None
    application_status: str  # "draft", "payment_pending", "submitted", etc.
    overall_progress: int  # 0-100%
    submission_deadline: Optional[str] = None
    payment_status: Optional[str] = None
    payment_amount: Optional[float] = None
    documents_uploaded: int
    documents_required: int


class DocumentUploadRequest(BaseModel):
    """Request to upload a document."""
    document_type: str  # e.g., "birth_certificate", "transcript", "passport"
    document_name: str
    # File data is sent as multipart/form-data, not in JSON body


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""
    status: str  # "success"
    document_id: str
    document_type: str
    document_url: str
    uploaded_at: str
    message: str


class DocumentListResponse(BaseModel):
    """List of uploaded documents for applicant."""
    total_documents: int
    required_documents: int
    documents: List[dict]  # [{id, type, name, url, uploaded_at, status}]


class DocumentDeleteResponse(BaseModel):
    """Response after document deletion."""
    status: str  # "success"
    message: str
    documents_remaining: int


class PaymentInitiationRequest(BaseModel):
    """Request to initiate payment for application fee."""
    application_id: str
    amount: float  # Application fee amount
    email: EmailStr


class PaymentInitiationResponse(BaseModel):
    """Response with Paystack authorization URL."""
    status: str  # "success"
    payment_id: str
    authorization_url: str  # Redirect to Paystack
    access_code: str
    reference: str
    message: str
