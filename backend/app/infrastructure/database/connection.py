import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import get_settings
from app.infrastructure.database.index_manager import IndexManager
from app.infrastructure.models import (
    User, Applicant, ApplicantResult, Student, Course, Program, Faculty, Department,
    Curriculum, Accreditation, Registration, AcademicCalendar, Payment, Scholarship, FeeStructure, Grade, Transcript,
    Assessment, GradeAppeal, Hall, Room, Accommodation, MaintenanceRequest, Attendance,
    LibraryBook, Borrowing, Reservation, StaffMember, Leave, PerformanceAppraisal,
    HealthRecord, ClinicAppointment, Counseling, ResearchProposal, Grant, Publication,
    AlumniProfile, Mentorship, Donation, Notification, NotificationTemplate, Campaign,
    Document, DigitalSignature, AuditLog, Workflow, WorkflowInstance, ApprovalTask, Tenant,
    Subscription, UniversityApplication, IdentifierSequence, Permission, Role, Inventory, Asset, MaintenanceSchedule,
    Timetable, Venue, TimeSlot, StaffAssignment
)

settings = get_settings()
client: AsyncIOMotorClient = None
db = None

import asyncio
import dns.resolver

# Ensure robust DNS SRV record resolution for MongoDB Atlas
try:
    resolver = dns.resolver.Resolver(configure=True)
    resolver.lifetime = 5.0
    resolver.timeout = 5.0
    dns.resolver.default_resolver = resolver
except Exception:
    pass

async def init_db():
    global client, db
    
    # Configure AsyncIOMotorClient with resilient connection parameters for MongoDB Atlas on Windows
    client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=20000,
        tlsCAFile=certifi.where(),
        tlsAllowInvalidCertificates=True,
    )
    db = client[settings.MONGODB_DB]

    # Retry loop to handle transient SSL handshake / network resets
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            await init_beanie(
                database=db,
                allow_index_dropping=True,
                document_models=[
                    User, Applicant, ApplicantResult, Student, Course, Program, Faculty, Department,
                    Curriculum, Accreditation, Registration, AcademicCalendar, Payment, Scholarship, FeeStructure, Grade, Transcript,
                    Assessment, GradeAppeal, Hall, Room, Accommodation, MaintenanceRequest, Attendance,
                    LibraryBook, Borrowing, Reservation, StaffMember, Leave, PerformanceAppraisal,
                    HealthRecord, ClinicAppointment, Counseling, ResearchProposal, Grant, Publication,
                    AlumniProfile, Mentorship, Donation, Notification, NotificationTemplate, Campaign,
                    Document, DigitalSignature, AuditLog, Workflow, WorkflowInstance, ApprovalTask, Tenant,
                    Subscription, UniversityApplication, IdentifierSequence, Permission, Role, Inventory, Asset, MaintenanceSchedule,
                    Timetable, Venue, TimeSlot, StaffAssignment
                ]
            )
            break
        except Exception as e:
            if attempt == max_retries:
                raise
            print(f"[WARNING] MongoDB connection attempt {attempt}/{max_retries} failed ({str(e)}). Retrying in 2s...")
            await asyncio.sleep(2)

    print("[OK] Connected to MongoDB & initialized Beanie models")
    
    # Initialize database indexes in background to prevent blocking startup
    asyncio.create_task(IndexManager.setup_indexes(db))

async def close_db():
    global client
    if client:
        client.close()
        print("[OK] Closed MongoDB connection")

async def get_db():
    return db
