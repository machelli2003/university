# Database Migration Guide

## Overview

This directory contains all database migrations required to transform the existing university management system to the new multi-tenant SaaS architecture.

The migration system uses MongoDB and tracks applied migrations to ensure idempotency and safe rollback.

## Migration Tracking

Migrations are tracked in the `migration_history` collection. Each applied migration is recorded with:
- `name`: Migration filename
- `applied_at`: UTC timestamp
- `direction`: "up" (applied) or "down" (rolled back)

## Available Migrations

### Migration 001: Create New Collections
**File**: `001_create_new_collections.py`

Creates three new collections required for the multi-tenant platform:

1. **university_applications**
   - Stores onboarding applications from prospective universities
   - Fields: university_application_id, school_code, status, tenant_id, setup_sections, etc.
   - Indexes: university_application_id (unique), school_code (unique), status, tenant_id, created_at

2. **identifier_sequences**
   - Tracks ID generation sequences per tenant
   - Fields: tenant_id, identifier_type, current_sequence
   - Index: (tenant_id, identifier_type) unique compound index

3. **staff_assignments**
   - Tracks staff assignments to departments, courses, and other resources
   - Fields: tenant_id, staff_id, assignment_type, assigned_resource_id
   - Indexes: (tenant_id, staff_id), (tenant_id, assignment_type), assigned_resource_id

Also adds `tenant_id` indexes to all existing collections for efficient tenant-scoped queries.

### Migration 002: Add New Application Status States
**File**: `002_update_applicant_statuses.py`

Updates the applicant workflow to support new result verification states:

- `AWAITING_RESULTS`: After submission, waiting for applicant to upload WASSCE results
- `RESULTS_UPLOADED`: Applicant has submitted results, awaiting officer verification
- `RESULTS_APPROVED`: Officer has verified and approved the results

**Data Preservation**: Existing applicant records are updated to maintain compatibility. No data is lost.

### Migration 003: Add Tenant Isolation and Role Structure
**File**: `003_add_tenant_and_roles.py`

Adds tenant isolation and role-based access control structure to users:

1. **tenant_id field**
   - Required for all users
   - Existing users assigned to "default" tenant
   - Enables multi-tenant isolation at the database level

2. **Role and Permission Structure**
   - Adds `role` object with value and name
   - Prepares user model for permission-based authorization
   - Existing users get default role if not present

3. **MFA Support**
   - Adds `mfa_enabled` boolean field (default: false)

4. **Active Status**
   - Adds `active` boolean field (default: true)
   - Enables soft-delete and deactivation workflows

**Indexes**: Creates index on `active` field for efficient active user queries.

## Running Migrations

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure MongoDB is running and accessible
# Set MONGODB_URL in your .env file
```

### Viewing Migration Status

```bash
python -m migrations.run_migrations status
```

Output:
```
============================================================
MIGRATION STATUS
============================================================
1. 001_create_new_collections ... ✅ APPLIED
2. 002_update_applicant_statuses ... ✅ APPLIED
3. 003_add_tenant_and_roles ... ⏳ PENDING

============================================================
Applied: 2/3
============================================================
```

### Applying All Pending Migrations

```bash
python -m migrations.run_migrations up
```

This will:
1. Check which migrations have been applied
2. Run all pending migrations in order
3. Record each migration in `migration_history`
4. Stop on first failure (safe fail-fast behavior)

### Applying a Specific Migration

```bash
python -m migrations.run_migrations 001_create_new_collections up
```

### Rolling Back the Last Migration

```bash
python -m migrations.run_migrations down
```

This will:
1. Identify the last applied migration
2. Execute the `down()` function to rollback changes
3. Remove it from migration history

### Rolling Back a Specific Migration

```bash
python -m migrations.run_migrations 003_add_tenant_and_roles down
```

## Migration Process for Production

### Step 1: Backup Database

```bash
# Using MongoDB tools
mongodump --uri="mongodb://..." --out=./backup_$(date +%Y%m%d_%H%M%S)
```

### Step 2: Test Migrations in Development/Staging

```bash
# Test all migrations
python -m migrations.run_migrations status
python -m migrations.run_migrations up

# Verify the application works
# Run test suite
python -m pytest tests/ -v
```

### Step 3: Apply Migrations to Production

```bash
# One-time: Create backup
mongodump --uri="mongodb://..." --out=./backup_pre_migration

# Apply migrations
python -m migrations.run_migrations up

# Verify application
python run.py  # Start app and verify functionality
```

### Step 4: Verify Results

After running migrations:

```bash
# Check migration history
mongo mongodb://... --eval "db.migration_history.find().pretty()"

# Verify new collections exist
mongo mongodb://... --eval "db.getCollectionNames().pretty()"

# Verify indexes were created
mongo mongodb://... --eval "db.university_applications.getIndexes().pretty()"
```

## Rollback Procedure

If a migration causes issues:

### Step 1: Stop Application

```bash
# Stop the running application
# Do not accept new requests
```

### Step 2: Rollback Last Migration

```bash
python -m migrations.run_migrations down
```

### Step 3: Restore from Backup (if needed)

```bash
# If rollback script was insufficient
mongorestore --uri="mongodb://..." ./backup_pre_migration
```

### Step 4: Restart Application

```bash
python run.py
```

## Writing New Migrations

When adding new migrations:

### 1. Create Migration File

Create `migrations/NNN_description_of_change.py`:

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()

async def up():
    """Apply the migration."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    
    try:
        print("🔄 Running Migration NNN")
        
        # Your migration logic here
        # Use db to access collections
        
        print("✅ Migration NNN completed")
    finally:
        client.close()

async def down():
    """Rollback the migration."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    
    try:
        print("🔄 Rolling back Migration NNN")
        
        # Your rollback logic here
        # This should undo all changes from up()
        
        print("✅ Migration NNN rolled back")
    finally:
        client.close()

if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "up"
    if action == "up":
        asyncio.run(up())
    elif action == "down":
        asyncio.run(down())
```

### 2. Add to MIGRATIONS List

Edit `run_migrations.py` and add your migration to the `MIGRATIONS` list:

```python
MIGRATIONS = [
    "001_create_new_collections",
    "002_update_applicant_statuses",
    "003_add_tenant_and_roles",
    "NNN_description_of_change",  # Add here
]
```

### 3. Test the Migration

```bash
# Test in development
python -m migrations.run_migrations status
python -m migrations.run_migrations NNN_description_of_change up
python -m migrations.run_migrations NNN_description_of_change down
```

### 4. Commit and Deploy

```bash
git add migrations/NNN_description_of_change.py
git commit -m "Add migration: NNN_description_of_change"
git push
```

## Best Practices

1. **Write both `up()` and `down()` functions** - Always make migrations reversible
2. **Use descriptive names** - Include migration number and description
3. **Add progress indicators** - Print clear status messages
4. **Handle missing collections** - Check if collections exist before operating on them
5. **Index thoughtfully** - Don't create redundant indexes
6. **Test thoroughly** - Test migrations multiple times before production
7. **Document changes** - Add comments explaining what each migration does
8. **Minimize downtime** - Design migrations that can run while app is running
9. **Batch large updates** - For very large collections, consider batching updates
10. **Monitor performance** - Large migrations can impact database performance

## Troubleshooting

### Migration fails with "connection refused"

```
Error: connection refused
```

**Solution**: Ensure MongoDB is running and MONGODB_URL is correct

```bash
# Check MongoDB is running
mongosh --uri="mongodb://..."

# Verify .env has correct MONGODB_URL
cat .env | grep MONGODB_URL
```

### Migration says it's already applied but rollback not working

```
Error: index not found
```

**Solution**: Some databases may have partial application of migrations. Manually check:

```bash
# Connect to database
mongosh mongodb://...

# Check migration history
db.migration_history.find().pretty()

# Check what actually exists
db.university_applications.exists()
db.university_applications.getIndexes()
```

### Want to re-run a migration that's already applied

```bash
# First rollback
python -m migrations.run_migrations NNN_name down

# Then apply again
python -m migrations.run_migrations up
```

## References

- [Beanie Documentation](https://roman-right.github.io/beanie/)
- [Motor (Async MongoDB Driver)](https://motor.readthedocs.io/)
- [MongoDB Indexes](https://docs.mongodb.com/manual/indexes/)
- [Migration Best Practices](https://en.wikipedia.org/wiki/Schema_migration)
