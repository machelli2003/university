"""
Seed script for hostel data: create a hall, a room and a sample student

Run: python -m scripts.seed_accommodation
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from passlib.context import CryptContext

from app.config import get_settings
from app.infrastructure.models import User, Tenant, Hall, Room, Student

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

async def seed():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]

    await init_beanie(database=db, document_models=[User, Tenant, Hall, Room, Student])

    tenant = await Tenant.find_one({"subdomain": "test-university"})
    if not tenant:
        tenant = Tenant(name="Test University Ghana", subdomain="test-university", admin_email="admin@testuniversity.edu.gh", country="Ghana")
        await tenant.insert()

    tenant_id = str(tenant.id)

    admin = await User.find_one({"email": "hosteladmin@test.com"})
    if not admin:
        admin = User(
            tenant_id=tenant_id,
            email="hosteladmin@test.com",
            first_name="Hostel",
            last_name="Admin",
            password_hash=pwd_context.hash("Hostel123!"),
            role="hostel_administrator",
            is_active=True,
            is_verified=True,
        )
        await admin.insert()

    hall = await Hall.find_one({"tenant_id": tenant_id, "name": "Alpha Hall"})
    if not hall:
        hall = Hall(tenant_id=tenant_id, name="Alpha Hall", capacity=100)
        await hall.insert()

    room = await Room.find_one({"tenant_id": tenant_id, "room_number": "101"})
    if not room:
        room = Room(tenant_id=tenant_id, hall_id=str(hall.id), room_number="101", room_type="single", capacity=1, occupied=0, students=[])
        await room.insert()

    student = await Student.find_one({"email": "student1@test.com"})
    if not student:
        student = Student(tenant_id=tenant_id, email="student1@test.com", first_name="Test", last_name="Student", student_id="STU1001")
        await student.insert()

    print("Seeded hostel data: hall, room, admin, student")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed())
