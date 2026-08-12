"""
Seed script for testing - creates a tenant, admin, admissions officer,
and a sample programme so you can test the full admissions flow.

Run: python -m scripts.seed_data
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from passlib.context import CryptContext

from app.config import get_settings
from app.infrastructure.models import (
    User, Tenant, Faculty, Department, Program,
    Applicant, Student, Course, Payment, Grade, Transcript, Hall, Room,
    LibraryBook, StaffMember, HealthRecord, ResearchProposal, AlumniProfile,
    Notification, Document, Workflow, Permission, Role, Attendance, Assessment,
    Accommodation, Inventory, Leave, Curriculum, Accreditation, Scholarship,
    FeeStructure, GradeAppeal, MaintenanceRequest, Borrowing, Reservation,
    PerformanceAppraisal, ClinicAppointment, Counseling, Grant, Publication,
    Mentorship, Donation, NotificationTemplate, Campaign, DigitalSignature,
    WorkflowInstance, ApprovalTask, Subscription, Asset, MaintenanceSchedule,
    Timetable, Venue, TimeSlot, ApplicantResult
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

async def seed():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]

    await init_beanie(database=db, document_models=[
        User, Tenant, Faculty, Department, Program, Applicant, Student, Course,
        Payment, Grade, Transcript, Hall, Room, LibraryBook, StaffMember,
        HealthRecord, ResearchProposal, AlumniProfile, Notification, Document,
        Workflow, Permission, Role, Attendance, Assessment, Accommodation,
        Inventory, Leave, Curriculum, Accreditation, Scholarship, FeeStructure,
        GradeAppeal, MaintenanceRequest, Borrowing, Reservation,
        PerformanceAppraisal, ClinicAppointment, Counseling, Grant, Publication,
        Mentorship, Donation, NotificationTemplate, Campaign, DigitalSignature,
        WorkflowInstance, ApprovalTask, Subscription, Asset, MaintenanceSchedule,
        Timetable, Venue, TimeSlot, ApplicantResult
    ])

    print("Seeding EUMP test data...\n")

    # 1. Create Tenant
    tenant = await Tenant.find_one({"subdomain": "test-university"})
    if not tenant:
        tenant = Tenant(
            name="Test University Ghana",
            subdomain="test-university",
            admin_email="admin@testuniversity.edu.gh",
            country="Ghana",
        )
        await tenant.insert()
        print(f"✓ Created tenant: {tenant.name} (id: {tenant.id})")
    else:
        print(f"✓ Tenant already exists: {tenant.name}")

    tenant_id = str(tenant.id)

    # 2. Create Admin User
    admin = await User.find_one({"email": "admin@test.com"})
    if not admin:
        admin = User(
            tenant_id=tenant_id,
            email="admin@test.com",
            first_name="System",
            last_name="Admin",
            password_hash=pwd_context.hash("Admin123!"),
            role="university_admin",
            is_active=True,
            is_verified=True,
        )
        await admin.insert()
        print(f"✓ Created admin: admin@test.com / Admin123!")

    # 3. Create Admissions Officer
    officer = await User.find_one({"email": "officer@test.com"})
    if not officer:
        officer = User(
            tenant_id=tenant_id,
            email="officer@test.com",
            first_name="Admissions",
            last_name="Officer",
            password_hash=pwd_context.hash("Officer123!"),
            role="admissions_officer",
            is_active=True,
            is_verified=True,
        )
        await officer.insert()
        print(f"✓ Created admissions officer: officer@test.com / Officer123!")

    # 4. Create Test Applicant User
    applicant_user = await User.find_one({"email": "applicant@test.com"})
    if not applicant_user:
        applicant_user = User(
            tenant_id=tenant_id,
            email="applicant@test.com",
            first_name="Kwame",
            last_name="Mensah",
            password_hash=pwd_context.hash("Applicant123!"),
            role="applicant",
            is_active=True,
            is_verified=True,
        )
        await applicant_user.insert()
        print(f"✓ Created applicant: applicant@test.com / Applicant123!")

    # 5. Create Faculty
    faculty = await Faculty.find_one({"tenant_id": tenant_id, "code": "FOS"})
    if not faculty:
        faculty = Faculty(
            tenant_id=tenant_id,
            name="Faculty of Science",
            code="FOS",
        )
        await faculty.insert()
        print(f"✓ Created faculty: {faculty.name}")

    # 6. Create Department
    department = await Department.find_one({"tenant_id": tenant_id, "code": "CS"})
    if not department:
        department = Department(
            tenant_id=tenant_id,
            faculty_id=str(faculty.id),
            name="Computer Science",
            code="CS",
        )
        await department.insert()
        print(f"✓ Created department: {department.name}")

    # 7. Create Programme
    programme = await Program.find_one({"tenant_id": tenant_id, "code": "BSC-CS"})
    if not programme:
        programme = Program(
            tenant_id=tenant_id,
            department_id=str(department.id),
            faculty_id=str(faculty.id),
            name="BSc Computer Science",
            code="BSC-CS",
            duration_years=4,
            required_subjects=["english", "mathematics", "science", "elective_1"],
            minimum_grades={
                "english": "C6",
                "mathematics": "C6",
                "science": "C6",
            },
            aggregate_threshold=24,
            accreditation_status="accredited",
            capacity_planned=100,
            capacity_reserved=5,
        )
        await programme.insert()
        print(f"✓ Created programme: {programme.name} (id: {programme.id})")

    print("\n" + "="*50)
    print("SEED COMPLETE - Test Credentials:")
    print("="*50)
    print(f"Admin:      admin@test.com / Admin123!")
    print(f"Officer:    officer@test.com / Officer123!")
    print(f"Applicant:  applicant@test.com / Applicant123!")
    print(f"\nTenant ID:    {tenant_id}")
    print(f"Programme ID: {programme.id}")
    print("="*50)

    client.close()

if __name__ == "__main__":
    asyncio.run(seed())
