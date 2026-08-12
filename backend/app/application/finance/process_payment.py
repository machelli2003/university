from datetime import datetime
from typing import Optional
from app.infrastructure.database.repositories.payment_repository import PaymentRepository
from app.infrastructure.models.finance import PaymentStatusEnum

class ProcessPaymentUseCase:
    def __init__(self, payment_repo: PaymentRepository):
        self.payment_repo = payment_repo

    async def initiate_payment(
        self,
        tenant_id: str,
        student_id: str,
        amount: float,
        fee_type: str,
        payment_method: str,
    ) -> dict:
        import uuid
        payment_reference = f"PAY-{uuid.uuid4().hex[:12].upper()}"

        payment_data = {
            "tenant_id": tenant_id,
            "student_id": student_id,
            "amount": amount,
            "fee_type": fee_type,
            "payment_method": payment_method,
            "payment_reference": payment_reference,
            "status": PaymentStatusEnum.PENDING,
        }

        payment = await self.payment_repo.create(payment_data)

        return {
            "payment_id": str(payment.id),
            "payment_reference": payment_reference,
            "amount": amount,
            "status": "pending",
        }

    async def confirm_payment(
        self,
        payment_id: str,
        paystack_reference: str
    ) -> dict:
        import uuid
        receipt_number = f"RCP-{uuid.uuid4().hex[:10].upper()}"

        updated = await self.payment_repo.update(payment_id, {
            "status": PaymentStatusEnum.SUCCESS,
            "paystack_reference": paystack_reference,
            "payment_date": datetime.utcnow(),
            "receipt_number": receipt_number,
        })

        return {
            "payment_id": payment_id,
            "status": "success",
            "receipt_number": receipt_number,
        }

    async def fail_payment(self, payment_id: str, reason: str = None) -> dict:
        await self.payment_repo.update(payment_id, {
            "status": PaymentStatusEnum.FAILED,
        })

        return {"payment_id": payment_id, "status": "failed", "reason": reason}

    async def get_student_payment_history(self, tenant_id: str, student_id: str) -> list:
        return await self.payment_repo.get_by_student(tenant_id, student_id)
