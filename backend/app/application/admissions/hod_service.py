"""
HOD Dashboard Service
Item 44: Head of Department operations

HOD responsibilities:
- Manage department staff and assignments
- Oversee department programmes
- Review course offerings
- Monitor student performance
- Manage department budgets and resources
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class StaffRole(str, Enum):
    """Staff roles in department"""
    LECTURER = "lecturer"
    SENIOR_LECTURER = "senior_lecturer"
    ASSOCIATE_PROFESSOR = "associate_professor"
    PROFESSOR = "professor"
    ASSISTANT = "assistant"


class DepartmentStatus(str, Enum):
    """Department operational status"""
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    INACTIVE = "inactive"


# ==================== MODELS ====================

class DepartmentStaffAssignment(BaseModel):
    """Staff member in department"""
    staff_id: str
    staff_name: str
    staff_email: str
    role: StaffRole
    department_id: str
    qualification: str
    assigned_date: datetime
    is_active: bool = True
    courses_teaching: List[str] = Field(default_factory=list)


class DepartmentProgramme(BaseModel):
    """Academic programme in department"""
    programme_id: str
    programme_name: str
    programme_code: str
    department_id: str
    level: str  # "undergraduate", "postgraduate"
    duration_years: int
    total_units_required: int
    programme_coordinator_id: str
    students_enrolled: int
    status: str = "active"


class DepartmentCourseOffering(BaseModel):
    """Course offering details"""
    course_id: str
    course_code: str
    course_title: str
    department_id: str
    programme_ids: List[str]  # Programmes offering this course
    lecturer_id: str
    lecturer_name: str
    semester: int
    academic_year: int
    student_count: int
    units: int
    status: str  # offered, cancelled


class DepartmentPerformanceMetrics(BaseModel):
    """Department performance indicators"""
    department_id: str
    total_staff: int
    total_students: int
    average_gpa: float
    pass_rate: float  # percentage
    graduation_rate: float  # percentage
    student_satisfaction: float  # 0-5 scale
    research_publications: int
    total_courses: int
    avg_class_size: float


class DepartmentMeeting(BaseModel):
    """Department meeting records"""
    meeting_id: str
    department_id: str
    meeting_date: datetime
    chaired_by: str
    topics: List[str]
    attendees: List[str]
    minutes: Optional[str] = None
    action_items: List[Dict[str, Any]] = Field(default_factory=list)


# ==================== DOCUMENTS ====================

class DepartmentStaffDocument(Document):
    """Department staff records"""
    staff_id: str = Indexed()
    tenant_id: str = Indexed()
    staff_name: str
    staff_email: str = Indexed()
    role: str
    department_id: str = Indexed()
    qualification: str
    assigned_date: datetime
    is_active: bool
    courses_teaching: List[str]
    
    class Settings:
        collection = "department_staff"


class DepartmentProgrammeDocument(Document):
    """Department programmes"""
    programme_id: str = Indexed()
    tenant_id: str = Indexed()
    programme_name: str
    programme_code: str
    department_id: str = Indexed()
    level: str
    duration_years: int
    total_units_required: int
    programme_coordinator_id: str
    students_enrolled: int
    status: str
    
    class Settings:
        collection = "department_programmes"


class DepartmentCourseDocument(Document):
    """Department course offerings"""
    course_id: str = Indexed()
    tenant_id: str = Indexed()
    course_code: str
    course_title: str
    department_id: str = Indexed()
    programme_ids: List[str]
    lecturer_id: str
    lecturer_name: str
    semester: int
    academic_year: int
    student_count: int
    units: int
    status: str
    
    class Settings:
        collection = "department_courses"


class DepartmentMetricsDocument(Document):
    """Department performance metrics"""
    metrics_id: str = Indexed()
    tenant_id: str = Indexed()
    department_id: str = Indexed()
    calculated_at: datetime = Indexed()
    total_staff: int
    total_students: int
    average_gpa: float
    pass_rate: float
    graduation_rate: float
    student_satisfaction: float
    research_publications: int
    total_courses: int
    avg_class_size: float
    
    class Settings:
        collection = "department_metrics"


class DepartmentMeetingDocument(Document):
    """Department meeting records"""
    meeting_id: str = Indexed()
    tenant_id: str = Indexed()
    department_id: str = Indexed()
    meeting_date: datetime
    chaired_by: str
    topics: List[str]
    attendees: List[str]
    minutes: Optional[str] = None
    action_items: List[Dict[str, Any]]
    
    class Settings:
        collection = "department_meetings"


# ==================== SERVICE ====================

class HODService:
    """Head of Department operations"""
    
    async def get_department_staff(
        self,
        tenant_id: str,
        department_id: str,
    ) -> List[DepartmentStaffAssignment]:
        """Get all staff in department"""
        docs = await DepartmentStaffDocument.find(
            DepartmentStaffDocument.tenant_id == tenant_id,
            DepartmentStaffDocument.department_id == department_id,
            DepartmentStaffDocument.is_active == True,
        ).to_list()
        
        return [
            DepartmentStaffAssignment(
                staff_id=d.staff_id,
                staff_name=d.staff_name,
                staff_email=d.staff_email,
                role=StaffRole(d.role),
                department_id=d.department_id,
                qualification=d.qualification,
                assigned_date=d.assigned_date,
                is_active=d.is_active,
                courses_teaching=d.courses_teaching,
            )
            for d in docs
        ]
    
    async def assign_lecturer_to_course(
        self,
        tenant_id: str,
        department_id: str,
        lecturer_id: str,
        course_id: str,
        hod_email: str,
    ) -> Dict[str, Any]:
        """Assign lecturer to teach course"""
        # Verify lecturer exists in department
        staff = await DepartmentStaffDocument.find_one(
            DepartmentStaffDocument.tenant_id == tenant_id,
            DepartmentStaffDocument.department_id == department_id,
            DepartmentStaffDocument.staff_id == lecturer_id,
        )
        
        if not staff:
            raise ValueError("Lecturer not found in department")
        
        # Add course to lecturer's teaching list
        if course_id not in staff.courses_teaching:
            staff.courses_teaching.append(course_id)
            await staff.save()
        
        logger.info(
            f"HOD {hod_email} assigned {lecturer_id} to course {course_id}"
        )
        
        return {
            "lecturer_id": lecturer_id,
            "course_id": course_id,
            "assigned_at": datetime.utcnow(),
            "message": "Lecturer assigned to course",
        }
    
    async def get_department_programmes(
        self,
        tenant_id: str,
        department_id: str,
    ) -> List[DepartmentProgramme]:
        """Get programmes offered by department"""
        docs = await DepartmentProgrammeDocument.find(
            DepartmentProgrammeDocument.tenant_id == tenant_id,
            DepartmentProgrammeDocument.department_id == department_id,
        ).to_list()
        
        return [
            DepartmentProgramme(
                programme_id=d.programme_id,
                programme_name=d.programme_name,
                programme_code=d.programme_code,
                department_id=d.department_id,
                level=d.level,
                duration_years=d.duration_years,
                total_units_required=d.total_units_required,
                programme_coordinator_id=d.programme_coordinator_id,
                students_enrolled=d.students_enrolled,
                status=d.status,
            )
            for d in docs
        ]
    
    async def get_department_course_offerings(
        self,
        tenant_id: str,
        department_id: str,
        academic_year: int,
        semester: Optional[int] = None,
    ) -> List[DepartmentCourseOffering]:
        """Get course offerings for department"""
        query = [
            DepartmentCourseDocument.tenant_id == tenant_id,
            DepartmentCourseDocument.department_id == department_id,
            DepartmentCourseDocument.academic_year == academic_year,
        ]
        
        if semester:
            query.append(DepartmentCourseDocument.semester == semester)
        
        docs = await DepartmentCourseDocument.find(*query).to_list()
        
        return [
            DepartmentCourseOffering(
                course_id=d.course_id,
                course_code=d.course_code,
                course_title=d.course_title,
                department_id=d.department_id,
                programme_ids=d.programme_ids,
                lecturer_id=d.lecturer_id,
                lecturer_name=d.lecturer_name,
                semester=d.semester,
                academic_year=d.academic_year,
                student_count=d.student_count,
                units=d.units,
                status=d.status,
            )
            for d in docs
        ]
    
    async def get_department_students(
        self,
        tenant_id: str,
        department_id: str,
    ) -> Dict[str, Any]:
        """Get student enrollment statistics"""
        # Query programmes to get enrolled students
        programmes = await self.get_department_programmes(tenant_id, department_id)
        total_students = sum(p.students_enrolled for p in programmes)
        
        return {
            "department_id": department_id,
            "total_students": total_students,
            "programmes": len(programmes),
            "by_programme": [
                {
                    "programme_id": p.programme_id,
                    "programme_name": p.programme_name,
                    "students_enrolled": p.students_enrolled,
                }
                for p in programmes
            ]
        }
    
    async def calculate_department_metrics(
        self,
        tenant_id: str,
        department_id: str,
    ) -> DepartmentPerformanceMetrics:
        """Calculate department performance metrics"""
        staff = await self.get_department_staff(tenant_id, department_id)
        students_data = await self.get_department_students(tenant_id, department_id)
        programmes = await self.get_department_programmes(tenant_id, department_id)
        courses = await self.get_department_course_offerings(
            tenant_id, department_id, datetime.utcnow().year
        )
        
        # Calculate metrics
        total_staff = len(staff)
        total_students = students_data["total_students"]
        total_courses = len(courses)
        avg_class_size = (
            (total_students / total_courses)
            if total_courses > 0
            else 0
        )
        
        # Placeholder values for CGPA, pass rate, graduation rate
        # These would be calculated from actual grade data
        average_gpa = 3.45
        pass_rate = 85.5
        graduation_rate = 92.0
        student_satisfaction = 4.2
        research_publications = 12
        
        metrics = DepartmentPerformanceMetrics(
            department_id=department_id,
            total_staff=total_staff,
            total_students=total_students,
            average_gpa=average_gpa,
            pass_rate=pass_rate,
            graduation_rate=graduation_rate,
            student_satisfaction=student_satisfaction,
            research_publications=research_publications,
            total_courses=total_courses,
            avg_class_size=round(avg_class_size, 2),
        )
        
        # Store metrics
        doc = DepartmentMetricsDocument(
            metrics_id=f"DEPT-METRICS-{department_id}-{datetime.utcnow().timestamp()}",
            tenant_id=tenant_id,
            department_id=department_id,
            calculated_at=datetime.utcnow(),
            **metrics.dict()
        )
        
        await doc.insert()
        
        logger.info(
            f"Calculated metrics for {department_id}: "
            f"{total_staff} staff, {total_students} students, {pass_rate}% pass rate"
        )
        
        return metrics
    
    async def record_department_meeting(
        self,
        tenant_id: str,
        department_id: str,
        hod_email: str,
        meeting_date: datetime,
        topics: List[str],
        attendees: List[str],
        minutes: Optional[str] = None,
        action_items: Optional[List[Dict[str, Any]]] = None,
    ) -> DepartmentMeeting:
        """Record department meeting"""
        meeting_id = f"MTG-{department_id}-{datetime.utcnow().timestamp()}"
        
        doc = DepartmentMeetingDocument(
            meeting_id=meeting_id,
            tenant_id=tenant_id,
            department_id=department_id,
            meeting_date=meeting_date,
            chaired_by=hod_email,
            topics=topics,
            attendees=attendees,
            minutes=minutes,
            action_items=action_items or [],
        )
        
        await doc.insert()
        
        logger.info(f"Recorded meeting {meeting_id} for {department_id}")
        
        return DepartmentMeeting(
            meeting_id=meeting_id,
            department_id=department_id,
            meeting_date=meeting_date,
            chaired_by=hod_email,
            topics=topics,
            attendees=attendees,
            minutes=minutes,
            action_items=action_items or [],
        )
    
    async def get_department_meeting_history(
        self,
        tenant_id: str,
        department_id: str,
        limit: int = 20,
    ) -> List[DepartmentMeeting]:
        """Get recent department meetings"""
        docs = await DepartmentMeetingDocument.find(
            DepartmentMeetingDocument.tenant_id == tenant_id,
            DepartmentMeetingDocument.department_id == department_id,
        ).sort([("meeting_date", -1)]).limit(limit).to_list()
        
        return [
            DepartmentMeeting(
                meeting_id=d.meeting_id,
                department_id=d.department_id,
                meeting_date=d.meeting_date,
                chaired_by=d.chaired_by,
                topics=d.topics,
                attendees=d.attendees,
                minutes=d.minutes,
                action_items=d.action_items,
            )
            for d in docs
        ]
    
    async def get_department_overview(
        self,
        tenant_id: str,
        department_id: str,
    ) -> Dict[str, Any]:
        """Get comprehensive department overview"""
        staff = await self.get_department_staff(tenant_id, department_id)
        students_data = await self.get_department_students(tenant_id, department_id)
        programmes = await self.get_department_programmes(tenant_id, department_id)
        metrics = await self.calculate_department_metrics(tenant_id, department_id)
        recent_meetings = await self.get_department_meeting_history(
            tenant_id, department_id, limit=5
        )
        
        return {
            "department_id": department_id,
            "staff_count": len(staff),
            "total_students": students_data["total_students"],
            "programmes_count": len(programmes),
            "metrics": metrics.dict(),
            "recent_meetings": [m.dict() for m in recent_meetings],
            "staff_by_role": {
                role: len([s for s in staff if s.role == role])
                for role in [r.value for r in StaffRole]
            }
        }
