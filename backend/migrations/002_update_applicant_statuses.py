"""
Migration 002: Add New Application Status States to Applicants

Updates the applicant status field to support the new comprehensive workflow states:
- AWAITING_RESULTS
- RESULTS_UPLOADED
- RESULTS_APPROVED
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()


async def up():
    """Apply the migration."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    
    try:
        print("🔄 Running Migration 002: Add New Application Status States")
        
        if "applicants" not in await db.list_collection_names():
            print("ℹ Applicants collection doesn't exist yet (OK for new installation)")
            return
        
        # Add migration for existing applicant records if needed
        # Map old statuses to new ones where applicable
        status_mappings = {
            "submitted": "submitted",  # No change
            "awaiting_results": "awaiting_results",  # New state
            "results_uploaded": "results_uploaded",  # New state
            "results_approved": "results_approved",  # New state
        }
        
        # Update any existing documents that need status normalization
        result = await db.applicants.update_many(
            {"status": {"$exists": False}},
            {"$set": {"status": "draft"}}
        )
        
        if result.modified_count > 0:
            print(f"✓ Normalized {result.modified_count} applicants with missing status")
        
        # Ensure all required enum-related fields exist
        result = await db.applicants.update_many(
            {},
            {
                "$setOnInsert": {
                    "verification_status": "pending_verification",
                    "updated_at": None
                }
            }
        )
        
        print("✓ Updated applicant documents with new status fields")
        print("✅ Migration 002 completed successfully")
        
    finally:
        client.close()


async def down():
    """Rollback the migration."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    
    try:
        print("🔄 Rolling back Migration 002")
        
        if "applicants" not in await db.list_collection_names():
            print("ℹ Applicants collection doesn't exist (nothing to rollback)")
            return
        
        # Map new statuses back to old compatible ones
        # This is a best-effort rollback
        status_reverse_map = {
            "awaiting_results": "submitted",
            "results_uploaded": "submitted",
            "results_approved": "submitted",
        }
        
        for new_status, old_status in status_reverse_map.items():
            await db.applicants.update_many(
                {"status": new_status},
                {"$set": {"status": old_status}}
            )
        
        print("✓ Reverted applicant statuses")
        print("✅ Migration 002 rolled back")
        
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
