"""
Dean Dashboard Service
Item 45: Faculty-level management and oversight

Dean responsibilities:
- Manage faculty structure (departments)
- Oversee academic programmes
- Review academic performance
- Manage faculty budget and resources
- Make strategic academic decisions
- Review and approve departmental initiatives
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class FacultyStatus(str, Enum):
    """Faculty operational status"""
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    RESTRUCTURING = "restructuring"
    INACTIVE = "inactive"


class ApprovalStatus(str, Enum):
    """Status of approval requests"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"


# ==================== MODELS ====================

class FacultyDepartment(BaseModel):
    """Department within faculty"""
    department_id: str
    department_name: str
    department_code: str
    faculty_id: str
    head_of_department_id: str
    head_name: str
    total_staff: int
    total_students: int
    programmes_offered: int
    status: str = "active"


class FacultyProgramme(BaseModel):
    """Academic programme in faculty"""
    programme_id: str
    programme_name: str
    programme_code: str
    faculty_id: str
    department_id: str
    level: str  # undergraduate, postgraduate, doctorate
    accreditation_status: str  # accredited, pending, unaccredited
    students_enrolled: int
    coordinator_id: str
    last_reviewed: datetime


class FacultyAcademicMetrics(BaseModel):
    """Faculty-level academic performance"""
    faculty_id: str
    total_departments: int
    total_programmes: int
    total_staff: int
    total_students: int
    average_gpa: float
    pass_rate: float  # percentage
    graduation_rate: float  # percentage
    research_productivity: int  # publications/research output
    student_satisfaction: float  # 0-5
    accreditation_rating: str  # excellent, good, satisfactory, needs improvement
    calculated_at: datetime


class DepartmentApprovalRequest(BaseModel):
    """Request from department for dean approval"""
    request_id: str
    department_id: str
    faculty_id: str
    request_type: str  # new_programme, curriculum_change, resource_allocation, staffing
    description: str
    submitted_by: str
    submitted_date: datetime
    status: ApprovalStatus
    dean_review: Optional[str] = None
    approval_date: Optional[datetime] = None
    approved_by: Optional[str] = None


class FacultyBudgetAllocation(BaseModel):
    """Budget allocation for faculty"""
    allocation_id: str
    faculty_id: str
    budget_cycle: str  # e.g., "2024-2025"
    total_budget: float
    personnel_budget: float
    operating_budget: float
    infrastructure_budget: float
    research_budget: float
    allocated_date: datetime
    allocated_by: str
    status: str = "active"


class FacultyReport(BaseModel):
    """Faculty performance report"""
    report_id: str
    faculty_id: str
    report_type: str  # annual, semester, accreditation
    period: str  # e.g., "2024-2025"
    generated_date: datetime
    generated_by: str
    content: Dict[str, Any]  # Key metrics and findings


# ==================== DOCUMENTS ====================

class FacultyDepartmentDocument(Document):
    """Faculty departments"""
    department_id: str = Indexed()
    tenant_id: str = Indexed()
    department_name: str
    department_code: str
    faculty_id: str = Indexed()
    head_of_department_id: str
    head_name: str
    total_staff: int
    total_students: int
    programmes_offered: int
    status: str
    
    class Settings:
        collection = "faculty_departments"


class FacultyProgrammeDocument(Document):
    """Faculty programmes"""
    programme_id: str = Indexed()
    tenant_id: str = Indexed()
    programme_name: str
    programme_code: str
    faculty_id: str = Indexed()
    department_id: str
    level: str
    accreditation_status: str
    students_enrolled: int
    coordinator_id: str
    last_reviewed: datetime
    
    class Settings:
        collection = "faculty_programmes"


class FacultyMetricsDocument(Document):
    """Faculty performance metrics"""
    metrics_id: str = Indexed()
    tenant_id: str = Indexed()
    faculty_id: str = Indexed()
    calculated_at: datetime = Indexed()
    total_departments: int
    total_programmes: int
    total_staff: int
    total_students: int
    average_gpa: float
    pass_rate: float
    graduation_rate: float
    research_productivity: int
    student_satisfaction: float
    accreditation_rating: str
    
    class Settings:
        collection = "faculty_metrics"


class DepartmentApprovalRequestDocument(Document):
    """Approval requests from departments"""
    request_id: str = Indexed()
    tenant_id: str = Indexed()
    department_id: str = Indexed()
    faculty_id: str = Indexed()
    request_type: str
    description: str
    submitted_by: str
    submitted_date: datetime
    status: str
    dean_review: Optional[str] = None
    approval_date: Optional[datetime] = None
    approved_by: Optional[str] = None
    
    class Settings:
        collection = "department_approval_requests"


class FacultyBudgetDocument(Document):
    """Faculty budget allocations"""
    allocation_id: str = Indexed()
    tenant_id: str = Indexed()
    faculty_id: str = Indexed()
    budget_cycle: str
    total_budget: float
    personnel_budget: float
    operating_budget: float
    infrastructure_budget: float
    research_budget: float
    allocated_date: datetime
    allocated_by: str
    status: str
    
    class Settings:
        collection = "faculty_budgets"


class FacultyReportDocument(Document):
    """Faculty reports"""
    report_id: str = Indexed()
    tenant_id: str = Indexed()
    faculty_id: str = Indexed()
    report_type: str
    period: str
    generated_date: datetime
    generated_by: str
    content: Dict[str, Any]
    
    class Settings:
        collection = "faculty_reports"


# ==================== SERVICE ====================

class DeanService:
    """Dean (Faculty Head) operations"""
    
    async def get_faculty_departments(
        self,
        tenant_id: str,
        faculty_id: str,
    ) -> List[FacultyDepartment]:
        """Get all departments in faculty"""
        docs = await FacultyDepartmentDocument.find(
            FacultyDepartmentDocument.tenant_id == tenant_id,
            FacultyDepartmentDocument.faculty_id == faculty_id,
        ).to_list()
        
        return [
            FacultyDepartment(
                department_id=d.department_id,
                department_name=d.department_name,
                department_code=d.department_code,
                faculty_id=d.faculty_id,
                head_of_department_id=d.head_of_department_id,
                head_name=d.head_name,
                total_staff=d.total_staff,
                total_students=d.total_students,
                programmes_offered=d.programmes_offered,
                status=d.status,
            )
            for d in docs
        ]
    
    async def get_faculty_programmes(
        self,
        tenant_id: str,
        faculty_id: str,
    ) -> List[FacultyProgramme]:
        """Get all programmes in faculty"""
        docs = await FacultyProgrammeDocument.find(
            FacultyProgrammeDocument.tenant_id == tenant_id,
            FacultyProgrammeDocument.faculty_id == faculty_id,
        ).to_list()
        
        return [
            FacultyProgramme(
                programme_id=d.programme_id,
                programme_name=d.programme_name,
                programme_code=d.programme_code,
                faculty_id=d.faculty_id,
                department_id=d.department_id,
                level=d.level,
                accreditation_status=d.accreditation_status,
                students_enrolled=d.students_enrolled,
                coordinator_id=d.coordinator_id,
                last_reviewed=d.last_reviewed,
            )
            for d in docs
        ]
    
    async def calculate_faculty_metrics(
        self,
        tenant_id: str,
        faculty_id: str,
    ) -> FacultyAcademicMetrics:
        """Calculate faculty-level performance metrics"""
        departments = await self.get_faculty_departments(tenant_id, faculty_id)
        programmes = await self.get_faculty_programmes(tenant_id, faculty_id)
        
        # Aggregate data
        total_departments = len(departments)
        total_programmes = len(programmes)
        total_staff = sum(d.total_staff for d in departments)
        total_students = sum(d.total_students for d in departments)
        
        # Placeholder metrics (would be calculated from actual data)
        average_gpa = 3.52
        pass_rate = 87.3
        graduation_rate = 91.5
        research_productivity = 45
        student_satisfaction = 4.3
        accreditation_rating = "excellent"
        
        metrics = FacultyAcademicMetrics(
            faculty_id=faculty_id,
            total_departments=total_departments,
            total_programmes=total_programmes,
            total_staff=total_staff,
            total_students=total_students,
            average_gpa=average_gpa,
            pass_rate=pass_rate,
            graduation_rate=graduation_rate,
            research_productivity=research_productivity,
            student_satisfaction=student_satisfaction,
            accreditation_rating=accreditation_rating,
            calculated_at=datetime.utcnow(),
        )
        
        # Store metrics
        doc = FacultyMetricsDocument(
            metrics_id=f"FAC-METRICS-{faculty_id}-{datetime.utcnow().timestamp()}",
            tenant_id=tenant_id,
            faculty_id=faculty_id,
            calculated_at=datetime.utcnow(),
            **metrics.dict()
        )
        
        await doc.insert()
        
        logger.info(
            f"Calculated metrics for faculty {faculty_id}: "
            f"{total_staff} staff, {total_students} students, {pass_rate}% pass rate"
        )
        
        return metrics
    
    async def get_pending_approvals(
        self,
        tenant_id: str,
        faculty_id: str,
    ) -> List[DepartmentApprovalRequest]:
        """Get pending approval requests from departments"""
        docs = await DepartmentApprovalRequestDocument.find(
            DepartmentApprovalRequestDocument.tenant_id == tenant_id,
            DepartmentApprovalRequestDocument.faculty_id == faculty_id,
            DepartmentApprovalRequestDocument.status == ApprovalStatus.PENDING.value,
        ).to_list()
        
        return [
            DepartmentApprovalRequest(
                request_id=d.request_id,
                department_id=d.department_id,
                faculty_id=d.faculty_id,
                request_type=d.request_type,
                description=d.description,
                submitted_by=d.submitted_by,
                submitted_date=d.submitted_date,
                status=ApprovalStatus(d.status),
                dean_review=d.dean_review,
                approval_date=d.approval_date,
                approved_by=d.approved_by,
            )
            for d in docs
        ]
    
    async def approve_department_request(
        self,
        tenant_id: str,
        faculty_id: str,
        request_id: str,
        dean_email: str,
        review_notes: Optional[str] = None,
    ) -> DepartmentApprovalRequest:
        """Approve department request"""
        doc = await DepartmentApprovalRequestDocument.find_one(
            DepartmentApprovalRequestDocument.tenant_id == tenant_id,
            DepartmentApprovalRequestDocument.faculty_id == faculty_id,
            DepartmentApprovalRequestDocument.request_id == request_id,
        )
        
        if not doc:
            raise ValueError(f"Request {request_id} not found")
        
        doc.status = ApprovalStatus.APPROVED.value
        doc.approval_date = datetime.utcnow()
        doc.approved_by = dean_email
        doc.dean_review = review_notes
        await doc.save()
        
        logger.info(f"Dean {dean_email} approved request {request_id}")
        
        return DepartmentApprovalRequest(**doc.dict())
    
    async def reject_department_request(
        self,
        tenant_id: str,
        faculty_id: str,
        request_id: str,
        dean_email: str,
        rejection_reason: str,
    ) -> DepartmentApprovalRequest:
        """Reject department request"""
        doc = await DepartmentApprovalRequestDocument.find_one(
            DepartmentApprovalRequestDocument.tenant_id == tenant_id,
            DepartmentApprovalRequestDocument.faculty_id == faculty_id,
            DepartmentApprovalRequestDocument.request_id == request_id,
        )
        
        if not doc:
            raise ValueError(f"Request {request_id} not found")
        
        doc.status = ApprovalStatus.REJECTED.value
        doc.approval_date = datetime.utcnow()
        doc.approved_by = dean_email
        doc.dean_review = rejection_reason
        await doc.save()
        
        logger.info(f"Dean {dean_email} rejected request {request_id}")
        
        return DepartmentApprovalRequest(**doc.dict())
    
    async def allocate_budget(
        self,
        tenant_id: str,
        faculty_id: str,
        budget_cycle: str,
        total_budget: float,
        personnel_budget: float,
        operating_budget: float,
        infrastructure_budget: float,
        research_budget: float,
        allocated_by: str,
    ) -> FacultyBudgetAllocation:
        """Allocate budget for faculty"""
        allocation_id = f"BUD-{faculty_id}-{budget_cycle}"
        
        doc = FacultyBudgetDocument(
            allocation_id=allocation_id,
            tenant_id=tenant_id,
            faculty_id=faculty_id,
            budget_cycle=budget_cycle,
            total_budget=total_budget,
            personnel_budget=personnel_budget,
            operating_budget=operating_budget,
            infrastructure_budget=infrastructure_budget,
            research_budget=research_budget,
            allocated_date=datetime.utcnow(),
            allocated_by=allocated_by,
            status="active",
        )
        
        await doc.insert()
        
        logger.info(f"Allocated budget {allocation_id}: ${total_budget}")
        
        return FacultyBudgetAllocation(
            allocation_id=allocation_id,
            faculty_id=faculty_id,
            budget_cycle=budget_cycle,
            total_budget=total_budget,
            personnel_budget=personnel_budget,
            operating_budget=operating_budget,
            infrastructure_budget=infrastructure_budget,
            research_budget=research_budget,
            allocated_date=doc.allocated_date,
            allocated_by=allocated_by,
            status=doc.status,
        )
    
    async def generate_faculty_report(
        self,
        tenant_id: str,
        faculty_id: str,
        report_type: str,  # annual, semester, accreditation
        period: str,
        dean_email: str,
    ) -> FacultyReport:
        """Generate faculty performance report"""
        metrics = await self.calculate_faculty_metrics(tenant_id, faculty_id)
        
        report_content = {
            "faculty_id": faculty_id,
            "report_type": report_type,
            "period": period,
            "metrics": metrics.dict(),
            "summary": {
                "key_achievements": [],
                "areas_for_improvement": [],
                "recommendations": [],
            }
        }
        
        report_id = f"REP-{faculty_id}-{report_type}-{period}"
        
        doc = FacultyReportDocument(
            report_id=report_id,
            tenant_id=tenant_id,
            faculty_id=faculty_id,
            report_type=report_type,
            period=period,
            generated_date=datetime.utcnow(),
            generated_by=dean_email,
            content=report_content,
        )
        
        await doc.insert()
        
        logger.info(f"Generated {report_type} report {report_id}")
        
        return FacultyReport(
            report_id=report_id,
            faculty_id=faculty_id,
            report_type=report_type,
            period=period,
            generated_date=doc.generated_date,
            generated_by=dean_email,
            content=report_content,
        )
    
    async def get_faculty_overview(
        self,
        tenant_id: str,
        faculty_id: str,
    ) -> Dict[str, Any]:
        """Get comprehensive faculty overview"""
        departments = await self.get_faculty_departments(tenant_id, faculty_id)
        programmes = await self.get_faculty_programmes(tenant_id, faculty_id)
        metrics = await self.calculate_faculty_metrics(tenant_id, faculty_id)
        pending_approvals = await self.get_pending_approvals(tenant_id, faculty_id)
        
        return {
            "faculty_id": faculty_id,
            "total_departments": len(departments),
            "total_programmes": len(programmes),
            "departments": [d.dict() for d in departments],
            "programmes": [p.dict() for p in programmes],
            "metrics": metrics.dict(),
            "pending_approvals_count": len(pending_approvals),
            "pending_approvals": [a.dict() for a in pending_approvals],
        }
    
    async def get_faculty_reports(
        self,
        tenant_id: str,
        faculty_id: str,
        limit: int = 20,
    ) -> List[FacultyReport]:
        """Get faculty reports"""
        docs = await FacultyReportDocument.find(
            FacultyReportDocument.tenant_id == tenant_id,
            FacultyReportDocument.faculty_id == faculty_id,
        ).sort([("generated_date", -1)]).limit(limit).to_list()
        
        return [
            FacultyReport(
                report_id=d.report_id,
                faculty_id=d.faculty_id,
                report_type=d.report_type,
                period=d.period,
                generated_date=d.generated_date,
                generated_by=d.generated_by,
                content=d.content,
            )
            for d in docs
        ]
