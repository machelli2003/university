"""
Exam Officer Dashboard Service
Item 49: Examination scheduling and management

Exam Officer responsibilities:
- Schedule examinations
- Manage exam venues and invigilation
- Track exam attendance
- Handle exam incidents/malpractices
- Generate exam reports
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class ExamStatus(str, Enum):
    """Exam status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"


class AttendanceStatus(str, Enum):
    """Student exam attendance"""
    ATTENDED = "attended"
    ABSENT = "absent"
    EXCUSED = "excused"
    LATE = "late"


class MalpracticeType(str, Enum):
    """Types of exam malpractices"""
    CHEATING = "cheating"
    IMPERSONATION = "impersonation"
    UNAUTHORIZED_MATERIALS = "unauthorized_materials"
    DISRUPTION = "disruption"
    OTHER = "other"


# ==================== MODELS ====================

class ExamSchedule(BaseModel):
    """Exam schedule"""
    exam_id: str
    course_id: str
    course_code: str
    course_title: str
    exam_date: datetime
    start_time: str
    end_time: str
    venue: str
    duration_minutes: int
    max_capacity: int
    enrolled_students: int
    status: ExamStatus
    created_by: str


class InvigilationAssignment(BaseModel):
    """Examiner/invigilator assignment"""
    assignment_id: str
    exam_id: str
    staff_id: str
    staff_name: str
    role: str  # chief_invigilator, invigilator, assistant
    assigned_date: datetime
    venue_section: str
    student_count: int


class ExamAttendance(BaseModel):
    """Student exam attendance record"""
    attendance_id: str
    exam_id: str
    student_id: str
    check_in_time: datetime
    attendance_status: AttendanceStatus
    registration_number: str
    seat_number: Optional[str] = None


class MalpracticeIncident(BaseModel):
    """Exam malpractice incident"""
    incident_id: str
    exam_id: str
    student_id: str
    incident_type: MalpracticeType
    description: str
    reported_by: str
    reported_date: datetime
    evidence: List[str] = Field(default_factory=list)
    investigation_status: str  # pending, under_review, completed
    action_taken: Optional[str] = None
    severity: str = "medium"  # low, medium, high


class ExamResult(BaseModel):
    """Exam result"""
    result_id: str
    exam_id: str
    student_id: str
    score: float
    grade: str
    remarks: Optional[str] = None
    entered_by: str
    entry_date: datetime
    status: str = "pending_approval"  # pending_approval, approved, rejected


class ExamReport(BaseModel):
    """Examination report"""
    report_id: str
    exam_id: str
    report_type: str  # attendance, performance, incidents
    total_students: int
    attended: int
    absent: int
    attendance_rate: float
    malpractice_incidents: int
    generated_date: datetime


# ==================== DOCUMENTS ====================

class ExamScheduleDocument(Document):
    """Exam schedules"""
    exam_id: str = Indexed()
    tenant_id: str = Indexed()
    course_id: str = Indexed()
    course_code: str
    course_title: str
    exam_date: datetime
    start_time: str
    end_time: str
    venue: str
    duration_minutes: int
    max_capacity: int
    enrolled_students: int
    status: str
    created_by: str
    
    class Settings:
        collection = "exam_schedules"


class InvigilationAssignmentDocument(Document):
    """Invigilation assignments"""
    assignment_id: str = Indexed()
    tenant_id: str = Indexed()
    exam_id: str = Indexed()
    staff_id: str = Indexed()
    staff_name: str
    role: str
    assigned_date: datetime
    venue_section: str
    student_count: int
    
    class Settings:
        collection = "invigilation_assignments"


class ExamAttendanceDocument(Document):
    """Exam attendance records"""
    attendance_id: str = Indexed()
    tenant_id: str = Indexed()
    exam_id: str = Indexed()
    student_id: str = Indexed()
    check_in_time: datetime
    attendance_status: str
    registration_number: str
    seat_number: Optional[str] = None
    
    class Settings:
        collection = "exam_attendance"


class MalpracticeIncidentDocument(Document):
    """Malpractice incidents"""
    incident_id: str = Indexed()
    tenant_id: str = Indexed()
    exam_id: str = Indexed()
    student_id: str = Indexed()
    incident_type: str
    description: str
    reported_by: str
    reported_date: datetime
    evidence: List[str]
    investigation_status: str
    action_taken: Optional[str] = None
    severity: str
    
    class Settings:
        collection = "malpractice_incidents"


class ExamResultDocument(Document):
    """Exam results"""
    result_id: str = Indexed()
    tenant_id: str = Indexed()
    exam_id: str = Indexed()
    student_id: str = Indexed()
    score: float
    grade: str
    remarks: Optional[str] = None
    entered_by: str
    entry_date: datetime
    status: str
    
    class Settings:
        collection = "exam_results"


class ExamReportDocument(Document):
    """Exam reports"""
    report_id: str = Indexed()
    tenant_id: str = Indexed()
    exam_id: str = Indexed()
    report_type: str
    total_students: int
    attended: int
    absent: int
    attendance_rate: float
    malpractice_incidents: int
    generated_date: datetime
    
    class Settings:
        collection = "exam_reports"


# ==================== SERVICE ====================

class ExamOfficerService:
    """Exam Officer operations"""
    
    async def schedule_exam(
        self,
        tenant_id: str,
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
        created_by: str,
    ) -> ExamSchedule:
        """Schedule examination"""
        exam_id = f"EXAM-{course_id}-{exam_date.timestamp()}"
        
        doc = ExamScheduleDocument(
            exam_id=exam_id,
            tenant_id=tenant_id,
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
            status=ExamStatus.SCHEDULED.value,
            created_by=created_by,
        )
        
        await doc.insert()
        
        logger.info(f"Scheduled exam {exam_id} for {course_code} on {exam_date.date()}")
        
        return ExamSchedule(
            exam_id=exam_id,
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
            status=ExamStatus.SCHEDULED,
            created_by=created_by,
        )
    
    async def assign_invigilator(
        self,
        tenant_id: str,
        exam_id: str,
        staff_id: str,
        staff_name: str,
        role: str,  # chief_invigilator, invigilator
        venue_section: str,
        student_count: int,
    ) -> InvigilationAssignment:
        """Assign invigilator to exam"""
        assignment_id = f"INV-{exam_id}-{staff_id}"
        
        doc = InvigilationAssignmentDocument(
            assignment_id=assignment_id,
            tenant_id=tenant_id,
            exam_id=exam_id,
            staff_id=staff_id,
            staff_name=staff_name,
            role=role,
            assigned_date=datetime.utcnow(),
            venue_section=venue_section,
            student_count=student_count,
        )
        
        await doc.insert()
        
        logger.info(f"Assigned {staff_name} ({role}) to {exam_id}")
        
        return InvigilationAssignment(
            assignment_id=assignment_id,
            exam_id=exam_id,
            staff_id=staff_id,
            staff_name=staff_name,
            role=role,
            assigned_date=doc.assigned_date,
            venue_section=venue_section,
            student_count=student_count,
        )
    
    async def record_attendance(
        self,
        tenant_id: str,
        exam_id: str,
        student_id: str,
        registration_number: str,
        attendance_status: AttendanceStatus,
        seat_number: Optional[str] = None,
    ) -> ExamAttendance:
        """Record student exam attendance"""
        attendance_id = f"ATTEND-{exam_id}-{student_id}"
        
        doc = ExamAttendanceDocument(
            attendance_id=attendance_id,
            tenant_id=tenant_id,
            exam_id=exam_id,
            student_id=student_id,
            check_in_time=datetime.utcnow(),
            attendance_status=attendance_status.value,
            registration_number=registration_number,
            seat_number=seat_number,
        )
        
        await doc.insert()
        
        logger.info(
            f"Recorded {attendance_status.value} for {student_id} in exam {exam_id}"
        )
        
        return ExamAttendance(
            attendance_id=attendance_id,
            exam_id=exam_id,
            student_id=student_id,
            check_in_time=doc.check_in_time,
            attendance_status=attendance_status,
            registration_number=registration_number,
            seat_number=seat_number,
        )
    
    async def report_malpractice(
        self,
        tenant_id: str,
        exam_id: str,
        student_id: str,
        incident_type: MalpracticeType,
        description: str,
        reported_by: str,
        severity: str = "medium",
        evidence: Optional[List[str]] = None,
    ) -> MalpracticeIncident:
        """Report exam malpractice incident"""
        incident_id = f"MAL-{exam_id}-{student_id}-{datetime.utcnow().timestamp()}"
        
        doc = MalpracticeIncidentDocument(
            incident_id=incident_id,
            tenant_id=tenant_id,
            exam_id=exam_id,
            student_id=student_id,
            incident_type=incident_type.value,
            description=description,
            reported_by=reported_by,
            reported_date=datetime.utcnow(),
            evidence=evidence or [],
            investigation_status="pending",
            severity=severity,
        )
        
        await doc.insert()
        
        logger.warning(
            f"Malpractice incident {incident_id}: {incident_type.value} - {severity}"
        )
        
        return MalpracticeIncident(
            incident_id=incident_id,
            exam_id=exam_id,
            student_id=student_id,
            incident_type=incident_type,
            description=description,
            reported_by=reported_by,
            reported_date=doc.reported_date,
            evidence=evidence or [],
            investigation_status="pending",
            severity=severity,
        )
    
    async def get_pending_investigations(
        self,
        tenant_id: str,
        limit: int = 20,
    ) -> List[MalpracticeIncident]:
        """Get pending malpractice investigations"""
        docs = await MalpracticeIncidentDocument.find(
            MalpracticeIncidentDocument.tenant_id == tenant_id,
            MalpracticeIncidentDocument.investigation_status.isin(["pending", "under_review"]),
        ).limit(limit).to_list()
        
        return [MalpracticeIncident(**d.dict()) for d in docs]
    
    async def enter_exam_result(
        self,
        tenant_id: str,
        exam_id: str,
        student_id: str,
        score: float,
        entered_by: str,
        remarks: Optional[str] = None,
    ) -> ExamResult:
        """Enter exam result"""
        # Grade conversion
        if score >= 70:
            grade = "A"
        elif score >= 60:
            grade = "B"
        elif score >= 50:
            grade = "C"
        elif score >= 40:
            grade = "D"
        else:
            grade = "F"
        
        result_id = f"RES-{exam_id}-{student_id}"
        
        doc = ExamResultDocument(
            result_id=result_id,
            tenant_id=tenant_id,
            exam_id=exam_id,
            student_id=student_id,
            score=score,
            grade=grade,
            remarks=remarks,
            entered_by=entered_by,
            entry_date=datetime.utcnow(),
            status="pending_approval",
        )
        
        await doc.insert()
        
        logger.info(f"Entered result for {student_id}: {grade} ({score})")
        
        return ExamResult(
            result_id=result_id,
            exam_id=exam_id,
            student_id=student_id,
            score=score,
            grade=grade,
            remarks=remarks,
            entered_by=entered_by,
            entry_date=doc.entry_date,
            status="pending_approval",
        )
    
    async def approve_exam_results(
        self,
        tenant_id: str,
        exam_id: str,
        approved_by: str,
    ) -> Dict[str, Any]:
        """Approve all results for exam"""
        docs = await ExamResultDocument.find(
            ExamResultDocument.tenant_id == tenant_id,
            ExamResultDocument.exam_id == exam_id,
            ExamResultDocument.status == "pending_approval",
        ).to_list()
        
        count = 0
        for doc in docs:
            doc.status = "approved"
            await doc.save()
            count += 1
        
        logger.info(f"Approved {count} results for exam {exam_id}")
        
        return {"exam_id": exam_id, "results_approved": count}
    
    async def generate_exam_report(
        self,
        tenant_id: str,
        exam_id: str,
        report_type: str,  # attendance, performance, incidents
    ) -> ExamReport:
        """Generate exam report"""
        # Get attendance records
        attendance = await ExamAttendanceDocument.find(
            ExamAttendanceDocument.tenant_id == tenant_id,
            ExamAttendanceDocument.exam_id == exam_id,
        ).to_list()
        
        attended = len([a for a in attendance if a.attendance_status == AttendanceStatus.ATTENDED.value])
        absent = len([a for a in attendance if a.attendance_status == AttendanceStatus.ABSENT.value])
        
        attendance_rate = (attended / len(attendance) * 100) if attendance else 0
        
        # Get malpractice incidents
        incidents = await MalpracticeIncidentDocument.find(
            MalpracticeIncidentDocument.tenant_id == tenant_id,
            MalpracticeIncidentDocument.exam_id == exam_id,
        ).to_list()
        
        report_id = f"REP-EXAM-{exam_id}-{report_type}"
        
        doc = ExamReportDocument(
            report_id=report_id,
            tenant_id=tenant_id,
            exam_id=exam_id,
            report_type=report_type,
            total_students=len(attendance),
            attended=attended,
            absent=absent,
            attendance_rate=round(attendance_rate, 2),
            malpractice_incidents=len(incidents),
            generated_date=datetime.utcnow(),
        )
        
        await doc.insert()
        
        logger.info(
            f"Generated {report_type} report for {exam_id}: "
            f"{attendance_rate}% attendance, {len(incidents)} incidents"
        )
        
        return ExamReport(
            report_id=report_id,
            exam_id=exam_id,
            report_type=report_type,
            total_students=len(attendance),
            attended=attended,
            absent=absent,
            attendance_rate=round(attendance_rate, 2),
            malpractice_incidents=len(incidents),
            generated_date=doc.generated_date,
        )
    
    async def get_exam_overview(
        self,
        tenant_id: str,
        exam_id: str,
    ) -> Dict[str, Any]:
        """Get comprehensive exam overview"""
        exam = await ExamScheduleDocument.find_one(
            ExamScheduleDocument.tenant_id == tenant_id,
            ExamScheduleDocument.exam_id == exam_id,
        )
        
        if not exam:
            raise ValueError("Exam not found")
        
        attendance = await ExamAttendanceDocument.find(
            ExamAttendanceDocument.tenant_id == tenant_id,
            ExamAttendanceDocument.exam_id == exam_id,
        ).to_list()
        
        invigilators = await InvigilationAssignmentDocument.find(
            InvigilationAssignmentDocument.tenant_id == tenant_id,
            InvigilationAssignmentDocument.exam_id == exam_id,
        ).to_list()
        
        incidents = await MalpracticeIncidentDocument.find(
            MalpracticeIncidentDocument.tenant_id == tenant_id,
            MalpracticeIncidentDocument.exam_id == exam_id,
        ).to_list()
        
        return {
            "exam_id": exam_id,
            "course": f"{exam.course_code} - {exam.course_title}",
            "exam_date": exam.exam_date,
            "venue": exam.venue,
            "status": exam.status,
            "enrolled_students": exam.enrolled_students,
            "attendance_summary": {
                "total": len(attendance),
                "attended": len([a for a in attendance if a.attendance_status == "attended"]),
                "absent": len([a for a in attendance if a.attendance_status == "absent"]),
            },
            "invigilators_count": len(invigilators),
            "invigilators": [
                {"name": i.staff_name, "role": i.role, "section": i.venue_section}
                for i in invigilators
            ],
            "malpractice_incidents": len(incidents),
            "incidents": [i.dict() for i in incidents],
        }
