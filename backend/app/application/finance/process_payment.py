from datetime import datetime
from typing import Optional
from app.infrastructure.database.repositories.payment_repository import PaymentRepository
from app.infrastructure.models.finance import PaymentStatusEnum
from app.infrastructure.external_services.s3_service import S3Service
from app.infrastructure.utils.receipt import generate_receipt_pdf


_s3 = S3Service()

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

        # fetch existing payment to read tenant/student info
        existing = await self.payment_repo.get_by_id(payment_id)

        updated = await self.payment_repo.update(payment_id, {
            "status": PaymentStatusEnum.SUCCESS,
            "paystack_reference": paystack_reference,
            "payment_date": datetime.utcnow(),
            "receipt_number": receipt_number,
        })

        # generate PDF receipt
        try:
            payment_info = {
                "receipt_number": receipt_number,
                "amount": float(getattr(updated, "amount", 0.0)),
                "payment_reference": getattr(updated, "payment_reference", ""),
                "payment_date": getattr(updated, "payment_date", datetime.utcnow()),
                "student_id": getattr(updated, "student_id", None),
            }

            pdf_bytes = generate_receipt_pdf(payment_info)

            # upload to S3 (or stub) and update payment record
            file_name = f"receipts/{getattr(updated, 'tenant_id', 'default')}/{receipt_number}.pdf"
            upload_result = await _s3.upload_file(pdf_bytes, file_name, content_type="application/pdf")
            if upload_result.get("uploaded") and upload_result.get("url"):
                await self.payment_repo.update(payment_id, {"receipt_pdf_url": upload_result.get("url")})
        except Exception:
            # don't fail the confirmation if receipt generation/upload fails
            pass

        # Update student fee clearance flags upon successful payment
        if updated and getattr(updated, "student_id", None):
            try:
                from app.infrastructure.database.repositories.student_repository import StudentRepository
                student_repo = StudentRepository()
                tenant_id = getattr(updated, "tenant_id", "default")
                student = await student_repo.get_by_student_id(tenant_id, updated.student_id)
                if not student:
                    # try finding student by user_id or id
                    all_students = await student_repo.get_all(tenant_id=tenant_id)
                    for s in all_students:
                        if s.student_id == updated.student_id or str(s.id) == updated.student_id:
                            student = s
                            break

                if student:
                    ft = (getattr(updated, "fee_type", "") or "").lower()
                    updates = {}
                    if ft in ["hostel", "hostel_fee", "hostel_fees", "accommodation"]:
                        updates["hostel_fee_paid"] = True
                    elif ft in ["tuition", "school_fees", "school_fee", "academic"]:
                        updates["school_fee_paid"] = True
                        new_bal = max(0.0, getattr(student, "fee_balance", 0.0) - float(updated.amount))
                        updates["fee_balance"] = new_bal
                    if updates:
                        await student_repo.update(str(student.id), updates)
            except Exception:
                pass

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
