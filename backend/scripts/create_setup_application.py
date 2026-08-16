#!/usr/bin/env python3
"""
Create a university setup application for the University of Machelli.
This is typically done by a super admin during initial onboarding.
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.application.onboarding.university_application_use_case import UniversityApplicationUseCase
from app.infrastructure.database.connection import init_db, get_db
from app.infrastructure.database.repositories.university_application_repository import UniversityApplicationRepository
from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.application.identifiers.identifier_service import IdentifierService


async def create_setup_application():
    """Create a university setup application for University of Machelli."""
    try:
        # Initialize database connection & Beanie models
        await init_db()
        db = await get_db()
        
        # Initialize repositories
        app_repo = UniversityApplicationRepository(db)
        tenant_repo = TenantRepository(db)
        identifier_service = IdentifierService(db)
        
        # Create use case
        use_case = UniversityApplicationUseCase(app_repo, tenant_repo, identifier_service)
        
        # Create the application
        application = await use_case.create_application(
            legal_name="University of Machelli",
            display_name="UOM",
            school_code="UOM",
            requested_by="super-admin",
            admin_first_name="System",
            admin_last_name="Admin",
            admin_email="admin@university.edu",
            country="Ghana",
            timezone="Africa/Accra",
            official_email="admin@university.edu",
            official_phone="+233 XXX XXX XXXX",
            description="Single-university enterprise system",
            academic_calendar_type="semester",
            currency="GHS",
        )
        
        print(f"✅ University setup application created successfully!")
        print(f"   Application ID: {application.university_application_id}")
        print(f"   Legal Name: {application.legal_name}")
        print(f"   Display Name: {application.display_name}")
        print(f"   Status: {application.status}")
        print(f"\n   Next: Log in as a university admin and access the Setup Wizard to configure all 23 sections.")
        
        return application
        
    except Exception as e:
        print(f"❌ Error creating setup application: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(create_setup_application())
    sys.exit(0 if result else 1)
