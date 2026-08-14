"""
Application Form Builder
Items 19-31: Build dynamic, configurable admission forms

Allows universities to define custom application forms with:
- Dynamic form fields
- Conditional logic
- Validation rules
- Document requirements
- Payment integration
- WASSCE data collection
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
from beanie import Document, Indexed
import uuid


class FieldType(str, Enum):
    """Supported form field types."""
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    NUMBER = "number"
    DATE = "date"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    FILE = "file"
    ADDRESS = "address"


class FormField(BaseModel):
    """Individual form field definition."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # Technical field name
    label: str  # Display label
    field_type: FieldType
    required: bool = True
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    
    # Options for dropdown/radio
    options: Optional[List[Dict[str, str]]] = None  # [{"label": "...", "value": "..."}]
    
    # Validation rules
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None  # Regex
    
    # File upload
    allowed_file_types: Optional[List[str]] = None  # e.g., ["pdf", "jpg"]
    max_file_size_mb: Optional[int] = None
    
    # Conditional display
    visible_if: Optional[Dict[str, Any]] = None  # {field_name: value_condition}
    
    # Order
    order: int = 0


class FormSection(BaseModel):
    """Logical grouping of form fields."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    fields: List[FormField] = []
    order: int = 0


class ApplicationForm(Document):
    """
    Customizable application form per university.
    
    Universities can configure what data applicants must provide.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: Indexed(str)  # Multi-tenant
    admission_cycle_id: Optional[str] = None  # Optional: per-cycle forms
    
    # Form metadata
    name: str  # e.g., "Undergraduate Application 2026"
    description: Optional[str] = None
    version: int = 1
    
    # Form structure
    sections: List[FormSection] = []
    
    # Settings
    collect_wassce: bool = True  # WASSCE results section
    collect_documents: bool = True  # Document upload section
    documents_required: List[str] = []  # e.g., ["transcript", "birth_certificate"]
    
    # Payment
    application_fee: float = 0.0
    fee_currency: str = "GHS"
    
    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None
    
    class Settings:
        collection = "application_forms"
        indexes = [
            [("tenant_id", 1)],
            [("admission_cycle_id", 1)],
            [("is_active", 1)],
        ]


class WAESSESection(BaseModel):
    """WASSCE/Exam results section of form."""
    examination_type: str  # "WASSCE", "A-Levels", etc.
    examination_year: int
    index_number: str
    examination_center: Optional[str] = None
    
    # Entered grades
    subjects: Dict[str, str] = {}  # {subject: grade}
    
    # Evidence
    evidence_file_path: Optional[str] = None
    verification_status: str = "pending"  # pending, verified, rejected
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None


class ApplicationDocument(BaseModel):
    """Document uploaded with application."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: str  # e.g., "transcript", "birth_certificate"
    file_path: str
    file_name: str
    file_size_bytes: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False
    verification_notes: Optional[str] = None


class FilledApplicationForm(Document):
    """
    Applicant's completed form submission.
    
    Stores the applicant's answers to the form.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: Indexed(str)
    applicant_id: Indexed(str)
    form_id: Indexed(str)
    
    # Form data (dynamic key-value)
    form_data: Dict[str, Any] = {}  # {field_name: value}
    
    # WASSCE (if collected)
    wassce_data: Optional[WAESSESection] = None
    
    # Documents
    documents: List[ApplicationDocument] = []
    
    # Payment
    payment_reference: Optional[str] = None
    payment_verified: bool = False
    payment_verified_at: Optional[datetime] = None
    
    # Status
    status: str = "draft"  # draft, submitted, under_review, completed
    submitted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "filled_application_forms"
        indexes = [
            [("tenant_id", 1)],
            [("applicant_id", 1)],
            [("form_id", 1)],
            [("status", 1)],
            [("payment_verified", 1)],
        ]


# ==================== SCHEMAS ====================

class FormFieldSchema(BaseModel):
    """Schema for form field API."""
    id: Optional[str] = None
    name: str
    label: str
    field_type: FieldType
    required: bool = True
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    options: Optional[List[Dict[str, str]]] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    allowed_file_types: Optional[List[str]] = None
    max_file_size_mb: Optional[int] = None
    visible_if: Optional[Dict[str, Any]] = None
    order: int = 0


class FormSectionSchema(BaseModel):
    """Schema for form section API."""
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    fields: List[FormFieldSchema] = []
    order: int = 0


class CreateApplicationFormRequest(BaseModel):
    """Request to create application form."""
    name: str
    description: Optional[str] = None
    sections: List[FormSectionSchema]
    collect_wassce: bool = True
    collect_documents: bool = True
    documents_required: List[str] = []
    application_fee: float = 0.0


class ApplicationFormResponse(BaseModel):
    """Response model for application form."""
    id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    sections: List[FormSectionSchema]
    collect_wassce: bool
    collect_documents: bool
    application_fee: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SubmitFormResponse(BaseModel):
    """Response after form submission."""
    application_id: str
    status: str
    message: str
    next_steps: List[str]
