from beanie import Document
from pydantic import Field, EmailStr, BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class UniversityApplicationStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING_SETUP = "pending_setup"
    SUBMITTED = "submitted"
    AWAITING_SUPER_ADMIN_APPROVAL = "awaiting_super_admin_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROVISIONING = "provisioning"
    ACTIVE = "active"


# ==================== STEP 1: UNIVERSITY INFORMATION ====================
class UniversityInformation(BaseModel):
    legal_name: str
    display_name: Optional[str] = None
    school_code: str
    institution_type: Optional[str] = None  # e.g., University, Polytechnic, College
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
    academic_calendar_type: Optional[str] = None  # Semester, Trimester, etc.
    timezone: Optional[str] = "Africa/Accra"
    currency: Optional[str] = "GHS"


# ==================== STEP 2: IDENTIFIER CONFIGURATION ====================
class IdentifierFormatConfig(BaseModel):
    format_pattern: str  # e.g., "{SCHOOL_CODE}-{YEAR}-{SEQUENCE}"
    prefix: Optional[str] = None
    starting_sequence: int = 1
    year_inclusion: bool = False
    includes_faculty_prefix: bool = False
    includes_department_prefix: bool = False


class IDConfiguration(BaseModel):
    student_id: IdentifierFormatConfig = Field(
        default=IdentifierFormatConfig(format_pattern="{SCHOOL_CODE}-{YEAR}-{SEQUENCE}")
    )
    staff_id: IdentifierFormatConfig = Field(
        default=IdentifierFormatConfig(format_pattern="{SCHOOL_CODE}-STF-{SEQUENCE}")
    )
    applicant_id: IdentifierFormatConfig = Field(
        default=IdentifierFormatConfig(format_pattern="{SCHOOL_CODE}-APP-{YEAR}-{SEQUENCE}")
    )
    university_application_id: IdentifierFormatConfig = Field(
        default=IdentifierFormatConfig(format_pattern="UAPP-{YEAR}-{SEQUENCE}")
    )


# ==================== STEP 3: ACADEMIC YEARS ====================
class AcademicSemester(BaseModel):
    name: str  # e.g., "Semester 1"
    start_date: datetime
    end_date: datetime
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    exam_start: Optional[datetime] = None
    exam_end: Optional[datetime] = None
    result_publication_date: Optional[datetime] = None


class AcademicYear(BaseModel):
    year: str  # e.g., "2026/2027"
    start_date: datetime
    end_date: datetime
    semesters: List[AcademicSemester] = []
    is_current: bool = False


class AcademicYearConfiguration(BaseModel):
    current_year: Optional[str] = None
    academic_years: List[AcademicYear] = []


# ==================== STEP 4: FACULTIES ====================
class FacultyInfo(BaseModel):
    faculty_code: str
    name: str
    description: Optional[str] = None
    dean_id: Optional[str] = None
    status: str = "active"  # active, inactive


class FacultiesConfiguration(BaseModel):
    faculties: List[FacultyInfo] = []


# ==================== STEP 5: DEPARTMENTS ====================
class DepartmentInfo(BaseModel):
    department_code: str
    name: str
    faculty_code: str
    hod_id: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"


class DepartmentsConfiguration(BaseModel):
    departments: List[DepartmentInfo] = []


# ==================== STEP 6: PROGRAMMES ====================
class ProgrammeAdmissionCategory(BaseModel):
    category_type: str  # Regular, Fee Paying, Mature, International, etc.
    capacity: int
    requirements: Optional[str] = None


class ProgrammeInfo(BaseModel):
    programme_code: str
    name: str
    faculty_code: str
    department_code: str
    degree_type: str  # BSc, MSc, PhD, Diploma, etc.
    duration_years: int
    study_mode: str  # Regular, Evening, Distance, etc.
    status: str = "active"
    capacity: int
    admission_categories: List[ProgrammeAdmissionCategory] = []
    minimum_requirements: Optional[str] = None
    required_documents: List[str] = []
    credit_requirements: Optional[int] = None


class ProgrammesConfiguration(BaseModel):
    programmes: List[ProgrammeInfo] = []


# ==================== STEP 7: COURSES ====================
class CourseInfo(BaseModel):
    course_code: str
    title: str
    credit_hours: float
    level: str  # 100, 200, 300, 400
    semester: str  # 1, 2
    department_code: str
    prerequisites: List[str] = []
    course_type: str  # Theory, Practical, Mixed
    is_mandatory: bool = False


class CoursesConfiguration(BaseModel):
    courses: List[CourseInfo] = []


# ==================== STEP 8: ADMISSION CYCLES ====================
class AdmissionCycleStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    OPEN = "open"
    CLOSED = "closed"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class AdmissionCycleInfo(BaseModel):
    cycle_name: str
    academic_year: str
    admission_type: str  # Undergraduate, Postgraduate, Transfer
    opening_date: datetime
    opening_time: str  # HH:MM format
    closing_date: datetime
    closing_time: str  # HH:MM format
    acceptance_deadline: Optional[datetime] = None
    enrollment_deadline: Optional[datetime] = None
    application_fee: float = 0.0
    currency: Optional[str] = "GHS"
    status: AdmissionCycleStatus = AdmissionCycleStatus.DRAFT


class AdmissionCycleConfiguration(BaseModel):
    admission_cycles: List[AdmissionCycleInfo] = []


# ==================== STEP 9: ADMISSION CATEGORIES ====================
class AdmissionCategoryConfig(BaseModel):
    category_type: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    capacity_percentage: Optional[float] = None


class AdmissionCategoriesConfiguration(BaseModel):
    categories: List[AdmissionCategoryConfig] = []


# ==================== STEP 10: PROGRAMME ADMISSION REQUIREMENTS ====================
class ProgrammeRequirementSubject(BaseModel):
    name: str
    grade: Optional[str] = None
    is_mandatory: bool = False


class ProgrammeRequirementInfo(BaseModel):
    programme_code: str
    mandatory_subjects: List[ProgrammeRequirementSubject] = []
    elective_subjects: List[ProgrammeRequirementSubject] = []
    minimum_grade_aggregate: Optional[int] = None
    additional_requirements: Optional[str] = None


class AdmissionRequirementsConfiguration(BaseModel):
    programme_requirements: List[ProgrammeRequirementInfo] = []


# ==================== STEP 11: APPLICATION FORM CONFIGURATION ====================
class ApplicationFormField(BaseModel):
    field_name: str
    field_type: str  # text, email, date, select, file, etc.
    category: str  # personal, identification, academic, programme, documents
    is_required: bool = True
    validation_rules: Optional[str] = None


class ApplicationFormConfiguration(BaseModel):
    fields: List[ApplicationFormField] = []
    allow_multiple_programme_choices: bool = True
    max_programme_choices: int = 3


# ==================== STEP 12: APPLICATION FEE CONFIGURATION ====================
class ApplicationFeeConfiguration(BaseModel):
    fee_amount: float
    currency: str = "GHS"
    payment_provider: str  # "paystack", "stripe", "manual", etc.
    payment_deadline: Optional[datetime] = None
    refund_policy: Optional[str] = None
    fee_categories: Dict[str, float] = {}  # e.g., {"regular": 100, "international": 150}


# ==================== STEP 13: STAFF SETUP ====================
class InitialStaffMember(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    staff_role: str  # Registrar, Admissions Officer, etc.
    department_code: Optional[str] = None
    faculty_code: Optional[str] = None


class StaffSetupConfiguration(BaseModel):
    staff_members: List[InitialStaffMember] = []


# ==================== STEP 14: ROLE & PERMISSION CONFIGURATION ====================
class RolePermission(BaseModel):
    permission_code: str
    permission_name: str


class RoleConfigInfo(BaseModel):
    role_name: str
    permissions: List[RolePermission] = []


class RolePermissionConfiguration(BaseModel):
    roles: List[RoleConfigInfo] = []


# ==================== STEP 15-17: ID CONFIGURATION (Separate sections for students/staff/applicants) ====================
class StudentIDConfiguration(BaseModel):
    format_pattern: str
    starting_sequence: int = 1
    year_inclusion: bool = True
    faculty_prefix_inclusion: bool = False


class StaffIDConfiguration(BaseModel):
    format_pattern: str
    starting_sequence: int = 1
    department_prefix_inclusion: bool = False


class ApplicantIDConfiguration(BaseModel):
    format_pattern: str
    starting_sequence: int = 1
    year_inclusion: bool = True


# ==================== STEP 18: HOSTEL CONFIGURATION ====================
class HostelBed(BaseModel):
    bed_number: str
    capacity: int = 1


class HostelRoom(BaseModel):
    room_number: str
    block: Optional[str] = None
    beds: List[HostelBed] = []


class HostelInfo(BaseModel):
    hostel_name: str
    hostel_code: Optional[str] = None
    capacity: int
    rooms: List[HostelRoom] = []
    hostel_fee: float = 0.0
    eligibility_criteria: Optional[str] = None
    allocation_rules: Optional[str] = None


class HostelConfiguration(BaseModel):
    hostels: List[HostelInfo] = []


# ==================== STEP 19: FINANCE CONFIGURATION ====================
class FeeStructureItem(BaseModel):
    fee_type: str  # Tuition, Accommodation, Library, etc.
    amount: float
    currency: str = "GHS"
    programme_code: Optional[str] = None  # Can be programme-specific


class FinanceConfiguration(BaseModel):
    fee_structures: List[FeeStructureItem] = []
    payment_methods: List[str] = ["paystack"]
    scholarship_rules: Optional[str] = None
    discount_rules: Optional[str] = None
    penalty_rules: Optional[str] = None
    refund_rules: Optional[str] = None


# ==================== STEP 20: LIBRARY CONFIGURATION ====================
class LibraryConfiguration(BaseModel):
    borrowing_rules: Optional[str] = None
    standard_borrowing_period_days: int = 14
    fine_per_day: float = 0.0
    max_books_per_borrowing: int = 5
    membership_rules: Optional[str] = None
    categories: List[str] = []


# ==================== STEP 21: GRADING CONFIGURATION ====================
class GradeScale(BaseModel):
    grade: str  # A1, A2, B1, etc.
    gpa_value: float
    range_start: int  # e.g., 90
    range_end: int  # e.g., 100


class GradingConfiguration(BaseModel):
    grade_scales: List[GradeScale] = []
    gpa_scale: float = 4.0
    cgpa_scale: float = 4.0
    pass_mark: int = 40
    ca_percentage: int = 40
    exam_percentage: int = 60
    resit_allowed: bool = True
    academic_standing_rules: Optional[str] = None


# ==================== STEP 22: GRADUATION CONFIGURATION ====================
class GraduationConfiguration(BaseModel):
    minimum_credits: int = 120
    minimum_cgpa: float = 1.0
    clearance_requirements: Optional[str] = None
    certificate_template: Optional[str] = None
    transcript_settings: Optional[str] = None


# ==================== STEP 23: MODULE ENABLEMENT ====================
class ModuleEnablement(BaseModel):
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


# ==================== MAIN UNIVERSITY APPLICATION DOCUMENT ====================
class UniversityApplication(Document):
    # ===== IDENTIFIERS =====
    university_application_id: str  # e.g., UAPP-2026-000001
    tenant_id: Optional[str] = None  # Only set after approval/provisioning
    
    # ===== APPLICATION TRACKING =====
    status: UniversityApplicationStatusEnum = UniversityApplicationStatusEnum.DRAFT
    requested_by: Optional[str] = None  # User who initiated the application
    admin_first_name: Optional[str] = None
    admin_last_name: Optional[str] = None
    admin_email: Optional[EmailStr] = None
    
    # ===== WORKFLOW DATES =====
    submitted_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    review_requested_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    provisioned_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    
    # ===== SETUP SECTIONS TRACKING =====
    setup_sections: Dict[str, bool] = Field(default_factory=lambda: {
        "university_information": False,
        "id_configuration": False,
        "academic_years": False,
        "faculties": False,
        "departments": False,
        "programmes": False,
        "courses": False,
        "admission_cycle": False,
        "admission_categories": False,
        "admission_requirements": False,
        "application_form": False,
        "application_fee": False,
        "staff": False,
        "role_permission": False,
        "student_id_configuration": False,
        "staff_id_configuration": False,
        "applicant_id_configuration": False,
        "hostel": False,
        "finance": False,
        "library": False,
        "grading": False,
        "graduation": False,
        "module_enablement": False,
    })
    
    # ===== WIZARD SECTIONS =====
    # Step 1: University Information
    university_information: Optional[UniversityInformation] = None
    
    # Step 2: ID Configuration
    id_configuration: Optional[IDConfiguration] = None
    
    # Step 3: Academic Years
    academic_year_configuration: Optional[AcademicYearConfiguration] = None
    
    # Step 4: Faculties
    faculties_configuration: Optional[FacultiesConfiguration] = None
    
    # Step 5: Departments
    departments_configuration: Optional[DepartmentsConfiguration] = None
    
    # Step 6: Programmes
    programmes_configuration: Optional[ProgrammesConfiguration] = None
    
    # Step 7: Courses
    courses_configuration: Optional[CoursesConfiguration] = None
    
    # Step 8: Admission Cycles
    admission_cycle_configuration: Optional[AdmissionCycleConfiguration] = None
    
    # Step 9: Admission Categories
    admission_categories_configuration: Optional[AdmissionCategoriesConfiguration] = None
    
    # Step 10: Admission Requirements
    admission_requirements_configuration: Optional[AdmissionRequirementsConfiguration] = None
    
    # Step 11: Application Form
    application_form_configuration: Optional[ApplicationFormConfiguration] = None
    
    # Step 12: Application Fee
    application_fee_configuration: Optional[ApplicationFeeConfiguration] = None
    
    # Step 13: Staff Setup
    staff_setup_configuration: Optional[StaffSetupConfiguration] = None
    
    # Step 14: Role & Permission Configuration
    role_permission_configuration: Optional[RolePermissionConfiguration] = None
    
    # Step 15: Student ID Configuration
    student_id_configuration: Optional[StudentIDConfiguration] = None
    
    # Step 16: Staff ID Configuration
    staff_id_configuration: Optional[StaffIDConfiguration] = None
    
    # Step 17: Applicant ID Configuration
    applicant_id_configuration: Optional[ApplicantIDConfiguration] = None
    
    # Step 18: Hostel Configuration
    hostel_configuration: Optional[HostelConfiguration] = None
    
    # Step 19: Finance Configuration
    finance_configuration: Optional[FinanceConfiguration] = None
    
    # Step 20: Library Configuration
    library_configuration: Optional[LibraryConfiguration] = None
    
    # Step 21: Grading Configuration
    grading_configuration: Optional[GradingConfiguration] = None
    
    # Step 22: Graduation Configuration
    graduation_configuration: Optional[GraduationConfiguration] = None
    
    # Step 23: Module Enablement
    module_enablement: Optional[ModuleEnablement] = None
    
    # ===== TIMESTAMPS =====
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "university_applications"
        indexes = [
            [("university_application_id", 1)],
            [("school_code", 1)],
            [("status", 1)],
            [("tenant_id", 1)],
        ]


class IdentifierSequence(Document):
    tenant_id: Optional[str] = None
    sequence_type: str
    year: Optional[int] = None
    sequence: int = 0
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "identifier_sequences"
        indexes = [
            [("tenant_id", 1), ("sequence_type", 1), ("year", 1)],
        ]
