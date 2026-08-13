from typing import Tuple, Optional, Dict
from datetime import datetime
from app.infrastructure.database.repositories.payment_repository import (
    PaymentRepository, ScholarshipRepository, FeeStructureRepository
)
from app.infrastructure.database.repositories.financial_clearance_repository import (
    FinancialClearanceRepository
)
from app.infrastructure.models.financial_clearance import ClearanceStatusEnum
from app.infrastructure.models.student import Student

class FinancialClearanceService:
    """Comprehensive financial clearance management for students"""

    def __init__(
        self,
        payment_repo: PaymentRepository = None,
        scholarship_repo: ScholarshipRepository = None,
        fee_structure_repo: FeeStructureRepository = None,
        clearance_repo: FinancialClearanceRepository = None,
    ):
        self.payment_repo = payment_repo or PaymentRepository()
        self.scholarship_repo = scholarship_repo or ScholarshipRepository()
        self.fee_structure_repo = fee_structure_repo or FeeStructureRepository()
        self.clearance_repo = clearance_repo or FinancialClearanceRepository()

    async def check_clearance(
        self,
        tenant_id: str,
        student_id: str,
        academic_year: str
    ) -> Tuple[bool, str, Dict]:
        """
        Check if student is financially cleared.
        
        Returns:
            (is_cleared: bool, status_message: str, clearance_details: dict)
        """
        # Get or create clearance record
        clearance = await self.clearance_repo.get_by_student_and_year(
            tenant_id, student_id, academic_year
        )
        
        if not clearance:
            # First time checking - calculate fresh balance
            balance_info = await self.calculate_balance(
                tenant_id, student_id, academic_year
            )
            
            # Create clearance record with initial status
            initial_status = (
                ClearanceStatusEnum.CLEARED
                if balance_info["outstanding_balance"] <= 0
                else ClearanceStatusEnum.OUTSTANDING
            )
            
            clearance = await self.clearance_repo.create({
                "tenant_id": tenant_id,
                "student_id": student_id,
                "academic_year": academic_year,
                "status": initial_status,
                "total_fees": balance_info["total_fees"],
                "total_paid": balance_info["total_paid"],
                "total_scholarships": balance_info["total_scholarships"],
                "outstanding_balance": balance_info["outstanding_balance"],
                "clearance_history": [{
                    "status": initial_status,
                    "timestamp": datetime.utcnow(),
                    "reason": "Initial calculation"
                }]
            })
        
        # Determine if cleared based on status
        is_cleared = clearance.status == ClearanceStatusEnum.CLEARED
        
        message = self._get_clearance_message(clearance)
        
        details = {
            "status": clearance.status,
            "total_fees": clearance.total_fees,
            "total_paid": clearance.total_paid,
            "total_scholarships": clearance.total_scholarships,
            "outstanding_balance": clearance.outstanding_balance,
            "cleared_at": clearance.cleared_at,
            "has_payment_plan": clearance.has_payment_plan,
            "payment_plan_deadline": clearance.payment_plan_deadline,
        }
        
        return is_cleared, message, details

    async def calculate_balance(
        self,
        tenant_id: str,
        student_id: str,
        academic_year: str
    ) -> Dict[str, float]:
        """
        Calculate comprehensive financial balance for a student.
        
        Returns dict with:
            - total_fees
            - total_paid
            - total_scholarships
            - outstanding_balance
        """
        # Get all payments for student
        payments = await self.payment_repo.get_by_student(tenant_id, student_id)
        
        # Sum successful payments only
        total_paid = sum(
            p.amount for p in payments
            if p.status.value == "success"
        )
        
        # Get all scholarships
        scholarships = await self.scholarship_repo.get_by_student(
            tenant_id, student_id
        )
        total_scholarships = sum(s.amount for s in scholarships)
        
        # Get fee structure for academic year and programme
        # This is simplified - in production, would need student's programme_id
        fee_structure = await self.fee_structure_repo.get_current_structure(
            tenant_id, academic_year=academic_year
        )
        
        # Calculate total fees (simplified - sum all fees from structure)
        total_fees = 0.0
        if fee_structure:
            total_fees = sum(
                float(amount) for amount in fee_structure.fees.values()
                if isinstance(amount, (int, float))
            )
        
        # Calculate balance
        outstanding_balance = total_fees - total_paid - total_scholarships
        outstanding_balance = max(0, outstanding_balance)  # Never negative
        
        return {
            "total_fees": total_fees,
            "total_paid": total_paid,
            "total_scholarships": total_scholarships,
            "outstanding_balance": outstanding_balance,
        }

    async def grant_clearance(
        self,
        tenant_id: str,
        student_id: str,
        academic_year: str,
        approved_by: str
    ) -> bool:
        """Grant financial clearance to student"""
        clearance = await self.clearance_repo.get_by_student_and_year(
            tenant_id, student_id, academic_year
        )
        
        if not clearance:
            return False
        
        # Update clearance status
        clearance.status = ClearanceStatusEnum.CLEARED
        clearance.cleared_by = approved_by
        clearance.cleared_at = datetime.utcnow()
        clearance.last_updated_at = datetime.utcnow()
        
        # Add to history
        if not clearance.clearance_history:
            clearance.clearance_history = []
        clearance.clearance_history.append({
            "status": ClearanceStatusEnum.CLEARED,
            "timestamp": datetime.utcnow(),
            "actor": approved_by,
            "reason": "Manually approved"
        })
        
        await self.clearance_repo.update(str(clearance.id), clearance.dict())
        return True

    async def revoke_clearance(
        self,
        tenant_id: str,
        student_id: str,
        academic_year: str,
        revoked_by: str,
        reason: str = "Outstanding balance detected"
    ) -> bool:
        """Revoke previously granted clearance"""
        clearance = await self.clearance_repo.get_by_student_and_year(
            tenant_id, student_id, academic_year
        )
        
        if not clearance or clearance.status != ClearanceStatusEnum.CLEARED:
            return False
        
        # Recalculate balance first
        balance_info = await self.calculate_balance(
            tenant_id, student_id, academic_year
        )
        
        clearance.status = ClearanceStatusEnum.OUTSTANDING
        clearance.revoked_by = revoked_by
        clearance.revoked_at = datetime.utcnow()
        clearance.revoked_reason = reason
        clearance.outstanding_balance = balance_info["outstanding_balance"]
        clearance.last_updated_at = datetime.utcnow()
        
        # Add to history
        if not clearance.clearance_history:
            clearance.clearance_history = []
        clearance.clearance_history.append({
            "status": ClearanceStatusEnum.OUTSTANDING,
            "timestamp": datetime.utcnow(),
            "actor": revoked_by,
            "reason": reason
        })
        
        await self.clearance_repo.update(str(clearance.id), clearance.dict())
        return True

    async def approve_payment_plan(
        self,
        tenant_id: str,
        student_id: str,
        academic_year: str,
        deadline: datetime,
        approved_by: str
    ) -> bool:
        """Approve a payment plan for student with outstanding balance"""
        clearance = await self.clearance_repo.get_by_student_and_year(
            tenant_id, student_id, academic_year
        )
        
        if not clearance:
            return False
        
        clearance.has_payment_plan = True
        clearance.payment_plan_approved_by = approved_by
        clearance.payment_plan_approved_at = datetime.utcnow()
        clearance.payment_plan_deadline = deadline
        clearance.status = ClearanceStatusEnum.CONDITIONAL
        clearance.last_updated_at = datetime.utcnow()
        
        # Add to history
        if not clearance.clearance_history:
            clearance.clearance_history = []
        clearance.clearance_history.append({
            "status": ClearanceStatusEnum.CONDITIONAL,
            "timestamp": datetime.utcnow(),
            "actor": approved_by,
            "reason": f"Payment plan approved until {deadline.date()}"
        })
        
        await self.clearance_repo.update(str(clearance.id), clearance.dict())
        return True

    async def verify_clearance_for_graduation(
        self,
        tenant_id: str,
        student_id: str,
        academic_year: str
    ) -> Tuple[bool, str]:
        """
        Verify financial clearance specifically for graduation eligibility.
        Graduation requires full clearance (not conditional).
        """
        is_cleared, message, details = await self.check_clearance(
            tenant_id, student_id, academic_year
        )
        
        # For graduation, only CLEARED status is acceptable
        if details["status"] != ClearanceStatusEnum.CLEARED:
            return False, (
                f"Financial clearance required for graduation. "
                f"Current status: {details['status']}. "
                f"Outstanding balance: GHS {details['outstanding_balance']:.2f}"
            )
        
        return True, "Financially cleared for graduation"

    def _get_clearance_message(self, clearance) -> str:
        """Generate human-readable clearance status message"""
        status_messages = {
            ClearanceStatusEnum.CLEARED: f"Financially cleared (Paid: GHS {clearance.total_paid:.2f})",
            ClearanceStatusEnum.OUTSTANDING: f"Outstanding balance: GHS {clearance.outstanding_balance:.2f}",
            ClearanceStatusEnum.CONDITIONAL: f"Payment plan approved. Deadline: {clearance.payment_plan_deadline.strftime('%Y-%m-%d') if clearance.payment_plan_deadline else 'N/A'}",
            ClearanceStatusEnum.HOLD: "Clearance on hold (debt recovery in progress)",
            ClearanceStatusEnum.PENDING: "Clearance status not yet determined",
            ClearanceStatusEnum.REVOKED: f"Clearance revoked: {clearance.revoked_reason or 'Balance outstanding'}",
        }
        return status_messages.get(
            clearance.status,
            f"Unknown clearance status: {clearance.status}"
        )
