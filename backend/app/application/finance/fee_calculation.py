from datetime import datetime
from typing import Any, Optional
from app.infrastructure.database.repositories.payment_repository import PaymentRepository, ScholarshipRepository, FeeStructureRepository
from app.infrastructure.database.repositories.student_repository import StudentRepository


def _sum_fees_obj(fees: dict) -> float:
    total = 0.0
    if not fees:
        return 0.0
    for v in fees.values():
        if isinstance(v, (int, float)):
            total += float(v)
        elif isinstance(v, dict):
            total += _sum_fees_obj(v)
    return total


def _get_field(source: Any, field: str, default: Any = None) -> Any:
    if isinstance(source, dict):
        return source.get(field, default)
    return getattr(source, field, default)


class FeeCalculatorUseCase:
    def __init__(self,
                 payment_repo: Optional[PaymentRepository] = None,
                 scholarship_repo: Optional[ScholarshipRepository] = None,
                 fee_repo: Optional[FeeStructureRepository] = None,
                 student_repo: Optional[StudentRepository] = None):
        self.payment_repo = payment_repo or PaymentRepository()
        self.scholarship_repo = scholarship_repo or ScholarshipRepository()
        self.fee_repo = fee_repo or FeeStructureRepository()
        self.student_repo = student_repo or StudentRepository()

    async def calculate_balance(self, tenant_id: str, student_id: str, academic_year: Optional[str] = None) -> dict:
        if not academic_year:
            academic_year = str(datetime.utcnow().year)

        student = await self.student_repo.get_by_student_id(tenant_id, student_id)
        programme_id = getattr(student, 'programme_id', None) if student else None

        # Try programme-specific structure first, then fallback to default (None)
        fee_structure = None
        if programme_id:
            fee_structure = await self.fee_repo.get_current_structure(tenant_id, programme_id)
        if not fee_structure:
            fee_structure = await self.fee_repo.get_current_structure(tenant_id, None)

        total_due = _sum_fees_obj(fee_structure.fees) if fee_structure else 0.0

        payments = await self.payment_repo.get_by_student(tenant_id, student_id)
        total_paid = 0.0
        for p in payments:
            status = _get_field(p, 'status', None)
            if status is None or str(status).lower() == "success":
                total_paid += float(_get_field(p, 'amount', 0.0))

        scholarships = await self.scholarship_repo.get_by_student(tenant_id, student_id)
        total_scholarships = 0.0
        for s in scholarships:
            if not _get_field(s, 'is_active', True):
                continue
            percentage = _get_field(s, 'percentage', None)
            if percentage is not None:
                try:
                    pct = float(percentage)
                    total_scholarships += (pct / 100.0) * total_due
                except Exception:
                    total_scholarships += float(_get_field(s, 'amount', 0.0))
            else:
                total_scholarships += float(_get_field(s, 'amount', 0.0))

        balance = total_due - total_paid - total_scholarships
        if balance < 0:
            balance = 0.0

        return {
            "total_due": total_due,
            "total_paid": total_paid,
            "total_scholarships": total_scholarships,
            "balance": balance,
        }
