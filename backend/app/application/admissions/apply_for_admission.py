from typing import Optional, List
from datetime import datetime
from app.infrastructure.database.repositories.applicant_repository import ApplicantRepository
from app.infrastructure.models.applicant import Applicant, ApplicationStatusEnum
from app.infrastructure.database.repositories.payment_repository import PaymentRepository
from app.infrastructure.database.repositories.admission_cycle_repository import AdmissionCycleRepository
from datetime import timezone

class ApplyForAdmissionUseCase:
    def __init__(self, applicant_repo: ApplicantRepository):
        self.applicant_repo = applicant_repo

    async def execute(
        self,
        tenant_id: str,
        user_id: str,
        first_name: str,
        last_name: str,
        phone: str,
        date_of_birth: Optional[datetime] = None,
        gender: Optional[str] = None,
        address: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Applicant:
        existing = await self.applicant_repo.get_by_user_id(tenant_id, user_id)
        if existing:
            raise ValueError("Application already exists for this user")

        applicant_data = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "address": address,
            "region": region,
            "status": ApplicationStatusEnum.DRAFT,
        }

        return await self.applicant_repo.create(applicant_data)

    async def submit_application(
        self,
        applicant_id: str,
        index_number: str,
        exam_year: int,
        exam_type: str,
        programme_choices: List[dict]
    ) -> Applicant:
        # Check admission cycle closing date by resolving applicant's tenant
        try:
            applicant_doc = await self.applicant_repo.get_by_id(applicant_id)
            tenant_id = getattr(applicant_doc, "tenant_id", "default") if applicant_doc else "default"
            cycle_repo = AdmissionCycleRepository()
            cycle = await cycle_repo.get_active_cycle(tenant_id)
            if cycle and cycle.closing_date:
                now = datetime.utcnow().replace(tzinfo=timezone.utc)
                if now > cycle.closing_date.replace(tzinfo=timezone.utc):
                    raise ValueError("Admission cycle is closed. Applications are no longer accepted.")
        except Exception:
            # if we cannot determine cycle, proceed with submission and rely on downstream checks
            pass

        updated = await self.applicant_repo.update(applicant_id, {
            "index_number": index_number,
            "exam_year": exam_year,
            "exam_type": exam_type,
            "programme_choices": programme_choices,
            # If an application fee is configured and unpaid, mark as PAYMENT_PENDING
            "status": ApplicationStatusEnum.SUBMITTED,
            "updated_at": datetime.utcnow(),
        })

        if not updated:
            raise ValueError("Applicant not found")

        # check for application fee payment; if fee configured and no successful payment, set PAYMENT_PENDING
        try:
            from app.infrastructure.database.repositories.application_fee_repository import ApplicationFeeRepository
            app_fee_repo = ApplicationFeeRepository()
            fee = await app_fee_repo.get_for_tenant(updated.tenant_id)
            if fee and getattr(fee, "amount", 0) and float(fee.amount) > 0:
                payment_repo = PaymentRepository()
                payments = await payment_repo.model.find({"tenant_id": updated.tenant_id, "applicant_id": str(updated.id), "fee_type": "application", "status": "success"}).to_list(None)
                if not payments:
                    await self.applicant_repo.update(str(updated.id), {"status": ApplicationStatusEnum.PAYMENT_PENDING})
                    updated = await self.applicant_repo.get_by_id(applicant_id)
        except Exception:
            # Do not block submission on fee-check errors; default remains submitted
            pass

        return updated
