from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List, Any
from enum import Enum

# ==================== SHARED ENUMS & MODELS ====================

class UniversityApplicationStatusResponse(str, Enum):
    DRAFT = "draft"
    PENDING_SETUP = "pending_setup"
    SUBMITTED = "submitted"
    AWAITING_SUPER_ADMIN_APPROVAL = "awaiting_super_admin_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROVISIONING = "provisioning"
    ACTIVE = "active"


# ==================== STEP 1: UNIVERSITY INFORMATION ====================

class CreateUniversityApplicationRequest(BaseModel):
    legal_name: str
    display_name: Optional[str] = None
    school_code: str
    admin_first_name: str
    admin_last_name: str
    admin_email: EmailStr
    institution_type: Optional[str] = None
    is_public: Optional[bool] = None
    location: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    postal_address: Optional[str] = None
    official_email: Optional[EmailStr] = None
    official_phone: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    description: Optional[str] = None
    academic_calendar_type: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None


class UpdateUniversityInformationRequest(BaseModel):
    legal_name: Optional[str] = None
    display_name: Optional[str] = None
    school_code: Optional[str] = None
    institution_type: Optional[str] = None
    is_public: Optional[bool] = None
    location: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    postal_address: Optional[str] = None
    official_email: Optional[EmailStr] = None
    official_phone: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    description: Optional[str] = None
    academic_calendar_type: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None


class UpdateUniversityApplicationRequest(UpdateUniversityInformationRequest):
    """Backward-compatible alias for generic university application updates."""
    pass


# ==================== STEP 2: ID CONFIGURATION ====================

class IdentifierFormatConfigRequest(BaseModel):
    format_pattern: str
    prefix: Optional[str] = None
    starting_sequence: int = 1
    year_inclusion: bool = False
    includes_faculty_prefix: bool = False
    includes_department_prefix: bool = False


class UpdateIDConfigurationRequest(BaseModel):
    student_id: Optional[IdentifierFormatConfigRequest] = None
    staff_id: Optional[IdentifierFormatConfigRequest] = None
    applicant_id: Optional[IdentifierFormatConfigRequest] = None
    university_application_id: Optional[IdentifierFormatConfigRequest] = None


# ==================== STEP 3: ACADEMIC YEARS ====================

class AcademicSemesterRequest(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    exam_start: Optional[datetime] = None
    exam_end: Optional[datetime] = None
    result_publication_date: Optional[datetime] = None


class AcademicYearRequest(BaseModel):
    year: str
    start_date: datetime
    end_date: datetime
    semesters: List[AcademicSemesterRequest] = []
    is_current: bool = False


class UpdateAcademicYearConfigurationRequest(BaseModel):
    current_year: Optional[str] = None
    academic_years: Optional[List[AcademicYearRequest]] = None


# ==================== STEP 4: FACULTIES ====================

class FacultyInfoRequest(BaseModel):
    faculty_code: str
    name: str
    description: Optional[str] = None
    dean_id: Optional[str] = None
    status: str = "active"


class UpdateFacultiesConfigurationRequest(BaseModel):
    faculties: List[FacultyInfoRequest] = []


# ==================== STEP 5: DEPARTMENTS ====================

class DepartmentInfoRequest(BaseModel):
    department_code: str
    name: str
    faculty_code: str
    hod_id: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"


class UpdateDepartmentsConfigurationRequest(BaseModel):
    departments: List[DepartmentInfoRequest] = []


# ==================== STEP 6: PROGRAMMES ====================

class ProgrammeAdmissionCategoryRequest(BaseModel):
    category_type: str
    capacity: int
    requirements: Optional[str] = None


class ProgrammeInfoRequest(BaseModel):
    programme_code: str
    name: str
    faculty_code: str
    department_code: str
    degree_type: str
    duration_years: int
    study_mode: str
    status: str = "active"
    capacity: int
    admission_categories: List[ProgrammeAdmissionCategoryRequest] = []
    minimum_requirements: Optional[str] = None
    required_documents: List[str] = []
    credit_requirements: Optional[int] = None


class UpdateProgrammesConfigurationRequest(BaseModel):
    programmes: List[ProgrammeInfoRequest] = []


# ==================== STEP 7: COURSES ====================

class CourseInfoRequest(BaseModel):
    course_code: str
    title: str
    credit_hours: float
    level: str
    semester: str
    department_code: str
    prerequisites: List[str] = []
    course_type: str
    is_mandatory: bool = False


class UpdateCoursesConfigurationRequest(BaseModel):
    courses: List[CourseInfoRequest] = []


# ==================== STEP 8: ADMISSION CYCLES ====================

class AdmissionCycleInfoRequest(BaseModel):
    cycle_name: str
    academic_year: str
    admission_type: str
    opening_date: datetime
    opening_time: str
    closing_date: datetime
    closing_time: str
    acceptance_deadline: Optional[datetime] = None
    enrollment_deadline: Optional[datetime] = None
    application_fee: float = 0.0
    currency: Optional[str] = "GHS"
    status: str = "draft"


class UpdateAdmissionCycleConfigurationRequest(BaseModel):
    admission_cycles: List[AdmissionCycleInfoRequest] = []


# ==================== STEP 9: ADMISSION CATEGORIES ====================

class AdmissionCategoryConfigRequest(BaseModel):
    category_type: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    capacity_percentage: Optional[float] = None


class UpdateAdmissionCategoriesConfigurationRequest(BaseModel):
    categories: List[AdmissionCategoryConfigRequest] = []


# ==================== STEP 10: PROGRAMME ADMISSION REQUIREMENTS ====================

class ProgrammeRequirementSubjectRequest(BaseModel):
    name: str
    grade: Optional[str] = None
    is_mandatory: bool = False


class ProgrammeRequirementInfoRequest(BaseModel):
    programme_code: str
    mandatory_subjects: List[ProgrammeRequirementSubjectRequest] = []
    elective_subjects: List[ProgrammeRequirementSubjectRequest] = []
    minimum_grade_aggregate: Optional[int] = None
    additional_requirements: Optional[str] = None


class UpdateAdmissionRequirementsConfigurationRequest(BaseModel):
    programme_requirements: List[ProgrammeRequirementInfoRequest] = []


# ==================== STEP 11: APPLICATION FORM CONFIGURATION ====================

class ApplicationFormFieldRequest(BaseModel):
    field_name: str
    field_type: str
    category: str
    is_required: bool = True
    validation_rules: Optional[str] = None


class UpdateApplicationFormConfigurationRequest(BaseModel):
    fields: List[ApplicationFormFieldRequest] = []
    allow_multiple_programme_choices: bool = True
    max_programme_choices: int = 3


# ==================== STEP 12: APPLICATION FEE CONFIGURATION ====================

class UpdateApplicationFeeConfigurationRequest(BaseModel):
    fee_amount: float
    currency: str = "GHS"
    payment_provider: str
    payment_deadline: Optional[datetime] = None
    refund_policy: Optional[str] = None
    fee_categories: Optional[Dict[str, float]] = None


# ==================== STEP 13: STAFF SETUP ====================

class InitialStaffMemberRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    staff_role: str
    department_code: Optional[str] = None
    faculty_code: Optional[str] = None


class UpdateStaffSetupConfigurationRequest(BaseModel):
    staff_members: List[InitialStaffMemberRequest] = []


# ==================== STEP 14: ROLE & PERMISSION CONFIGURATION ====================

class RolePermissionRequest(BaseModel):
    permission_code: str
    permission_name: str


class RoleConfigInfoRequest(BaseModel):
    role_name: str
    permissions: List[RolePermissionRequest] = []


class UpdateRolePermissionConfigurationRequest(BaseModel):
    roles: List[RoleConfigInfoRequest] = []


# ==================== STEP 15-17: ID CONFIGURATION ====================

class UpdateStudentIDConfigurationRequest(BaseModel):
    format_pattern: str
    starting_sequence: int = 1
    year_inclusion: bool = True
    faculty_prefix_inclusion: bool = False


class UpdateStaffIDConfigurationRequest(BaseModel):
    format_pattern: str
    starting_sequence: int = 1
    department_prefix_inclusion: bool = False


class UpdateApplicantIDConfigurationRequest(BaseModel):
    format_pattern: str
    starting_sequence: int = 1
    year_inclusion: bool = True


# ==================== STEP 18: HOSTEL CONFIGURATION ====================

class HostelBedRequest(BaseModel):
    bed_number: str
    capacity: int = 1


class HostelRoomRequest(BaseModel):
    room_number: str
    block: Optional[str] = None
    beds: List[HostelBedRequest] = []


class HostelInfoRequest(BaseModel):
    hostel_name: str
    hostel_code: Optional[str] = None
    capacity: int
    rooms: List[HostelRoomRequest] = []
    hostel_fee: float = 0.0
    eligibility_criteria: Optional[str] = None
    allocation_rules: Optional[str] = None


class UpdateHostelConfigurationRequest(BaseModel):
    hostels: List[HostelInfoRequest] = []


# ==================== STEP 19: FINANCE CONFIGURATION ====================

class FeeStructureItemRequest(BaseModel):
    fee_type: str
    amount: float
    currency: str = "GHS"
    programme_code: Optional[str] = None


class UpdateFinanceConfigurationRequest(BaseModel):
    fee_structures: List[FeeStructureItemRequest] = []
    payment_methods: List[str] = ["paystack"]
    scholarship_rules: Optional[str] = None
    discount_rules: Optional[str] = None
    penalty_rules: Optional[str] = None
    refund_rules: Optional[str] = None


# ==================== STEP 20: LIBRARY CONFIGURATION ====================

class UpdateLibraryConfigurationRequest(BaseModel):
    borrowing_rules: Optional[str] = None
    standard_borrowing_period_days: int = 14
    fine_per_day: float = 0.0
    max_books_per_borrowing: int = 5
    membership_rules: Optional[str] = None
    categories: List[str] = []


# ==================== STEP 21: GRADING CONFIGURATION ====================

class GradeScaleRequest(BaseModel):
    grade: str
    gpa_value: float
    range_start: int
    range_end: int


class UpdateGradingConfigurationRequest(BaseModel):
    grade_scales: List[GradeScaleRequest] = []
    gpa_scale: float = 4.0
    cgpa_scale: float = 4.0
    pass_mark: int = 40
    ca_percentage: int = 40
    exam_percentage: int = 60
    resit_allowed: bool = True
    academic_standing_rules: Optional[str] = None


# ==================== STEP 22: GRADUATION CONFIGURATION ====================

class UpdateGraduationConfigurationRequest(BaseModel):
    minimum_credits: int = 120
    minimum_cgpa: float = 1.0
    clearance_requirements: Optional[str] = None
    certificate_template: Optional[str] = None
    transcript_settings: Optional[str] = None


# ==================== STEP 23: MODULE ENABLEMENT ====================

class UpdateModuleEnablementRequest(BaseModel):
    admissions: bool = True
    academics: bool = True
    finance: bool = True
    accommodation: bool = False
    library: bool = False
    examinations: bool = True
    alumni: bool = False
    health: bool = False
    research: bool = False
    hr: bool = False


# ==================== REJECTION & SUBMISSION ====================

class RejectUniversityApplicationRequest(BaseModel):
    reason: str


class RequestUniversityApplicationChangesRequest(BaseModel):
    reason: str


class ApproveUniversityApplicationRequest(BaseModel):
    approval_notes: Optional[str] = None


# ==================== GENERIC UPDATE ====================

class UpdateSetupSectionRequest(BaseModel):
    completed: bool


# ==================== RESPONSE MODELS ====================

class UniversityApplicationResponse(BaseModel):
    id: str
    university_application_id: str
    status: str
    requested_by: Optional[str] = None
    admin_first_name: Optional[str] = None
    admin_last_name: Optional[str] = None
    admin_email: Optional[EmailStr] = None
    review_notes: Optional[str] = None
    review_requested_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    provisioned_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    tenant_id: Optional[str] = None
    setup_sections: Dict[str, bool]
    university_information: Optional[Dict[str, Any]] = None
    id_configuration: Optional[Dict[str, Any]] = None
    academic_year_configuration: Optional[Dict[str, Any]] = None
    faculties_configuration: Optional[Dict[str, Any]] = None
    departments_configuration: Optional[Dict[str, Any]] = None
    programmes_configuration: Optional[Dict[str, Any]] = None
    courses_configuration: Optional[Dict[str, Any]] = None
    admission_cycle_configuration: Optional[Dict[str, Any]] = None
    admission_categories_configuration: Optional[Dict[str, Any]] = None
    admission_requirements_configuration: Optional[Dict[str, Any]] = None
    application_form_configuration: Optional[Dict[str, Any]] = None
    application_fee_configuration: Optional[Dict[str, Any]] = None
    staff_setup_configuration: Optional[Dict[str, Any]] = None
    role_permission_configuration: Optional[Dict[str, Any]] = None
    student_id_configuration: Optional[Dict[str, Any]] = None
    staff_id_configuration: Optional[Dict[str, Any]] = None
    applicant_id_configuration: Optional[Dict[str, Any]] = None
    hostel_configuration: Optional[Dict[str, Any]] = None
    finance_configuration: Optional[Dict[str, Any]] = None
    library_configuration: Optional[Dict[str, Any]] = None
    grading_configuration: Optional[Dict[str, Any]] = None
    graduation_configuration: Optional[Dict[str, Any]] = None
    module_enablement: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
