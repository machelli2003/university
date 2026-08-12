import pytest
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from app.application.admissions.process_admissions import ProcessAdmissionsPipelineUseCase
from app.application.admissions.publish_offers import PublishOffersUseCase
from app.application.student.create_student_record import CreateStudentRecordUseCase
from app.domain.admissions.eligibility_engine import EligibilityEngine
from app.domain.admissions.merit_ranking import MeritRankingEngine
from app.domain.admissions.allocation_engine import AllocationEngine


@dataclass
class FakeApplicant:
    id: str
    tenant_id: str
    user_id: str
    first_name: str
    last_name: str
    phone: str
    status: str
    date_of_birth: datetime | None = None
    gender: str | None = None
    programme_choices: list = field(default_factory=list)
    results: dict = field(default_factory=dict)
    aggregate: int = 0
    is_eligible: bool = False
    merit_score: float = 0.0
    merit_rank: int | None = None
    allocated_programme_id: str | None = None
    student_id: str | None = None
    application_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FakeProgram:
    id: str
    tenant_id: str
    name: str
    code: str
    required_subjects: list = field(default_factory=list)
    minimum_grades: dict = field(default_factory=dict)
    aggregate_threshold: int | None = None
    capacity_planned: int = 1
    capacity_reserved: int = 0


@dataclass
class FakeStudent:
    id: str
    tenant_id: str
    user_id: str
    applicant_id: str
    student_id: str
    first_name: str
    last_name: str
    date_of_birth: datetime | None = None
    gender: str | None = None
    phone: str | None = None
    email: str = ""
    programme_id: str | None = None
    faculty_id: str = ""
    department_id: str = ""
    entry_level: str = "100"
    entry_semester: str = "1"
    entry_year: int = field(default_factory=lambda: datetime.utcnow().year)
    status: str = "registered"


class FakeApplicantRepository:
    def __init__(self):
        self._items = {}

    async def create(self, data):
        applicant_id = str(uuid4())
        data.setdefault("application_date", datetime.utcnow())
        data["id"] = applicant_id
        applicant = FakeApplicant(**data)
        self._items[applicant_id] = applicant
        return applicant

    async def get_by_id(self, doc_id):
        return self._items.get(doc_id)

    async def get_by_user_id(self, tenant_id, user_id):
        return next(
            (a for a in self._items.values() if a.tenant_id == tenant_id and a.user_id == user_id),
            None,
        )

    async def get_by_status(self, tenant_id, status):
        return [a for a in self._items.values() if a.tenant_id == tenant_id and a.status == status]

    async def get_eligible_applicants(self, tenant_id):
        return [
            a
            for a in self._items.values()
            if a.tenant_id == tenant_id and a.is_eligible and a.status in ["eligible", "ranked"]
        ]

    async def update_eligibility(self, applicant_id, is_eligible, reason):
        applicant = await self.get_by_id(applicant_id)
        if not applicant:
            return None
        applicant.is_eligible = is_eligible
        return applicant

    async def update(self, doc_id, data):
        applicant = await self.get_by_id(doc_id)
        if not applicant:
            return None
        for key, value in data.items():
            setattr(applicant, key, value)
        return applicant

    async def get_by_programme_choice(self, tenant_id, programme_id):
        return [
            a
            for a in self._items.values()
            if a.tenant_id == tenant_id and any(c.get("programme_id") == programme_id for c in a.programme_choices)
        ]


class FakeProgramRepository:
    def __init__(self):
        self._items = {}

    async def create(self, data):
        program_id = str(uuid4())
        data["id"] = program_id
        program = FakeProgram(**data)
        self._items[program_id] = program
        return program

    async def get_by_id(self, program_id):
        return self._items.get(program_id)

    async def get_all(self, tenant_id):
        return [p for p in self._items.values() if p.tenant_id == tenant_id]


class FakeStudentRepository:
    def __init__(self):
        self._students = {}

    async def create(self, data):
        student_id = str(uuid4())
        data["id"] = student_id
        student = FakeStudent(**data)
        self._students[student_id] = student
        return student

    async def count(self, tenant_id=None):
        return len([s for s in self._students.values() if s.tenant_id == tenant_id])


@pytest.mark.asyncio
async def test_admissions_pipeline_and_student_record_creation():
    tenant_id = "default"

    applicant_repo = FakeApplicantRepository()
    program_repo = FakeProgramRepository()
    student_repo = FakeStudentRepository()

    program = await program_repo.create({
        "tenant_id": tenant_id,
        "name": "Computer Science",
        "code": "CS101",
        "required_subjects": ["english", "mathematics", "physics"],
        "minimum_grades": {"english": "C5", "mathematics": "C4", "physics": "C5"},
        "aggregate_threshold": 12,
        "capacity_planned": 1,
        "capacity_reserved": 0,
    })

    applicant = await applicant_repo.create({
        "tenant_id": tenant_id,
        "user_id": "user-123",
        "first_name": "Amina",
        "last_name": "Owusu",
        "phone": "233501234567",
        "status": "results_approved",
        "programme_choices": [{"programme_id": program.id, "choice_order": 1}],
        "results": {"english": "C4", "mathematics": "C4", "physics": "C4"},
        "aggregate": 12,
    })

    pipeline = ProcessAdmissionsPipelineUseCase(
        applicant_repo=applicant_repo,
        program_repo=program_repo,
        eligibility_engine=EligibilityEngine(),
        ranking_engine=MeritRankingEngine(),
        allocation_engine=AllocationEngine(),
    )

    summary = await pipeline.execute(tenant_id)

    assert summary["eligible"] == 1
    assert summary["ineligible"] == 0
    assert summary["ranked"] == 1
    assert summary["allocated"] == 1
    assert summary["offers_published"] == 1

    offered_applicants = await applicant_repo.get_by_status(tenant_id, "offered")
    assert len(offered_applicants) == 1
    offered_applicant = offered_applicants[0]
    assert offered_applicant.allocated_programme_id == program.id

    publish_use_case = PublishOffersUseCase(applicant_repo)
    accept_result = await publish_use_case.accept_offer(offered_applicant.id)
    assert accept_result["status"] == "accepted"

    assert offered_applicant.status == "accepted"

    create_student_use_case = CreateStudentRecordUseCase(applicant_repo, student_repo)
    student_record = await create_student_use_case.execute(offered_applicant.id, tenant_id)

    assert student_record["student_code"].startswith("UNIV/")
    assert student_record["student_id"]
    assert offered_applicant.student_id == student_record["student_id"]

    student_count = await student_repo.count(tenant_id=tenant_id)
    assert student_count == 1


@pytest.mark.asyncio
async def test_admissions_pipeline_marks_ineligible_applicant_without_offer():
    tenant_id = "default"

    applicant_repo = FakeApplicantRepository()
    program_repo = FakeProgramRepository()
    student_repo = FakeStudentRepository()

    program = await program_repo.create({
        "tenant_id": tenant_id,
        "name": "Civil Engineering",
        "code": "CE101",
        "required_subjects": ["english", "mathematics", "physics"],
        "minimum_grades": {"english": "C5", "mathematics": "C4", "physics": "C5"},
        "aggregate_threshold": 12,
        "capacity_planned": 1,
        "capacity_reserved": 0,
    })

    await applicant_repo.create({
        "tenant_id": tenant_id,
        "user_id": "user-456",
        "first_name": "Samuel",
        "last_name": "Mensah",
        "phone": "233501234568",
        "status": "results_approved",
        "programme_choices": [{"programme_id": program.id, "choice_order": 1}],
        "results": {"english": "C4", "mathematics": "C4", "physics": "D7"},
        "aggregate": 18,
    })

    pipeline = ProcessAdmissionsPipelineUseCase(
        applicant_repo=applicant_repo,
        program_repo=program_repo,
        eligibility_engine=EligibilityEngine(),
        ranking_engine=MeritRankingEngine(),
        allocation_engine=AllocationEngine(),
    )

    summary = await pipeline.execute(tenant_id)

    assert summary["eligible"] == 0
    assert summary["ineligible"] == 1
    assert summary["ranked"] == 0
    assert summary["allocated"] == 0
    assert summary["offers_published"] == 0

    offered_applicants = await applicant_repo.get_by_status(tenant_id, "offered")
    assert offered_applicants == []

    ineligible_applicants = await applicant_repo.get_by_status(tenant_id, "ineligible")
    assert len(ineligible_applicants) == 1
    assert ineligible_applicants[0].user_id == "user-456"


@pytest.mark.asyncio
async def test_admissions_pipeline_waitlists_applicant_when_capacity_is_exhausted():
    tenant_id = "default"

    applicant_repo = FakeApplicantRepository()
    program_repo = FakeProgramRepository()
    student_repo = FakeStudentRepository()

    program = await program_repo.create({
        "tenant_id": tenant_id,
        "name": "Mechanical Engineering",
        "code": "ME101",
        "required_subjects": ["english", "mathematics", "physics"],
        "minimum_grades": {"english": "C5", "mathematics": "C4", "physics": "C5"},
        "aggregate_threshold": 12,
        "capacity_planned": 1,
        "capacity_reserved": 0,
    })

    await applicant_repo.create({
        "tenant_id": tenant_id,
        "user_id": "user-789",
        "first_name": "Nana",
        "last_name": "Kwame",
        "phone": "233501234569",
        "status": "results_approved",
        "programme_choices": [{"programme_id": program.id, "choice_order": 1}],
        "results": {"english": "C4", "mathematics": "C4", "physics": "C4"},
        "aggregate": 10,
    })

    await applicant_repo.create({
        "tenant_id": tenant_id,
        "user_id": "user-890",
        "first_name": "Miriam",
        "last_name": "Agyemang",
        "phone": "233501234570",
        "status": "results_approved",
        "programme_choices": [{"programme_id": program.id, "choice_order": 1}],
        "results": {"english": "C4", "mathematics": "C4", "physics": "C4"},
        "aggregate": 12,
    })

    pipeline = ProcessAdmissionsPipelineUseCase(
        applicant_repo=applicant_repo,
        program_repo=program_repo,
        eligibility_engine=EligibilityEngine(),
        ranking_engine=MeritRankingEngine(),
        allocation_engine=AllocationEngine(),
    )

    summary = await pipeline.execute(tenant_id)

    assert summary["eligible"] == 2
    assert summary["ineligible"] == 0
    assert summary["ranked"] == 2
    assert summary["allocated"] == 1
    assert summary["waitlisted"] == 1
    assert summary["offers_published"] == 1

    offered_applicants = await applicant_repo.get_by_status(tenant_id, "offered")
    assert len(offered_applicants) == 1

    waitlisted_applicants = await applicant_repo.get_by_status(tenant_id, "waitlisted")
    assert len(waitlisted_applicants) == 1
    assert waitlisted_applicants[0].user_id == "user-890"
