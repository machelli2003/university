"""
Finance Officer Dashboard Service
Item 46: Financial operations and payment management

Finance Officer responsibilities:
- Manage student payments and fees
- Track fee collection and reconciliation
- Monitor payment plans
- Generate financial reports
- Handle refunds and adjustments
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class FeeType(str, Enum):
    """Types of fees"""
    TUITION = "tuition"
    ACCOMMODATION = "accommodation"
    LIBRARY = "library"
    LABORATORY = "laboratory"
    TECHNOLOGY = "technology"
    MISCELLANEOUS = "miscellaneous"


class PaymentMethod(str, Enum):
    """Payment methods"""
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"
    MOBILE_MONEY = "mobile_money"
    CASH = "cash"
    CHECK = "check"


# ==================== MODELS ====================

class StudentFeeStructure(BaseModel):
    """Fee breakdown for student"""
    fee_id: str
    student_id: str
    programme_id: str
    academic_year: int
    tuition_fee: float
    accommodation_fee: float = 0.0
    library_fee: float
    laboratory_fee: float = 0.0
    technology_fee: float
    miscellaneous_fee: float = 0.0
    total_fee: float
    due_date: datetime
    created_date: datetime


class PaymentRecord(BaseModel):
    """Student payment record"""
    payment_id: str
    student_id: str
    amount_paid: float
    payment_method: PaymentMethod
    payment_date: datetime
    reference_number: str
    status: PaymentStatus
    verified_by: Optional[str] = None
    notes: Optional[str] = None


class PaymentPlan(BaseModel):
    """Payment plan for student"""
    plan_id: str
    student_id: str
    total_amount: float
    installment_count: int
    installment_amount: float
    first_payment_date: datetime
    installments: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "active"
    created_by: str


class FinancialReport(BaseModel):
    """Financial report"""
    report_id: str
    report_type: str  # daily, weekly, monthly, annual
    period: str
    total_collected: float
    total_pending: float
    total_refunded: float
    payment_success_rate: float
    generated_date: datetime
    generated_by: str


class BankReconciliation(BaseModel):
    """Bank reconciliation record"""
    reconciliation_id: str
    reconciliation_date: datetime
    bank_statement_total: float
    recorded_transactions_total: float
    discrepancies: List[Dict[str, Any]] = Field(default_factory=list)
    reconciled_by: str
    status: str = "pending"  # pending, reconciled, flagged


# ==================== DOCUMENTS ====================

class StudentFeeDocument(Document):
    """Student fee structure"""
    fee_id: str = Indexed()
    tenant_id: str = Indexed()
    student_id: str = Indexed()
    programme_id: str
    academic_year: int
    tuition_fee: float
    accommodation_fee: float
    library_fee: float
    laboratory_fee: float
    technology_fee: float
    miscellaneous_fee: float
    total_fee: float
    due_date: datetime
    created_date: datetime
    
    class Settings:
        collection = "student_fees"


class PaymentRecordDocument(Document):
    """Payment records"""
    payment_id: str = Indexed()
    tenant_id: str = Indexed()
    student_id: str = Indexed()
    amount_paid: float
    payment_method: str
    payment_date: datetime = Indexed()
    reference_number: str = Indexed()
    status: str
    verified_by: Optional[str] = None
    notes: Optional[str] = None
    
    class Settings:
        collection = "payment_records"


class PaymentPlanDocument(Document):
    """Payment plans"""
    plan_id: str = Indexed()
    tenant_id: str = Indexed()
    student_id: str = Indexed()
    total_amount: float
    installment_count: int
    installment_amount: float
    first_payment_date: datetime
    installments: List[Dict[str, Any]]
    status: str
    created_by: str
    
    class Settings:
        collection = "payment_plans"


class FinancialReportDocument(Document):
    """Financial reports"""
    report_id: str = Indexed()
    tenant_id: str = Indexed()
    report_type: str
    period: str
    total_collected: float
    total_pending: float
    total_refunded: float
    payment_success_rate: float
    generated_date: datetime
    generated_by: str
    
    class Settings:
        collection = "financial_reports"


class BankReconciliationDocument(Document):
    """Bank reconciliation"""
    reconciliation_id: str = Indexed()
    tenant_id: str = Indexed()
    reconciliation_date: datetime
    bank_statement_total: float
    recorded_transactions_total: float
    discrepancies: List[Dict[str, Any]]
    reconciled_by: str
    status: str
    
    class Settings:
        collection = "bank_reconciliations"


# ==================== SERVICE ====================

class FinanceOfficerService:
    """Finance Officer operations"""
    
    async def get_student_fee_structure(
        self,
        tenant_id: str,
        student_id: str,
        academic_year: int,
    ) -> Optional[StudentFeeStructure]:
        """Get student fee breakdown"""
        doc = await StudentFeeDocument.find_one(
            StudentFeeDocument.tenant_id == tenant_id,
            StudentFeeDocument.student_id == student_id,
            StudentFeeDocument.academic_year == academic_year,
        )
        
        if not doc:
            return None
        
        return StudentFeeStructure(
            fee_id=doc.fee_id,
            student_id=doc.student_id,
            programme_id=doc.programme_id,
            academic_year=doc.academic_year,
            tuition_fee=doc.tuition_fee,
            accommodation_fee=doc.accommodation_fee,
            library_fee=doc.library_fee,
            laboratory_fee=doc.laboratory_fee,
            technology_fee=doc.technology_fee,
            miscellaneous_fee=doc.miscellaneous_fee,
            total_fee=doc.total_fee,
            due_date=doc.due_date,
            created_date=doc.created_date,
        )
    
    async def record_payment(
        self,
        tenant_id: str,
        student_id: str,
        amount: float,
        payment_method: PaymentMethod,
        reference_number: str,
        notes: Optional[str] = None,
    ) -> PaymentRecord:
        """Record student payment"""
        payment_id = f"PAY-{student_id}-{datetime.utcnow().timestamp()}"
        
        doc = PaymentRecordDocument(
            payment_id=payment_id,
            tenant_id=tenant_id,
            student_id=student_id,
            amount_paid=amount,
            payment_method=payment_method.value,
            payment_date=datetime.utcnow(),
            reference_number=reference_number,
            status=PaymentStatus.PENDING.value,
            notes=notes,
        )
        
        await doc.insert()
        
        logger.info(
            f"Recorded payment {payment_id}: ${amount} from {student_id}"
        )
        
        return PaymentRecord(
            payment_id=payment_id,
            student_id=student_id,
            amount_paid=amount,
            payment_method=payment_method,
            payment_date=doc.payment_date,
            reference_number=reference_number,
            status=PaymentStatus.PENDING,
            notes=notes,
        )
    
    async def verify_payment(
        self,
        tenant_id: str,
        payment_id: str,
        verified_by: str,
    ) -> PaymentRecord:
        """Verify and complete payment"""
        doc = await PaymentRecordDocument.find_one(
            PaymentRecordDocument.tenant_id == tenant_id,
            PaymentRecordDocument.payment_id == payment_id,
        )
        
        if not doc:
            raise ValueError(f"Payment {payment_id} not found")
        
        doc.status = PaymentStatus.COMPLETED.value
        doc.verified_by = verified_by
        await doc.save()
        
        logger.info(f"Verified payment {payment_id}")
        
        return PaymentRecord(**doc.dict())
    
    async def create_payment_plan(
        self,
        tenant_id: str,
        student_id: str,
        total_amount: float,
        installment_count: int,
        first_payment_date: datetime,
        created_by: str,
    ) -> PaymentPlan:
        """Create payment plan for student"""
        plan_id = f"PLAN-{student_id}-{datetime.utcnow().timestamp()}"
        installment_amount = total_amount / installment_count
        
        # Generate installment schedule
        installments = []
        from datetime import timedelta
        for i in range(installment_count):
            payment_date = first_payment_date + timedelta(days=30*i)
            installments.append({
                "installment_number": i + 1,
                "amount": installment_amount,
                "due_date": payment_date,
                "status": "pending",
            })
        
        doc = PaymentPlanDocument(
            plan_id=plan_id,
            tenant_id=tenant_id,
            student_id=student_id,
            total_amount=total_amount,
            installment_count=installment_count,
            installment_amount=installment_amount,
            first_payment_date=first_payment_date,
            installments=installments,
            status="active",
            created_by=created_by,
        )
        
        await doc.insert()
        
        logger.info(
            f"Created payment plan {plan_id}: ${total_amount} in {installment_count} installments"
        )
        
        return PaymentPlan(
            plan_id=plan_id,
            student_id=student_id,
            total_amount=total_amount,
            installment_count=installment_count,
            installment_amount=installment_amount,
            first_payment_date=first_payment_date,
            installments=installments,
            created_by=created_by,
        )
    
    async def get_student_payment_history(
        self,
        tenant_id: str,
        student_id: str,
    ) -> List[PaymentRecord]:
        """Get all payments from student"""
        docs = await PaymentRecordDocument.find(
            PaymentRecordDocument.tenant_id == tenant_id,
            PaymentRecordDocument.student_id == student_id,
        ).sort([("payment_date", -1)]).to_list()
        
        return [PaymentRecord(**d.dict()) for d in docs]
    
    async def get_outstanding_fees(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get students with outstanding fees"""
        fees = await StudentFeeDocument.find(
            StudentFeeDocument.tenant_id == tenant_id,
        ).limit(limit).to_list()
        
        # Calculate amounts paid per student
        outstanding = []
        for fee in fees:
            payments = await self.get_student_payment_history(tenant_id, fee.student_id)
            total_paid = sum(p.amount_paid for p in payments if p.status == PaymentStatus.COMPLETED.value)
            amount_outstanding = fee.total_fee - total_paid
            
            if amount_outstanding > 0:
                outstanding.append({
                    "student_id": fee.student_id,
                    "total_fee": fee.total_fee,
                    "amount_paid": total_paid,
                    "amount_outstanding": amount_outstanding,
                    "due_date": fee.due_date,
                    "days_overdue": (datetime.utcnow() - fee.due_date).days if fee.due_date < datetime.utcnow() else 0,
                })
        
        return sorted(outstanding, key=lambda x: x["amount_outstanding"], reverse=True)
    
    async def generate_financial_report(
        self,
        tenant_id: str,
        report_type: str,  # daily, weekly, monthly, annual
        period: str,
        generated_by: str,
    ) -> FinancialReport:
        """Generate financial report"""
        # Query all payments in period
        payments = await PaymentRecordDocument.find(
            PaymentRecordDocument.tenant_id == tenant_id,
        ).to_list()
        
        completed_payments = [p for p in payments if p.status == PaymentStatus.COMPLETED.value]
        total_collected = sum(p.amount_paid for p in completed_payments)
        total_refunded = sum(p.amount_paid for p in payments if p.status == PaymentStatus.REFUNDED.value)
        
        # Calculate pending
        fees = await StudentFeeDocument.find(
            StudentFeeDocument.tenant_id == tenant_id,
        ).to_list()
        total_fees = sum(f.total_fee for f in fees)
        total_pending = total_fees - total_collected
        
        # Success rate
        success_rate = (len(completed_payments) / len(payments) * 100) if payments else 0
        
        report_id = f"REP-FIN-{report_type}-{period}"
        
        doc = FinancialReportDocument(
            report_id=report_id,
            tenant_id=tenant_id,
            report_type=report_type,
            period=period,
            total_collected=total_collected,
            total_pending=total_pending,
            total_refunded=total_refunded,
            payment_success_rate=success_rate,
            generated_date=datetime.utcnow(),
            generated_by=generated_by,
        )
        
        await doc.insert()
        
        logger.info(f"Generated {report_type} financial report for {period}")
        
        return FinancialReport(
            report_id=report_id,
            report_type=report_type,
            period=period,
            total_collected=total_collected,
            total_pending=total_pending,
            total_refunded=total_refunded,
            payment_success_rate=success_rate,
            generated_date=doc.generated_date,
            generated_by=generated_by,
        )
    
    async def reconcile_payments(
        self,
        tenant_id: str,
        bank_total: float,
        reconciled_by: str,
    ) -> BankReconciliation:
        """Reconcile payments with bank statement"""
        # Query all completed payments
        payments = await PaymentRecordDocument.find(
            PaymentRecordDocument.tenant_id == tenant_id,
            PaymentRecordDocument.status == PaymentStatus.COMPLETED.value,
        ).to_list()
        
        recorded_total = sum(p.amount_paid for p in payments)
        discrepancy = abs(bank_total - recorded_total)
        
        status = "reconciled" if discrepancy == 0 else "flagged"
        
        reconciliation_id = f"REC-{datetime.utcnow().timestamp()}"
        
        doc = BankReconciliationDocument(
            reconciliation_id=reconciliation_id,
            tenant_id=tenant_id,
            reconciliation_date=datetime.utcnow(),
            bank_statement_total=bank_total,
            recorded_transactions_total=recorded_total,
            discrepancies=[
                {
                    "type": "amount_difference",
                    "amount": discrepancy,
                    "description": f"Bank total ${bank_total} vs recorded ${recorded_total}",
                }
            ] if discrepancy > 0 else [],
            reconciled_by=reconciled_by,
            status=status,
        )
        
        await doc.insert()
        
        logger.info(
            f"Reconciliation {reconciliation_id}: Bank ${bank_total}, Recorded ${recorded_total}, Status: {status}"
        )
        
        return BankReconciliation(
            reconciliation_id=reconciliation_id,
            reconciliation_date=doc.reconciliation_date,
            bank_statement_total=bank_total,
            recorded_transactions_total=recorded_total,
            discrepancies=doc.discrepancies,
            reconciled_by=reconciled_by,
            status=status,
        )
