"""
Officer Dashboard API Routes
Items 43, 46-49: All officer role endpoints

Unified routes for:
- Course Coordinator (Item 43)
- Finance Officer (Item 46)
- Hostel Manager (Item 47)
- Librarian (Item 48)
- Exam Officer (Item 49)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.presentation.dependencies import get_current_user, require_roles
from app.presentation.schemas.responses import StandardResponse

from app.application.admissions.course_coordinator_service import CourseCoordinatorService
from app.application.admissions.finance_officer_service import FinanceOfficerService
from app.application.admissions.hostel_manager_service import HostelManagerService
from app.application.admissions.librarian_service import LibrarianService
from app.application.admissions.exam_officer_service import ExamOfficerService

router = APIRouter(prefix="/api/v1/officers", tags=["Officer Dashboards"])


# ==================== COURSE COORDINATOR (ITEM 43) ====================

@router.get("/coordinator/courses", response_model=StandardResponse)
async def get_coordinated_courses(
    academic_year: int,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["course_coordinator"])),
):
    """Get courses coordinated by staff member"""
    try:
        service = CourseCoordinatorService()
        courses = await service.get_coordinated_courses(
            tenant_id=current_user.tenant_id,
            coordinator_id=current_user.id,
            academic_year=academic_year,
        )
        
        return StandardResponse(
            status="success",
            message=f"{len(courses)} courses coordinated",
            data={"courses": [c.dict() for c in courses]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coordinator/course/{course_id}/resource", response_model=StandardResponse)
async def allocate_course_resource(
    course_id: str,
    resource_type: str,
    quantity: int,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["course_coordinator"])),
):
    """Allocate resource to course"""
    try:
        service = CourseCoordinatorService()
        resource = await service.allocate_course_resource(
            tenant_id=current_user.tenant_id,
            course_id=course_id,
            resource_type=resource_type,
            quantity=quantity,
            allocated_by=current_user.email,
        )
        
        return StandardResponse(
            status="success",
            message=f"Allocated {quantity} {resource_type} to course",
            data=resource.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/coordinator/course/{course_id}/overview", response_model=StandardResponse)
async def get_course_overview(
    course_id: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["course_coordinator"])),
):
    """Get course overview"""
    try:
        service = CourseCoordinatorService()
        overview = await service.get_course_overview(
            tenant_id=current_user.tenant_id,
            course_id=course_id,
            coordinator_id=current_user.id,
        )
        
        return StandardResponse(
            status="success",
            message="Course overview retrieved",
            data=overview
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ==================== FINANCE OFFICER (ITEM 46) ====================

@router.get("/finance/student/{student_id}/fees", response_model=StandardResponse)
async def get_student_fees(
    student_id: str,
    academic_year: int,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["finance_officer"])),
):
    """Get student fee structure"""
    try:
        service = FinanceOfficerService()
        fees = await service.get_student_fee_structure(
            tenant_id=current_user.tenant_id,
            student_id=student_id,
            academic_year=academic_year,
        )
        
        if not fees:
            raise HTTPException(status_code=404, detail="Fee structure not found")
        
        return StandardResponse(
            status="success",
            message="Fee structure retrieved",
            data=fees.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finance/payment/record", response_model=StandardResponse)
async def record_payment(
    student_id: str,
    amount: float,
    payment_method: str,
    reference_number: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["finance_officer"])),
):
    """Record student payment"""
    try:
        service = FinanceOfficerService()
        payment = await service.record_payment(
            tenant_id=current_user.tenant_id,
            student_id=student_id,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
        )
        
        return StandardResponse(
            status="success",
            message="Payment recorded",
            data=payment.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/finance/outstanding-fees", response_model=StandardResponse)
async def get_outstanding_fees(
    limit: int = 50,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["finance_officer"])),
):
    """Get students with outstanding fees"""
    try:
        service = FinanceOfficerService()
        outstanding = await service.get_outstanding_fees(
            tenant_id=current_user.tenant_id,
            limit=limit,
        )
        
        return StandardResponse(
            status="success",
            message=f"{len(outstanding)} students with outstanding fees",
            data={"outstanding_fees": outstanding}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/finance/report", response_model=StandardResponse)
async def generate_financial_report(
    report_type: str,
    period: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["finance_officer"])),
):
    """Generate financial report"""
    try:
        service = FinanceOfficerService()
        report = await service.generate_financial_report(
            tenant_id=current_user.tenant_id,
            report_type=report_type,
            period=period,
            generated_by=current_user.email,
        )
        
        return StandardResponse(
            status="success",
            message=f"Generated {report_type} report",
            data=report.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HOSTEL MANAGER (ITEM 47) ====================

@router.get("/hostel/{hostel_id}/overview", response_model=StandardResponse)
async def get_hostel_overview(
    hostel_id: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["hostel_manager"])),
):
    """Get hostel overview"""
    try:
        service = HostelManagerService()
        overview = await service.get_hostel_overview(
            tenant_id=current_user.tenant_id,
            hostel_id=hostel_id,
            manager_id=current_user.id,
        )
        
        return StandardResponse(
            status="success",
            message="Hostel overview retrieved",
            data=overview
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/hostel/{hostel_id}/room-allocation", response_model=StandardResponse)
async def allocate_room(
    hostel_id: str,
    room_id: str,
    room_number: str,
    student_id: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["hostel_manager"])),
):
    """Allocate room to student"""
    try:
        service = HostelManagerService()
        allocation = await service.allocate_room(
            tenant_id=current_user.tenant_id,
            hostel_id=hostel_id,
            room_id=room_id,
            room_number=room_number,
            student_id=student_id,
            manager_id=current_user.id,
        )
        
        return StandardResponse(
            status="success",
            message="Room allocated",
            data=allocation.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/hostel/{hostel_id}/maintenance-request", response_model=StandardResponse)
async def report_maintenance(
    hostel_id: str,
    issue_type: str,
    description: str,
    room_id: Optional[str] = None,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["hostel_manager"])),
):
    """Report maintenance issue"""
    try:
        service = HostelManagerService()
        request = await service.report_maintenance(
            tenant_id=current_user.tenant_id,
            hostel_id=hostel_id,
            issue_type=issue_type,
            description=description,
            reported_by=current_user.email,
            room_id=room_id,
        )
        
        return StandardResponse(
            status="success",
            message="Maintenance request filed",
            data=request.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== LIBRARIAN (ITEM 48) ====================

@router.get("/library/overview", response_model=StandardResponse)
async def get_library_overview(
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["librarian"])),
):
    """Get library overview"""
    try:
        service = LibrarianService()
        overview = await service.get_library_overview(
            tenant_id=current_user.tenant_id,
        )
        
        return StandardResponse(
            status="success",
            message="Library overview retrieved",
            data=overview
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/library/checkout", response_model=StandardResponse)
async def checkout_resource(
    resource_id: str,
    student_id: str,
    checkout_days: int = 14,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["librarian"])),
):
    """Check out library resource"""
    try:
        service = LibrarianService()
        checkout = await service.checkout_resource(
            tenant_id=current_user.tenant_id,
            resource_id=resource_id,
            student_id=student_id,
            checkout_days=checkout_days,
        )
        
        return StandardResponse(
            status="success",
            message="Resource checked out",
            data=checkout.dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/library/student/{student_id}/overdue", response_model=StandardResponse)
async def get_overdue_items(
    student_id: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["librarian"])),
):
    """Get overdue items for student"""
    try:
        service = LibrarianService()
        overdue = await service.get_student_overdue_items(
            tenant_id=current_user.tenant_id,
            student_id=student_id,
        )
        
        return StandardResponse(
            status="success",
            message=f"{len(overdue)} overdue items",
            data={"overdue_items": [o.dict() for o in overdue]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/library/report", response_model=StandardResponse)
async def generate_library_report(
    report_type: str,
    period: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["librarian"])),
):
    """Generate library report"""
    try:
        service = LibrarianService()
        report = await service.generate_library_report(
            tenant_id=current_user.tenant_id,
            report_type=report_type,
            period=period,
        )
        
        return StandardResponse(
            status="success",
            message=f"Generated {report_type} report",
            data=report.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== EXAM OFFICER (ITEM 49) ====================

@router.post("/exam/schedule", response_model=StandardResponse)
async def schedule_exam(
    course_id: str,
    course_code: str,
    course_title: str,
    exam_date: datetime,
    start_time: str,
    end_time: str,
    venue: str,
    duration_minutes: int,
    max_capacity: int,
    enrolled_students: int,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["exam_officer"])),
):
    """Schedule examination"""
    try:
        service = ExamOfficerService()
        exam = await service.schedule_exam(
            tenant_id=current_user.tenant_id,
            course_id=course_id,
            course_code=course_code,
            course_title=course_title,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time,
            venue=venue,
            duration_minutes=duration_minutes,
            max_capacity=max_capacity,
            enrolled_students=enrolled_students,
            created_by=current_user.email,
        )
        
        return StandardResponse(
            status="success",
            message="Exam scheduled",
            data=exam.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/exam/{exam_id}/record-attendance", response_model=StandardResponse)
async def record_exam_attendance(
    exam_id: str,
    student_id: str,
    registration_number: str,
    attendance_status: str,
    seat_number: Optional[str] = None,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["exam_officer"])),
):
    """Record student exam attendance"""
    try:
        service = ExamOfficerService()
        attendance = await service.record_attendance(
            tenant_id=current_user.tenant_id,
            exam_id=exam_id,
            student_id=student_id,
            registration_number=registration_number,
            attendance_status=attendance_status,
            seat_number=seat_number,
        )
        
        return StandardResponse(
            status="success",
            message="Attendance recorded",
            data=attendance.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/exam/investigations/pending", response_model=StandardResponse)
async def get_pending_investigations(
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["exam_officer"])),
):
    """Get pending malpractice investigations"""
    try:
        service = ExamOfficerService()
        pending = await service.get_pending_investigations(
            tenant_id=current_user.tenant_id,
        )
        
        return StandardResponse(
            status="success",
            message=f"{len(pending)} pending investigations",
            data={"investigations": [i.dict() for i in pending]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exam/{exam_id}/overview", response_model=StandardResponse)
async def get_exam_overview(
    exam_id: str,
    current_user = Depends(get_current_user),
    _ = Depends(require_roles(["exam_officer"])),
):
    """Get exam overview"""
    try:
        service = ExamOfficerService()
        overview = await service.get_exam_overview(
            tenant_id=current_user.tenant_id,
            exam_id=exam_id,
        )
        
        return StandardResponse(
            status="success",
            message="Exam overview retrieved",
            data=overview
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
