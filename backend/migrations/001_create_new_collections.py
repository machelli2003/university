"""
Migration 001: Create New Collections for Multi-Tenant University Platform

This migration creates the new collections and schema required for the transformation:
- university_applications: Stores onboarding applications for new universities
- identifier_sequences: Tracks ID sequence counters per tenant
- Indexes for tenant_id on existing collections
"""

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()


async def up():
    """Apply the migration."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    
    try:
        print("🔄 Running Migration 001: Create New Collections")
        
        # 1. Create university_applications collection with schema validation
        if "university_applications" not in await db.list_collection_names():
            await db.create_collection("university_applications")
            await db.university_applications.create_index("university_application_id", unique=True)
            await db.university_applications.create_index("school_code", unique=True)
            await db.university_applications.create_index("status")
            await db.university_applications.create_index("tenant_id")
            await db.university_applications.create_index("created_at")
            print("✓ Created university_applications collection and indexes")
        
        # 2. Create identifier_sequences collection
        if "identifier_sequences" not in await db.list_collection_names():
            await db.create_collection("identifier_sequences")
            await db.identifier_sequences.create_index([("tenant_id", 1), ("identifier_type", 1)], unique=True)
            print("✓ Created identifier_sequences collection and indexes")
        
        # 3. Create staff_assignments collection
        if "staff_assignments" not in await db.list_collection_names():
            await db.create_collection("staff_assignments")
            await db.staff_assignments.create_index([("tenant_id", 1), ("staff_id", 1)])
            await db.staff_assignments.create_index([("tenant_id", 1), ("assignment_type", 1)])
            await db.staff_assignments.create_index([("assigned_resource_id", 1)])
            print("✓ Created staff_assignments collection and indexes")
        
        # 4. Add tenant_id index to existing collections
        collections_to_index = [
            "users", "applicants", "students", "staff_members",
            "faculties", "departments", "programs", "courses",
            "payments", "grades", "attendance", "accommodation",
            "library_books", "borrowings", "audit_logs"
        ]
        
        for collection_name in collections_to_index:
            if collection_name in await db.list_collection_names():
                try:
                    await db[collection_name].create_index("tenant_id")
                    print(f"✓ Added tenant_id index to {collection_name}")
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"⚠ Error indexing {collection_name}: {e}")
        
        print("✅ Migration 001 completed successfully")
        
    finally:
        client.close()


async def down():
    """Rollback the migration."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    
    try:
        print("🔄 Rolling back Migration 001")
        
        # Drop new collections
        for collection in ["university_applications", "identifier_sequences", "staff_assignments"]:
            if collection in await db.list_collection_names():
                await db[collection].drop()
                print(f"✓ Dropped {collection} collection")
        
        # Remove tenant_id indexes from existing collections
        collections_to_deindex = [
            "users", "applicants", "students", "staff_members",
            "faculties", "departments", "programs", "courses",
            "payments", "grades", "attendance", "accommodation",
            "library_books", "borrowings", "audit_logs"
        ]
        
        for collection_name in collections_to_deindex:
            if collection_name in await db.list_collection_names():
                try:
                    await db[collection_name].drop_index("tenant_id_1")
                    print(f"✓ Removed tenant_id index from {collection_name}")
                except Exception as e:
                    if "index not found" not in str(e):
                        print(f"⚠ Error removing index from {collection_name}: {e}")
        
        print("✅ Migration 001 rolled back")
        
    finally:
        client.close()


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "up"
    if action == "up":
        asyncio.run(up())
    elif action == "down":
        asyncio.run(down())
    else:
        print(f"Unknown action: {action}")
