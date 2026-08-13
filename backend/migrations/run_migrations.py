"""
Database Migration Runner

Orchestrates running database migrations in order.
Maintains a migration history to track which migrations have been applied.

Usage:
    python run_migrations.py up        # Apply all pending migrations
    python run_migrations.py down      # Rollback last migration
    python run_migrations.py status    # Show migration status
    python run_migrations.py <001|002|003> up     # Run specific migration
    python run_migrations.py <001|002|003> down   # Rollback specific migration
"""

import asyncio
import importlib
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from app.config import get_settings

settings = get_settings()

# List of all migrations in order
MIGRATIONS = [
    "001_create_new_collections",
    "002_update_applicant_statuses",
    "003_add_tenant_and_roles",
]


async def get_migration_collection(client):
    """Get or create the migration history collection."""
    db = client[settings.MONGODB_DB]
    
    if "migration_history" not in await db.list_collection_names():
        await db.create_collection("migration_history")
        await db.migration_history.create_index("name", unique=True)
    
    return db.migration_history


async def get_applied_migrations(client):
    """Get list of applied migrations."""
    collection = await get_migration_collection(client)
    docs = await collection.find().to_list(None)
    return [doc["name"] for doc in docs]


async def record_migration(client, name, direction):
    """Record a migration as applied or rolled back."""
    collection = await get_migration_collection(client)
    
    if direction == "up":
        await collection.insert_one({
            "name": name,
            "applied_at": datetime.utcnow(),
            "direction": "up"
        })
    elif direction == "down":
        await collection.delete_one({"name": name})


async def run_migration(migration_name, direction):
    """Run a single migration."""
    try:
        module = importlib.import_module(f"migrations.{migration_name}")
        
        print(f"\n{'='*60}")
        print(f"Running: {migration_name} ({direction.upper()})")
        print(f"{'='*60}")
        
        if direction == "up":
            await module.up()
        elif direction == "down":
            await module.down()
        
        # Record in migration history
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        try:
            await record_migration(client, migration_name, direction)
        finally:
            client.close()
        
        print(f"\n✅ {migration_name} completed ({direction})")
        return True
        
    except Exception as e:
        print(f"\n❌ Error running {migration_name}: {e}")
        return False


async def show_status():
    """Show migration status."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    try:
        applied = await get_applied_migrations(client)
        
        print("\n" + "="*60)
        print("MIGRATION STATUS")
        print("="*60)
        
        for i, migration in enumerate(MIGRATIONS, 1):
            status = "✅ APPLIED" if migration in applied else "⏳ PENDING"
            print(f"{i}. {migration} ... {status}")
        
        print("\n" + "="*60)
        print(f"Applied: {len(applied)}/{len(MIGRATIONS)}")
        print("="*60 + "\n")
        
    finally:
        client.close()


async def up():
    """Apply all pending migrations."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    try:
        applied = await get_applied_migrations(client)
    finally:
        client.close()
    
    pending = [m for m in MIGRATIONS if m not in applied]
    
    if not pending:
        print("\n✅ All migrations already applied")
        return True
    
    print(f"\n🔄 Applying {len(pending)} pending migration(s)...")
    
    for migration in pending:
        success = await run_migration(migration, "up")
        if not success:
            print("\n❌ Migration failed. Stopping.")
            return False
    
    print("\n" + "="*60)
    print("✅ All migrations applied successfully")
    print("="*60 + "\n")
    return True


async def down():
    """Rollback last migration."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    try:
        applied = await get_applied_migrations(client)
    finally:
        client.close()
    
    if not applied:
        print("\n✅ No migrations to rollback")
        return True
    
    # Rollback the last applied migration
    last_migration = applied[-1]
    print(f"\n🔄 Rolling back: {last_migration}")
    
    success = await run_migration(last_migration, "down")
    
    if success:
        print("\n✅ Rollback completed")
    
    return success


async def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        await show_status()
        return
    
    command = sys.argv[1]
    
    if command == "status":
        await show_status()
    elif command == "up":
        await up()
    elif command == "down":
        await down()
    elif len(sys.argv) >= 3 and sys.argv[2] in ["up", "down"]:
        # Run specific migration
        migration_name = command
        direction = sys.argv[2]
        await run_migration(migration_name, direction)
        await show_status()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    asyncio.run(main())
