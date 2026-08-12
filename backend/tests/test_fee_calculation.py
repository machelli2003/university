import asyncio
import pytest
from app.application.finance.fee_calculation import FeeCalculatorUseCase

class MockFeeRepo:
    def __init__(self, fees):
        self._fees = fees
    async def get_current_structure(self, tenant_id, programme_id=None):
        class S: pass
        if self._fees is None:
            return None
        s = S()
        s.fees = self._fees
        return s

class MockPaymentRepo:
    def __init__(self, payments):
        self._payments = payments
    async def get_by_student(self, tenant_id, student_id):
        return self._payments

class MockScholarshipRepo:
    def __init__(self, scholarships):
        self._sch = scholarships
    async def get_by_student(self, tenant_id, student_id):
        return self._sch

class MockStudentRepo:
    def __init__(self, student):
        self._s = student
    async def get_by_student_id(self, tenant_id, student_id):
        return self._s

@pytest.mark.asyncio
async def test_percentage_scholarship_applied():
    fees = {"tuition": 1000, "lab": 200}
    payments = []
    scholarships = [{"amount": 0, "percentage": 50, "is_active": True}]
    student = type("S", (), {"programme_id": "prog1"})()

    fee_repo = MockFeeRepo(fees)
    payment_repo = MockPaymentRepo(payments)
    sch_repo = MockScholarshipRepo(scholarships)
    student_repo = MockStudentRepo(student)

    calc = FeeCalculatorUseCase(payment_repo=payment_repo, scholarship_repo=sch_repo, fee_repo=fee_repo, student_repo=student_repo)
    res = await calc.calculate_balance("t1", "s1")

    assert res["total_due"] == 1200
    assert res["total_scholarships"] == pytest.approx(600.0)
    assert res["balance"] == pytest.approx(600.0)

@pytest.mark.asyncio
async def test_programme_fallback_to_default():
    # programme-specific missing, fallback to default
    prog_fees = None
    default_fees = {"tuition": 800}
    payments = [{"amount": 100}, {"amount": 200}]
    scholarships = [{"amount": 50, "is_active": True}]
    student = type("S", (), {"programme_id": "progX"})()

    fee_repo = MockFeeRepoNone(prog_fees=prog_fees, default_fees=default_fees) if False else None
    # We'll implement a small adaptor inline:
    class FeeRepoAdapter:
        def __init__(self, prog, default):
            self.prog = prog
            self.default = default
        async def get_current_structure(self, tenant_id, programme_id=None):
            class S: pass
            if programme_id == "progX":
                return None
            s = S(); s.fees = self.default; return s
    fee_repo = FeeRepoAdapter(None, default_fees)

    payment_repo = MockPaymentRepo(payments)
    sch_repo = MockScholarshipRepo(scholarships)
    student_repo = MockStudentRepo(student)

    calc = FeeCalculatorUseCase(payment_repo=payment_repo, scholarship_repo=sch_repo, fee_repo=fee_repo, student_repo=student_repo)
    res = await calc.calculate_balance("t1", "s1")

    assert res["total_due"] == 800
    assert res["total_paid"] == 300
    assert res["total_scholarships"] == 50
    assert res["balance"] == 450
