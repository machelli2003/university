import pytest
from datetime import datetime
from fastapi import HTTPException
from app.presentation.api.v1.onboarding.routes import (
    create_university_application,
    get_university_application,
    update_university_application,
    submit_university_application_for_review,
    approve_university_application,
    activate_university_application,
    reject_university_application,
    update_application_setup_section,
)
from app.application.onboarding.university_application_use_case import UniversityApplicationUseCase
from app.presentation.api.v1.onboarding.schemas import (
    CreateUniversityApplicationRequest,
    UpdateUniversityApplicationRequest,
    UpdateSetupSectionRequest,
    RejectUniversityApplicationRequest,
)
from app.infrastructure.database.repositories.university_application_repository import IdentifierSequenceRepository

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

    async def get_by_id(self, application_id):
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

def test_create_request_allows_blank_optional_email_fields():
    request = CreateUniversityApplicationRequest(
        legal_name="Test University",
        display_name="Test Uni",
        school_code="TST",
        admin_first_name="Jane",
        admin_last_name="Doe",
        admin_email="jane.doe@example.com",
        official_email="",
        website="",
    )

    assert request.official_email is None
    assert request.website is None


@pytest.mark.asyncio
async def test_submit_for_review_sends_super_admin_notification(monkeypatch):
    user = MockUser(role="super_admin")
    app_repo = MockUniversityApplicationRepo()
    app = MockApplication(
        id="app-1",
        university_application_id="UAPP-2026-000002",
        requested_by="u1",
        status="draft",
        setup_sections={
            "university_information": True,
            "id_configuration": True,
            "academic_years": True,
            "faculties": True,
            "departments": True,
            "programmes": True,
            "courses": True,
            "admission_cycle": True,
            "admission_requirements": True,
            "application_form": True,
            "application_fee": True,
            "staff": True,
            "student_id_configuration": True,
            "staff_id_configuration": True,
            "applicant_id_configuration": True,
            "grading": True,
            "graduation": True,
            "finance": True,
            "module_enablement": True,
            "admission_categories": False,
            "role_permission": False,
            "hostel": False,
            "library": False,
        },
    )
    app_repo.applications[app.university_application_id] = app
    app_repo.applications[app.id] = app
    tenant_repo = MockTenantRepo()
    identifier_service = MockIdentifierService()
    notifications = []

    async def fake_notify(**kwargs):
        notifications.append(kwargs)

    monkeypatch.setattr(
        "app.application.onboarding.university_application_use_case.notify_super_admins_for_application",
        fake_notify,
    )

    use_case = UniversityApplicationUseCase(app_repo, tenant_repo, identifier_service)
    await use_case.submit_for_review(app.university_application_id)

    assert notifications
    assert notifications[0]["target_url"] == "/admin/super-admin-review"


@pytest.mark.asyncio
async def test_identifier_sequence_upsert_avoids_conflicting_updated_at_fields():
    class GuardedCollection:
        async def find_one_and_update(self, filter_query, update, upsert=True, return_document=None):
            if "$setOnInsert" in update and "$set" in update:
                set_on_insert = update["$setOnInsert"]
                set_update = update["$set"]
                if "updated_at" in set_on_insert and "updated_at" in set_update:
                    raise AssertionError("Conflicting updated_at updates in the same Mongo operation")
            return {"sequence": 1}

    repo = IdentifierSequenceRepository()
    repo.model.get_motor_collection = lambda: GuardedCollection()

    sequence = await repo.next_sequence(None, "university_application", 2026)

    assert sequence == 1


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


@pytest.mark.asyncio
async def test_get_university_application_allows_university_admin_same_tenant():
    current_user = MockUser(id_="admin-1", role="university_admin", tenant_id="tenant-123")
    app_repo = MockUniversityApplicationRepo()
    app = MockApplication(
        id="app-1",
        university_application_id="UAPP-2026-000002",
        tenant_id="tenant-123",
        requested_by="other-admin",
        legal_name="Tenant University",
        school_code="TNT",
        status="draft",
        setup_sections={
            "university_information": True,
            "id_configuration": True,
            "academic_years": True,
            "faculties": True,
            "departments": True,
            "programmes": True,
            "courses": True,
            "admission_cycle": True,
            "admission_categories": True,
            "admission_requirements": True,
            "application_form": True,
            "application_fee": True,
            "staff": True,
            "role_permission": True,
            "student_id_configuration": True,
            "staff_id_configuration": True,
            "applicant_id_configuration": True,
            "grading": True,
            "graduation": True,
        },
    )
    app_repo.applications[app.university_application_id] = app
    application_id = app.university_application_id
    user = current_user
    tenant_repo = MockTenantRepo()
    identifier_service = MockIdentifierService()
    audit_repo = MockAuditRepo()

    result = await get_university_application(
        application_id="UAPP-2026-000002",
        current_user=current_user,
        application_repo=app_repo,
    )

    assert result.university_application_id == "UAPP-2026-000002"

    section_request = UpdateSetupSectionRequest(completed=True)
    updated = await update_application_setup_section(
        application_id,
        "university_information",
        section_request,
        current_user=user,
        application_repo=app_repo,
        tenant_repo=tenant_repo,
        identifier_service=identifier_service,
        audit_repo=audit_repo,
    )
    assert updated.setup_sections["university_information"] is True

    # All mandatory sections are already complete for this regression scenario.
    submitted = await submit_university_application_for_review(
        application_id,
        current_user=user,
        application_repo=app_repo,
        tenant_repo=tenant_repo,
        identifier_service=identifier_service,
        audit_repo=audit_repo,
    )
    assert submitted.status == "awaiting_super_admin_approval"

    approved = await approve_university_application(
        application_id,
        current_user=user,
        application_repo=app_repo,
        tenant_repo=tenant_repo,
        identifier_service=identifier_service,
        audit_repo=audit_repo,
    )
    assert approved.status == "provisioning"

    activated = await activate_university_application(
        application_id,
        current_user=user,
        application_repo=app_repo,
        tenant_repo=tenant_repo,
        identifier_service=identifier_service,
        audit_repo=audit_repo,
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
