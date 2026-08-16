"""
Seed script for library data: create a librarian, a sample book and a sample student

Run: python -m scripts.seed_library
"""

import os
import sys

# Ensure backend directory is on Python path regardless of execution location
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from passlib.context import CryptContext

from app.config import get_settings
from app.infrastructure.models import User, Tenant, LibraryBook, Student

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

async def seed():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]

    await init_beanie(database=db, document_models=[User, Tenant, LibraryBook, Student])

    tenant = await Tenant.find_one({"subdomain": "test-university"})
    if not tenant:
        tenant = Tenant(name="Test University Ghana", subdomain="test-university", admin_email="admin@testuniversity.edu.gh", country="Ghana")
        await tenant.insert()

    tenant_id = str(tenant.id)

    librarian = await User.find_one({"email": "librarian@test.com"})
    if not librarian:
        librarian = User(
            tenant_id=tenant_id,
            email="librarian@test.com",
            first_name="Lib",
            last_name="Rarian",
            password_hash=pwd_context.hash("Librarian123!"),
            role="librarian",
            is_active=True,
            is_verified=True,
        )
        await librarian.insert()

    book = await LibraryBook.find_one({"tenant_id": tenant_id, "title": "Introduction to Programming"})
    if not book:
        book = LibraryBook(tenant_id=tenant_id, title="Introduction to Programming", isbn="978-0-00-000000-0", author="Jane Doe", publisher="UniPub", category="Computer Science", total_copies=3, available_copies=3)
        await book.insert()

    student_user = await User.find_one({"email": "studentlib@test.com"})
    if not student_user:
        student_user = User(
            tenant_id=tenant_id,
            email="studentlib@test.com",
            first_name="Lib",
            last_name="Student",
            password_hash=pwd_context.hash("Student123!"),
            role="student",
            is_active=True,
            is_verified=True,
        )
        await student_user.insert()

    student = await Student.find_one({"email": "studentlib@test.com"})
    if not student:
        student = Student(
            tenant_id=tenant_id,
            user_id=str(student_user.id),
            email="studentlib@test.com",
            first_name="Lib",
            last_name="Student",
            student_id="STULIB001",
            phone="0241000002",
            programme_id="prog1",
            faculty_id="fac1",
            department_id="dep1",
            entry_level="100",
            entry_semester="1",
            entry_year=2024,
        )
        await student.insert()

    print("Seeded library data: book, librarian, student")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed())
