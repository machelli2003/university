import pytest
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from app.application.admissions.verify_waec_results import SubmitManualResultsUseCase, ApproveResultsUseCase
from app.domain.admissions.waec_service import ManualResultsEntryService
from app.infrastructure.models.applicant import ApplicationStatusEnum

@dataclass
class FakeApplicant:
    id: str
    tenant_id: str
    user_id: str
    first_name: str
    last_name: str
    phone: str
    status: str
    results: dict = field(default_factory=dict)
    aggregate: int | None = None
    eligibility_reason: str | None = None
    updated_at: datetime = field(default_factory=datetime.utcnow)

class FakeApplicantRepository:
    def __init__(self):
        self._items = {}

    async def get_by_id(self, doc_id):
        return self._items.get(doc_id)

    async def update(self, doc_id, data):
        applicant = await self.get_by_id(doc_id)
        if not applicant:
            return None
        for key, value in data.items():
            setattr(applicant, key, value)
        applicant.updated_at = datetime.utcnow()
        return applicant

    async def create(self, data):
        applicant_id = str(uuid4())
        data["id"] = applicant_id
        applicant = FakeApplicant(**data)
        self._items[applicant_id] = applicant
        return applicant

class FakeApplicantResultRepository:
    def __init__(self):
        self._items = {}

    async def create(self, data):
        result_id = str(uuid4())
        self._items[result_id] = {"id": result_id, **data}
        return self._items[result_id]

    async def get_by_applicant(self, applicant_id):
        return [item for item in self._items.values() if item["applicant_id"] == applicant_id]

    async def update(self, doc_id, data):
        item = self._items.get(doc_id)
        if not item:
            return None
        item.update(data)
        return item

@pytest.mark.asyncio
async def test_manual_results_submission_and_approval_flow():
    tenant_id = "default"
    applicant_id = str(uuid4())

    applicant_repo = FakeApplicantRepository()
    result_repo = FakeApplicantResultRepository()
    manual_service = ManualResultsEntryService()

    applicant = await applicant_repo.create({
        "tenant_id": tenant_id,
        "user_id": "user-123",
        "first_name": "Ama",
        "last_name": "Opoku",
        "phone": "233501234567",
        "status": "submitted",
    })

    submit_use_case = SubmitManualResultsUseCase(applicant_repo, result_repo, manual_service)
    updated_applicant = await submit_use_case.execute(
        tenant_id=tenant_id,
        applicant_id=applicant.id,
        results={
            "english": "C4",
            "mathematics": "C5",
            "science": "C5",
            "social_studies": "C5",
        },
        uploaded_by="user-123",
    )

    assert updated_applicant.status == "results_uploaded"
    assert updated_applicant.results["english"] == "C4"
    assert len(result_repo._items) == 4

@pytest.mark.asyncio
async def test_approve_and_reject_manual_results_flow():
    tenant_id = "default"

    applicant_repo = FakeApplicantRepository()
    result_repo = FakeApplicantResultRepository()

    applicant = await applicant_repo.create({
        "tenant_id": tenant_id,
        "user_id": "user-456",
        "first_name": "Yaa",
        "last_name": "Boateng",
        "phone": "233501234568",
        "status": "results_uploaded",
        "results": {"english": "B2", "mathematics": "C4", "science": "C5", "social_studies": "C5"},
    })

    await result_repo.create({
        "tenant_id": tenant_id,
        "applicant_id": applicant.id,
        "subject": "english",
        "grade": "B2",
        "uploaded_by": "user-456",
        "uploaded_at": datetime.utcnow(),
    })
    await result_repo.create({
        "tenant_id": tenant_id,
        "applicant_id": applicant.id,
        "subject": "mathematics",
        "grade": "C4",
        "uploaded_by": "user-456",
        "uploaded_at": datetime.utcnow(),
    })

    approve_use_case = ApproveResultsUseCase(applicant_repo, result_repo)
    updated = await approve_use_case.execute(applicant.id, approved_by="admin-1")

    assert updated.status == ApplicationStatusEnum.RESULTS_APPROVED
    assert updated.aggregate is not None

    rejected = await approve_use_case.reject(applicant.id, rejected_by="admin-1", reason="Incomplete documentation")
    assert rejected.status == "submitted"
    assert rejected.eligibility_reason is not None
    assert "Results rejected" in rejected.eligibility_reason
