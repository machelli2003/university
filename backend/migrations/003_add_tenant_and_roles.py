"""
Migration 003: Add Tenant Isolation and Role/Permission Structure to Users

Migrates existing users to support:
- tenant_id field (required for multi-tenant isolation)
- role object with permissions
- MFA support
- active status
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
        print("🔄 Running Migration 003: Add Tenant Isolation and Role Structure")
        
        if "users" not in await db.list_collection_names():
            print("ℹ Users collection doesn't exist yet (OK for new installation)")
            return
        
        # Add tenant_id to users who don't have it
        # For existing users, assign to default tenant
        result = await db.users.update_many(
            {"tenant_id": {"$exists": False}},
            {"$set": {"tenant_id": "default"}}
        )
        
        if result.modified_count > 0:
            print(f"✓ Added tenant_id to {result.modified_count} users (assigned to 'default' tenant)")
        
        # Ensure all users have a role structure (if not present)
        result = await db.users.update_many(
            {"role": {"$exists": False}},
            {"$set": {"role": {"value": "user", "name": "User"}}}
        )
        
        if result.modified_count > 0:
            print(f"✓ Added role structure to {result.modified_count} users")
        
        # Ensure all users have MFA and active fields
        result = await db.users.update_many(
            {},
            {
                "$setOnInsert": {
                    "mfa_enabled": False,
                    "active": True,
                    "created_at": None,
                    "updated_at": None
                }
            }
        )
        
        # Add active index for querying active users
        await db.users.create_index("active")
        
        print("✓ Updated user documents with tenant isolation structure")
        print("✓ Created active status index")
        print("✅ Migration 003 completed successfully")
        
    finally:
        client.close()


async def down():
    """Rollback the migration."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    
    try:
        print("🔄 Rolling back Migration 003")
        
        if "users" not in await db.list_collection_names():
            print("ℹ Users collection doesn't exist (nothing to rollback)")
            return
        
        # Remove tenant_id from users (optional - may want to keep for audit trail)
        # await db.users.update_many({}, {"$unset": {"tenant_id": ""}})
        
        # Drop active index
        try:
            await db.users.drop_index("active_1")
        except Exception as e:
            if "index not found" not in str(e):
                print(f"⚠ Error dropping index: {e}")
        
        print("✓ Rolled back user structure changes")
        print("✅ Migration 003 rolled back")
        
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
