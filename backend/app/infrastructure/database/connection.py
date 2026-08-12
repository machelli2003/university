from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import get_settings
from app.infrastructure.models import (
    User, Applicant, ApplicantResult, Student, Course, Program, Faculty, Department,
    Curriculum, Accreditation, Payment, Scholarship, FeeStructure, Grade, Transcript,
    Assessment, GradeAppeal, Hall, Room, Accommodation, MaintenanceRequest, Attendance,
    LibraryBook, Borrowing, Reservation, StaffMember, Leave, PerformanceAppraisal,
    HealthRecord, ClinicAppointment, Counseling, ResearchProposal, Grant, Publication,
    AlumniProfile, Mentorship, Donation, Notification, NotificationTemplate, Campaign,
    Document, DigitalSignature, AuditLog, Workflow, WorkflowInstance, ApprovalTask, Tenant,
    Subscription, Permission, Role, Inventory, Asset, MaintenanceSchedule,
    Timetable, Venue, TimeSlot
)

settings = get_settings()
client: AsyncIOMotorClient = None
db = None

async def init_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]

    await init_beanie(
        database=db,
        document_models=[
            User, Applicant, ApplicantResult, Student, Course, Program, Faculty, Department,
            Curriculum, Accreditation, Registration, AcademicCalendar, Payment, Scholarship, FeeStructure, Grade, Transcript,
            Assessment, GradeAppeal, Hall, Room, Accommodation, MaintenanceRequest, Attendance,
            LibraryBook, Borrowing, Reservation, StaffMember, Leave, PerformanceAppraisal,
            HealthRecord, ClinicAppointment, Counseling, ResearchProposal, Grant, Publication,
            AlumniProfile, Mentorship, Donation, Notification, NotificationTemplate, Campaign,
            Document, DigitalSignature, AuditLog, Workflow, WorkflowInstance, ApprovalTask, Tenant,
            Subscription, Permission, Role, Inventory, Asset, MaintenanceSchedule,
            Timetable, Venue, TimeSlot
        ]
    )
    print("✓ Connected to MongoDB & initialized Beanie models")

async def close_db():
    global client
    if client:
        client.close()
        print("✓ Closed MongoDB connection")

async def get_db():
    return db
