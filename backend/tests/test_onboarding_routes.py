import pytest
from datetime import datetime
from fastapi import HTTPException
from app.presentation.api.v1.onboarding.routes import (
    create_university_application,
    update_university_application,
    submit_university_application_for_review,
    approve_university_application,
    activate_university_application,
    reject_university_application,
    update_application_setup_section,
)
from app.presentation.api.v1.onboarding.schemas import (
    CreateUniversityApplicationRequest,
    UpdateUniversityApplicationRequest,
    UpdateSetupSectionRequest,
    RejectUniversityApplicationRequest,
)

class MockUser:
    def __init__(self, tenant_id=None, id_="u1", role="super_admin"):
        self.tenant_id = tenant_id
        self.id = id_
        self.role = type("R", (), {"value": role})()

class MockApplication:
    def __init__(self, **data):
        self.__dict__.update(data)
        self.id = data.get("id", "app1")
        self.university_application_id = data.get("university_application_id", "UAPP-2026-000001")
        self.status = data.get("status", "draft")
        self.tenant_id = data.get("tenant_id", None)
        self.legal_name = data.get("legal_name", "Test University")
        self.display_name = data.get("display_name", "Test Uni")
        self.school_code = data.get("school_code", "TST")
        self.description = data.get("description", "Test university description")
        self.official_email = data.get("official_email", None)
        self.admin_email = data.get("admin_email", "admin@test.com")
        self.official_phone = data.get("official_phone", None)
        self.country = data.get("country", "Ghana")
        self.timezone = data.get("timezone", "Africa/Accra")
        self.setup_sections = data.get("setup_sections", {
            "university_information": False,
            "id_configuration": False,
            "academic_years": False,
            "faculties": False,
            "departments": False,
            "programmes": False,
            "courses": False,
            "admission_cycle": False,
            "admission_categories": False,
            "admission_requirements": False,
            "application_form": False,
            "application_fee": False,
            "staff": False,
            "role_permission": False,
            "student_id_configuration": False,
            "staff_id_configuration": False,
            "applicant_id_configuration": False,
            "grading": False,
            "graduation": False,
        })
        self.created_at = data.get("created_at", datetime.utcnow())
        self.updated_at = data.get("updated_at", datetime.utcnow())

class MockUniversityApplicationRepo:
    def __init__(self):
        self.applications = {}
        self.updated = []

    async def create(self, data):
        application = MockApplication(**data)
        self.applications[application.university_application_id] = application
        self.applications[application.id] = application
        return application

    async def get_by_application_id(self, application_id):
        return self.applications.get(application_id)

    async def get_all(self):
        # Return unique application objects when both keys exist
        unique_apps = {id(app): app for app in self.applications.values()}
        return list(unique_apps.values())

    async def update(self, app_id, data):
        app = next((a for a in self.applications.values() if a.id == app_id), None)
        if not app:
            return None
        app.__dict__.update(data)
        self.updated.append((app_id, data))
        return app

    async def list_by_status(self, status):
        return [a for a in self.applications.values() if a.status == status]

    async def update_section_status(self, application_id, section, completed):
        app = self.applications.get(application_id)
        if not app:
            app = next((a for a in self.applications.values() if a.id == application_id), None)
        if not app:
            return None
        app.setup_sections[section] = completed
        return app

class MockTenantRepo:
    def __init__(self, exists=False):
        self.exists = exists
        self.created = False

    async def get_by_subdomain(self, subdomain):
        return None if not self.exists else MockApplication(id="t1", subdomain=subdomain)

    async def create(self, data):
        self.created = True
        return MockApplication(id="t1", **data)

    async def get_by_id(self, tenant_id):
        return MockApplication(id=tenant_id, school_code="TST")

    async def update(self, tenant_id, data):
        return MockApplication(id=tenant_id, **data)

class MockIdentifierService:
    async def generate_university_application_id(self, year=None):
        return "UAPP-2026-000001"

class MockAuditRepo:
    async def create(self, data):
        return None

@pytest.mark.asyncio
async def test_create_submit_approve_activate_workflow():
    user = MockUser(role="super_admin")
    app_repo = MockUniversityApplicationRepo()
    tenant_repo = MockTenantRepo()
    identifier_service = MockIdentifierService()

    request = CreateUniversityApplicationRequest(
        legal_name="Test University",
        display_name="Test Uni",
        school_code="TST",
        admin_first_name="Jane",
        admin_last_name="Doe",
        admin_email="jane.doe@example.com",
    )

    class MockAuditRepo:
        async def create(self, data):
            return None

    application = await create_university_application(
        request,
        current_user=user,
        application_repo=app_repo,
        tenant_repo=tenant_repo,
        identifier_service=identifier_service,
        audit_repo=MockAuditRepo(),
    )
    assert application.university_application_id == "UAPP-2026-000001"
    application_id = application.university_application_id

    section_request = UpdateSetupSectionRequest(completed=True)
    updated = await update_application_setup_section(
        application_id,
        "university_information",
        section_request,
        current_user=user,
        application_repo=app_repo,
        tenant_repo=tenant_repo,
        identifier_service=identifier_service,
        audit_repo=MockAuditRepo(),
    )
    assert updated.setup_sections["university_information"] is True

    # Mark all sections complete via direct repo update
    fetched_app = await app_repo.get_by_application_id(application_id)
    if fetched_app:
        for section in fetched_app.setup_sections:
            fetched_app.setup_sections[section] = True
    submitted = await submit_university_application_for_review(
        application_id,
        current_user=user,
        application_repo=app_repo,
        tenant_repo=tenant_repo,
        identifier_service=identifier_service,
        audit_repo=MockAuditRepo(),
    )
    assert submitted.status == "awaiting_super_admin_approval"

    approved = await approve_university_application(
        application_id,
        current_user=user,
        application_repo=app_repo,
        tenant_repo=tenant_repo,
        identifier_service=identifier_service,
        audit_repo=MockAuditRepo(),
    )
    assert approved.status == "provisioning"

    activated = await activate_university_application(
        application_id,
        current_user=user,
        application_repo=app_repo,
        tenant_repo=tenant_repo,
        identifier_service=identifier_service,
        audit_repo=MockAuditRepo(),
    )
    assert activated.status == "active"

@pytest.mark.asyncio
async def test_reject_application():
    user = MockUser(role="super_admin")
    app_repo = MockUniversityApplicationRepo()
    tenant_repo = MockTenantRepo()
    identifier_service = MockIdentifierService()

    application = MockApplication(
        id="app2",
        university_application_id="UAPP-2026-000002",
        legal_name="Test University",
        school_code="TST",
        status="awaiting_super_admin_approval",
        setup_sections={"university_information": True},
    )
    app_repo.applications[application.university_application_id] = application

    reject_request = RejectUniversityApplicationRequest(reason="Incomplete documents")
    rejected = await reject_university_application(
        application.university_application_id,
        reject_request,
        current_user=user,
        application_repo=app_repo,
        tenant_repo=tenant_repo,
        identifier_service=identifier_service,
        audit_repo=MockAuditRepo(),
    )
    assert rejected.status == "rejected"
    assert rejected.review_notes == "Incomplete documents"
