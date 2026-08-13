from app.infrastructure.models.financial_clearance import FinancialClearance, ClearanceStatusEnum
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional
from datetime import datetime

class FinancialClearanceRepository(BaseRepository[FinancialClearance]):
    """Repository for managing financial clearance records"""
    
    def __init__(self):
        super().__init__(FinancialClearance)

    async def get_by_student_and_year(
        self,
        tenant_id: str,
        student_id: str,
        academic_year: str
    ) -> Optional[FinancialClearance]:
        """Get clearance record for student in specific academic year"""
        return await self.model.find_one({
            "tenant_id": tenant_id,
            "student_id": student_id,
            "academic_year": academic_year
        })

    async def get_by_student(
        self,
        tenant_id: str,
        student_id: str
    ) -> List[FinancialClearance]:
        """Get all clearance records for a student"""
        return await self.model.find({
            "tenant_id": tenant_id,
            "student_id": student_id
        }).sort("academic_year", -1).to_list(None)

    async def get_cleared_students(
        self,
        tenant_id: str,
        academic_year: str
    ) -> List[FinancialClearance]:
        """Get all cleared students for an academic year"""
        return await self.model.find({
            "tenant_id": tenant_id,
            "academic_year": academic_year,
            "status": ClearanceStatusEnum.CLEARED
        }).to_list(None)

    async def get_students_with_outstanding_balance(
        self,
        tenant_id: str,
        academic_year: str
    ) -> List[FinancialClearance]:
        """Get students with outstanding balance"""
        return await self.model.find({
            "tenant_id": tenant_id,
            "academic_year": academic_year,
            "status": ClearanceStatusEnum.OUTSTANDING,
            "outstanding_balance": {"$gt": 0}
        }).to_list(None)

    async def get_by_status(
        self,
        tenant_id: str,
        status: ClearanceStatusEnum,
        academic_year: Optional[str] = None
    ) -> List[FinancialClearance]:
        """Get clearance records by status"""
        query = {
            "tenant_id": tenant_id,
            "status": status
        }
        if academic_year:
            query["academic_year"] = academic_year
        return await self.model.find(query).to_list(None)

    async def get_payment_plan_approvals(
        self,
        tenant_id: str,
        academic_year: str
    ) -> List[FinancialClearance]:
        """Get students with approved payment plans"""
        return await self.model.find({
            "tenant_id": tenant_id,
            "academic_year": academic_year,
            "has_payment_plan": True,
            "payment_plan_approved_at": {"$ne": None}
        }).to_list(None)

    async def get_overdue_payment_plans(
        self,
        tenant_id: str
    ) -> List[FinancialClearance]:
        """Get students with overdue payment plans"""
        now = datetime.utcnow()
        return await self.model.find({
            "tenant_id": tenant_id,
            "has_payment_plan": True,
            "payment_plan_deadline": {"$lt": now},
            "status": {"$in": [ClearanceStatusEnum.OUTSTANDING, ClearanceStatusEnum.HOLD]}
        }).to_list(None)
