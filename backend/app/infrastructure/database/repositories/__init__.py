"""Repository exports for the database layer.

This package is used via imports such as:
    from app.infrastructure.database.repositories import ApplicantRepository
"""

from app.infrastructure.database.repositories.academic_calendar_repository import AcademicCalendarRepository
from app.infrastructure.database.repositories.accommodation_repository import (
    HallRepository,
    RoomRepository,
    AccommodationRepository,
    MaintenanceRequestRepository,
)
from app.infrastructure.database.repositories.alumni_repository import (
    AlumniProfileRepository,
    MentorshipRepository,
    DonationRepository,
)
from app.infrastructure.database.repositories.applicant_repository import ApplicantRepository, ApplicantResultRepository
from app.infrastructure.database.repositories.attendance_repository import AttendanceRepository
from app.infrastructure.database.repositories.audit_repository import AuditRepository
from app.infrastructure.database.repositories.course_material_repository import CourseMaterialRepository
from app.infrastructure.database.repositories.course_repository import (
    CourseRepository,
    ProgramRepository,
    FacultyRepository,
    DepartmentRepository,
)
from app.infrastructure.database.repositories.counseling_repository import CounselingRepository
from app.infrastructure.database.repositories.document_repository import DocumentRepository, DigitalSignatureRepository
from app.infrastructure.database.repositories.grade_repository import (
    GradeRepository,
    TranscriptRepository,
    GradeAppealRepository,
)
from app.infrastructure.database.repositories.guardian_repository import GuardianRepository
from app.infrastructure.database.repositories.health_repository import (
    HealthRecordRepository,
    ClinicAppointmentRepository,
)
from app.infrastructure.database.repositories.hr_repository import (
    StaffMemberRepository,
    LeaveRepository,
    PerformanceAppraisalRepository,
)
from app.infrastructure.database.repositories.inventory_repository import (
    AssetRepository,
    InventoryRepository,
    MaintenanceScheduleRepository,
)
from app.infrastructure.database.repositories.library_repository import (
    LibraryBookRepository,
    BorrowingRepository,
    ReservationRepository,
)
from app.infrastructure.database.repositories.notification_repository import (
    NotificationRepository,
    NotificationTemplateRepository,
    CampaignRepository,
)
from app.infrastructure.database.repositories.payment_repository import (
    PaymentRepository,
    ScholarshipRepository,
    FeeStructureRepository,
)
from app.infrastructure.database.repositories.registration_repository import RegistrationRepository
from app.infrastructure.database.repositories.research_repository import (
    ResearchProposalRepository,
    GrantRepository,
    PublicationRepository,
)
from app.infrastructure.database.repositories.student_repository import StudentRepository
from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.infrastructure.database.repositories.university_application_repository import (
    UniversityApplicationRepository,
    IdentifierSequenceRepository,
)
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.workflow_repository import (
    WorkflowRepository,
    WorkflowInstanceRepository,
    ApprovalTaskRepository,
)

__all__ = [
    "AcademicCalendarRepository",
    "HallRepository",
    "RoomRepository",
    "AccommodationRepository",
    "MaintenanceRequestRepository",
    "AlumniProfileRepository",
    "MentorshipRepository",
    "DonationRepository",
    "ApplicantRepository",
    "ApplicantResultRepository",
    "AttendanceRepository",
    "AuditRepository",
    "CourseMaterialRepository",
    "CourseRepository",
    "ProgramRepository",
    "FacultyRepository",
    "DepartmentRepository",
    "CounselingRepository",
    "DocumentRepository",
    "DigitalSignatureRepository",
    "GradeRepository",
    "TranscriptRepository",
    "GradeAppealRepository",
    "GuardianRepository",
    "HealthRecordRepository",
    "ClinicAppointmentRepository",
    "StaffMemberRepository",
    "LeaveRepository",
    "PerformanceAppraisalRepository",
    "AssetRepository",
    "InventoryRepository",
    "MaintenanceScheduleRepository",
    "LibraryBookRepository",
    "BorrowingRepository",
    "ReservationRepository",
    "NotificationRepository",
    "NotificationTemplateRepository",
    "CampaignRepository",
    "PaymentRepository",
    "ScholarshipRepository",
    "FeeStructureRepository",
    "RegistrationRepository",
    "ResearchProposalRepository",
    "GrantRepository",
    "PublicationRepository",
    "StudentRepository",
    "TenantRepository",
    "UniversityApplicationRepository",
    "IdentifierSequenceRepository",
    "UserRepository",
    "WorkflowRepository",
    "WorkflowInstanceRepository",
    "ApprovalTaskRepository",
]
