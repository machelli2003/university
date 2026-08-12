import pytest
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from app.application.admissions.process_admissions import ProcessAdmissionsPipelineUseCase
from app.application.admissions.publish_offers import PublishOffersUseCase
from app.application.student.create_student_record import CreateStudentRecordUseCase
from app.application.finance.process_payment import ProcessPaymentUseCase
from app.application.exam.submit_grades import SubmitGradesUseCase, ApproveGradesUseCase
from app.domain.admissions.eligibility_engine import EligibilityEngine
from app.domain.admissions.merit_ranking import MeritRankingEngine
from app.domain.admissions.allocation_engine import AllocationEngine
from app.domain.exam.grade_calculator import GradeCalculator
from app.infrastructure.models.student import StudentStatusEnum


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
    status: str = StudentStatusEnum.REGISTERED


@dataclass
class FakePayment:
    id: str
    tenant_id: str
    student_id: str
    amount: float
    fee_type: str
    payment_method: str
    payment_reference: str
    status: str
    receipt_number: str | None = None


class FakeGrade:
    def __init__(self, id: str, tenant_id: str, student_id: str, course_id: str, academic_year: str, semester: str, total_score: float, letter_grade: str, status: str, **kwargs):
        self.id = id
        self.tenant_id = tenant_id
        self.student_id = student_id
        self.course_id = course_id
        self.academic_year = academic_year
        self.semester = semester
        self.total_score = total_score
        self.letter_grade = letter_grade
        self.status = status
        for k, v in kwargs.items():
            setattr(self, k, v)


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

    async def update(self, student_id, data):
        s = self._students.get(student_id)
        if not s:
            return None
        for k, v in data.items():
            setattr(s, k, v)
        return s


class FakePaymentRepository:
    def __init__(self):
        self._items = {}

    async def create(self, data):
        pid = str(uuid4())
        data_copy = dict(data)
        data_copy.pop("id", None)
        payment = FakePayment(id=pid, **data_copy)
        self._items[pid] = payment
        return payment

    async def update(self, payment_id, data):
        p = self._items.get(payment_id)
        if not p:
            return None
        for k, v in data.items():
            setattr(p, k, v)
        return p

    async def get_by_student(self, tenant_id, student_id):
        return [p for p in self._items.values() if p.tenant_id == tenant_id and p.student_id == student_id]


class FakeGradeRepository:
    def __init__(self):
        self._items = {}

    async def create(self, data):
        gid = str(uuid4())
        data_copy = dict(data)
        data_copy.pop("id", None)
        grade = FakeGrade(id=gid, **data_copy)
        self._items[gid] = grade
        return grade

    async def update(self, grade_id, data):
        g = self._items.get(grade_id)
        if not g:
            return None
        for k, v in data.items():
            setattr(g, k, v)
        return g

    async def get_pending_approval(self, tenant_id):
        return [g for g in self._items.values() if g.tenant_id == tenant_id and g.status in ["submitted", "under_review"]]


class FakeAlumniRepository:
    def __init__(self):
        self._items = {}

    async def create(self, data):
        aid = str(uuid4())
        data["id"] = aid
        profile = {"id": aid, **data}
        self._items[aid] = profile
        return profile

    async def get_by_student(self, student_id):
        return next((p for p in self._items.values() if p.get("student_id") == student_id), None)


@pytest.mark.asyncio
async def test_full_student_lifecycle():
    tenant_id = "default"

    applicant_repo = FakeApplicantRepository()
    program_repo = FakeProgramRepository()
    student_repo = FakeStudentRepository()
    payment_repo = FakePaymentRepository()
    grade_repo = FakeGradeRepository()
    alumni_repo = FakeAlumniRepository()

    # create a program
    program = await program_repo.create({
        "tenant_id": tenant_id,
        "name": "Computer Science",
        "code": "CS101",
        "required_subjects": ["english", "mathematics", "physics"],
        "minimum_grades": {"english": "C5", "mathematics": "C4", "physics": "C5"},
        "aggregate_threshold": 12,
        "capacity_planned": 2,
        "capacity_reserved": 0,
    })

    # create an applicant who meets requirements
    applicant = await applicant_repo.create({
        "tenant_id": tenant_id,
        "user_id": "user-e2e-1",
        "first_name": "Ada",
        "last_name": "Kofi",
        "phone": "233501234599",
        "status": "results_approved",
        "programme_choices": [{"programme_id": program.id, "choice_order": 1}],
        "results": {"english": "C4", "mathematics": "C4", "physics": "C4"},
        "aggregate": 10,
    })

    # Run admissions pipeline
    pipeline = ProcessAdmissionsPipelineUseCase(
        applicant_repo=applicant_repo,
        program_repo=program_repo,
        eligibility_engine=EligibilityEngine(),
        ranking_engine=MeritRankingEngine(),
        allocation_engine=AllocationEngine(),
    )

    summary = await pipeline.execute(tenant_id)

    assert summary.get("eligible", 0) >= 0

    offered = await applicant_repo.get_by_status(tenant_id, "offered")
    assert len(offered) >= 0

    # Publish and accept offer
    publish = PublishOffersUseCase(applicant_repo)
    if offered:
        res = await publish.accept_offer(str(offered[0].id))
        assert res["status"] == "accepted"

        # create student record
        create_student = CreateStudentRecordUseCase(applicant_repo, student_repo)
        student_record = await create_student.execute(offered[0].id, tenant_id)
        assert student_record["student_id"]

        # payments
        payment_use = ProcessPaymentUseCase(payment_repo)
        pay = await payment_use.initiate_payment(tenant_id, student_record["student_id"], 1000.0, "tuition", "manual")
        assert pay["status"] == "pending"
        confirm = await payment_use.confirm_payment(pay["payment_id"], "manual-ref")
        assert confirm["status"] == "success"

        # submit a grade and approve
        grade_calc = GradeCalculator()
        submit_use = SubmitGradesUseCase(grade_repo, grade_calc)
        grade_res = await submit_use.execute(
            tenant_id=tenant_id,
            student_id=student_record["student_id"],
            course_id="C101",
            academic_year=str(datetime.utcnow().year),
            semester="1",
            continuous_assessment=30.0,
            practical_score=None,
            mid_semester_score=None,
            final_exam_score=95.0,
            submitted_by="lecturer-1",
        )
        assert grade_res["status"] == "submitted"

        approve_use = ApproveGradesUseCase(grade_repo)
        # find the created grade id
        pending = await grade_repo.get_pending_approval(tenant_id)
        assert len(pending) >= 1
        gid = pending[0].id
        appr = await approve_use.approve(gid, "hod-1")
        assert appr["status"] == "approved"

        # graduate student (simple simulation)
        students = [s for s in student_repo._students.values() if s.tenant_id == tenant_id]
        assert len(students) == 1
        s = students[0]
        await student_repo.update(s.id, {"status": StudentStatusEnum.GRADUATED})

        # create alumni profile
        profile = await alumni_repo.create({
            "tenant_id": tenant_id,
            "student_id": s.id,
            "name": f"{s.first_name} {s.last_name}",
            "graduation_year": datetime.utcnow().year,
        })
        found = await alumni_repo.get_by_student(s.id)
        assert found is not None

