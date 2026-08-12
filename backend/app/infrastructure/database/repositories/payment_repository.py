from app.infrastructure.models.finance import Payment, Scholarship, FeeStructure
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional
from datetime import datetime, timedelta

class PaymentRepository(BaseRepository[Payment]):
    def __init__(self):
        super().__init__(Payment)

    async def get_by_student(self, tenant_id: str, student_id: str) -> List[Payment]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "student_id": student_id
        }).to_list(None)

    async def get_successful_payments(self, tenant_id: str) -> List[Payment]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "status": "success"
        }).to_list(None)

    async def get_pending_payments(self, tenant_id: str) -> List[Payment]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "status": "pending"
        }).to_list(None)

    async def get_by_paystack_ref(self, paystack_ref: str) -> Optional[Payment]:
        return await self.model.find_one({
            "paystack_reference": paystack_ref
        })

    async def get_revenue_for_period(self, tenant_id: str, start_date: datetime, end_date: datetime) -> float:
        payments = await self.model.find({
            "tenant_id": tenant_id,
            "status": "success",
            "payment_date": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)
        return sum(p.amount for p in payments)

    async def get_outstanding_fees(self, tenant_id: str, student_id: str) -> List[Payment]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "student_id": student_id,
            "status": {"$in": ["pending", "failed"]}
        }).to_list(None)

class ScholarshipRepository(BaseRepository[Scholarship]):
    def __init__(self):
        super().__init__(Scholarship)

    async def get_by_student(self, tenant_id: str, student_id: str) -> List[Scholarship]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "student_id": student_id,
            "is_active": True
        }).to_list(None)

    async def get_active_scholarships(self, tenant_id: str) -> List[Scholarship]:
        now = datetime.utcnow()
        return await self.model.find({
            "tenant_id": tenant_id,
            "is_active": True,
            "start_date": {"$lte": now},
            "$or": [
                {"end_date": None},
                {"end_date": {"$gte": now}}
            ]
        }).to_list(None)

class FeeStructureRepository(BaseRepository[FeeStructure]):
    def __init__(self):
        super().__init__(FeeStructure)

    async def get_current_structure(self, tenant_id: str, programme_id: Optional[str] = None) -> Optional[FeeStructure]:
        current_year = str(datetime.utcnow().year)
        query = {
            "tenant_id": tenant_id,
            "academic_year": current_year
        }
        if programme_id:
            query["programme_id"] = programme_id
        else:
            query["programme_id"] = None

        return await self.model.find_one(query)
