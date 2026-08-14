"""
Course Coordinator Dashboard Service
Item 43: Course-level coordination and oversight

Course Coordinator responsibilities:
- Oversee assigned course(s)
- Manage course staff and tutors
- Monitor course students
- Track attendance and grades
- Manage course resources and materials
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class CourseStatus(str, Enum):
    """Course operational status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


# ==================== MODELS ====================

class CoordinatedCourse(BaseModel):
    """Course coordinated by staff member"""
    course_id: str
    course_code: str
    course_title: str
    department_id: str
    semester: int
    academic_year: int
    coordinator_id: str
    lecturer_id: str
    tutors: List[str] = Field(default_factory=list)
    total_students: int
    units: int
    status: CourseStatus


class CourseResourceAllocation(BaseModel):
    """Resources allocated to course"""
    resource_id: str
    course_id: str
    resource_type: str  # textbook, lab_equipment, software, room
    quantity: int
    allocation_date: datetime
    allocated_by: str
    status: str = "active"


class CourseAttendanceMetrics(BaseModel):
    """Course attendance statistics"""
    course_id: str
    total_students: int
    average_attendance: float  # 0-100%
    attendance_by_week: List[Dict[str, Any]] = Field(default_factory=list)
    students_with_low_attendance: List[str] = Field(default_factory=list)


class CoursePerformanceReview(BaseModel):
    """Course performance evaluation"""
    review_id: str
    course_id: str
    review_date: datetime
    reviewed_by: str
    average_gpa: float
    pass_rate: float
    student_feedback_score: float  # 0-5
    instructor_effectiveness: str  # excellent, good, satisfactory, needs_improvement
    recommendations: List[str] = Field(default_factory=list)


class CourseAnnouncement(BaseModel):
    """Course announcements for students"""
    announcement_id: str
    course_id: str
    title: str
    content: str
    announced_by: str
    announced_date: datetime
    priority: str = "normal"  # low, normal, high, urgent
    expiry_date: Optional[datetime] = None


# ==================== DOCUMENTS ====================

class CoordinatedCourseDocument(Document):
    """Coordinated courses"""
    course_id: str = Indexed()
    tenant_id: str = Indexed()
    course_code: str
    course_title: str
    department_id: str = Indexed()
    semester: int
    academic_year: int
    coordinator_id: str = Indexed()
    lecturer_id: str
    tutors: List[str]
    total_students: int
    units: int
    status: str
    
    class Settings:
        collection = "coordinated_courses"


class CourseResourceDocument(Document):
    """Course resources"""
    resource_id: str = Indexed()
    tenant_id: str = Indexed()
    course_id: str = Indexed()
    resource_type: str
    quantity: int
    allocation_date: datetime
    allocated_by: str
    status: str
    
    class Settings:
        collection = "course_resources"


class CourseAttendanceMetricsDocument(Document):
    """Course attendance metrics"""
    metrics_id: str = Indexed()
    tenant_id: str = Indexed()
    course_id: str = Indexed()
    calculated_at: datetime = Indexed()
    total_students: int
    average_attendance: float
    attendance_by_week: List[Dict[str, Any]]
    students_with_low_attendance: List[str]
    
    class Settings:
        collection = "course_attendance_metrics"


class CoursePerformanceReviewDocument(Document):
    """Course performance reviews"""
    review_id: str = Indexed()
    tenant_id: str = Indexed()
    course_id: str = Indexed()
    review_date: datetime
    reviewed_by: str
    average_gpa: float
    pass_rate: float
    student_feedback_score: float
    instructor_effectiveness: str
    recommendations: List[str]
    
    class Settings:
        collection = "course_performance_reviews"


class CourseAnnouncementDocument(Document):
    """Course announcements"""
    announcement_id: str = Indexed()
    tenant_id: str = Indexed()
    course_id: str = Indexed()
    title: str
    content: str
    announced_by: str
    announced_date: datetime
    priority: str
    expiry_date: Optional[datetime] = None
    
    class Settings:
        collection = "course_announcements"


# ==================== SERVICE ====================

class CourseCoordinatorService:
    """Course Coordinator operations"""
    
    async def get_coordinated_courses(
        self,
        tenant_id: str,
        coordinator_id: str,
        academic_year: int,
    ) -> List[CoordinatedCourse]:
        """Get courses coordinated by staff member"""
        docs = await CoordinatedCourseDocument.find(
            CoordinatedCourseDocument.tenant_id == tenant_id,
            CoordinatedCourseDocument.coordinator_id == coordinator_id,
            CoordinatedCourseDocument.academic_year == academic_year,
        ).to_list()
        
        return [
            CoordinatedCourse(
                course_id=d.course_id,
                course_code=d.course_code,
                course_title=d.course_title,
                department_id=d.department_id,
                semester=d.semester,
                academic_year=d.academic_year,
                coordinator_id=d.coordinator_id,
                lecturer_id=d.lecturer_id,
                tutors=d.tutors,
                total_students=d.total_students,
                units=d.units,
                status=CourseStatus(d.status),
            )
            for d in docs
        ]
    
    async def allocate_course_resource(
        self,
        tenant_id: str,
        course_id: str,
        resource_type: str,
        quantity: int,
        allocated_by: str,
    ) -> CourseResourceAllocation:
        """Allocate resource to course"""
        resource_id = f"RES-{course_id}-{resource_type}-{datetime.utcnow().timestamp()}"
        
        doc = CourseResourceDocument(
            resource_id=resource_id,
            tenant_id=tenant_id,
            course_id=course_id,
            resource_type=resource_type,
            quantity=quantity,
            allocation_date=datetime.utcnow(),
            allocated_by=allocated_by,
            status="active",
        )
        
        await doc.insert()
        
        logger.info(
            f"Allocated {quantity} {resource_type} to course {course_id}"
        )
        
        return CourseResourceAllocation(
            resource_id=resource_id,
            course_id=course_id,
            resource_type=resource_type,
            quantity=quantity,
            allocation_date=doc.allocation_date,
            allocated_by=allocated_by,
            status=doc.status,
        )
    
    async def get_course_resources(
        self,
        tenant_id: str,
        course_id: str,
    ) -> List[CourseResourceAllocation]:
        """Get resources allocated to course"""
        docs = await CourseResourceDocument.find(
            CourseResourceDocument.tenant_id == tenant_id,
            CourseResourceDocument.course_id == course_id,
            CourseResourceDocument.status == "active",
        ).to_list()
        
        return [
            CourseResourceAllocation(
                resource_id=d.resource_id,
                course_id=d.course_id,
                resource_type=d.resource_type,
                quantity=d.quantity,
                allocation_date=d.allocation_date,
                allocated_by=d.allocated_by,
                status=d.status,
            )
            for d in docs
        ]
    
    async def calculate_attendance_metrics(
        self,
        tenant_id: str,
        course_id: str,
    ) -> CourseAttendanceMetrics:
        """Calculate course attendance metrics"""
        # Query attendance records from lecturer_service
        # NOTE: This would integrate with AttendanceRecordDocument
        # For now, returning placeholder with structure
        
        metrics = CourseAttendanceMetrics(
            course_id=course_id,
            total_students=0,
            average_attendance=85.5,
            attendance_by_week=[],
            students_with_low_attendance=[],
        )
        
        doc = CourseAttendanceMetricsDocument(
            metrics_id=f"ATT-METRICS-{course_id}-{datetime.utcnow().timestamp()}",
            tenant_id=tenant_id,
            course_id=course_id,
            calculated_at=datetime.utcnow(),
            **metrics.dict()
        )
        
        await doc.insert()
        
        return metrics
    
    async def submit_course_review(
        self,
        tenant_id: str,
        course_id: str,
        reviewer_email: str,
        average_gpa: float,
        pass_rate: float,
        student_feedback_score: float,
        instructor_effectiveness: str,
        recommendations: List[str],
    ) -> CoursePerformanceReview:
        """Submit course performance review"""
        review_id = f"REV-{course_id}-{datetime.utcnow().timestamp()}"
        
        doc = CoursePerformanceReviewDocument(
            review_id=review_id,
            tenant_id=tenant_id,
            course_id=course_id,
            review_date=datetime.utcnow(),
            reviewed_by=reviewer_email,
            average_gpa=average_gpa,
            pass_rate=pass_rate,
            student_feedback_score=student_feedback_score,
            instructor_effectiveness=instructor_effectiveness,
            recommendations=recommendations,
        )
        
        await doc.insert()
        
        logger.info(f"Submitted review for course {course_id}")
        
        return CoursePerformanceReview(
            review_id=review_id,
            course_id=course_id,
            review_date=doc.review_date,
            reviewed_by=reviewer_email,
            average_gpa=average_gpa,
            pass_rate=pass_rate,
            student_feedback_score=student_feedback_score,
            instructor_effectiveness=instructor_effectiveness,
            recommendations=recommendations,
        )
    
    async def post_announcement(
        self,
        tenant_id: str,
        course_id: str,
        title: str,
        content: str,
        posted_by: str,
        priority: str = "normal",
        expiry_days: Optional[int] = None,
    ) -> CourseAnnouncement:
        """Post announcement to course"""
        announcement_id = f"ANN-{course_id}-{datetime.utcnow().timestamp()}"
        expiry_date = None
        
        if expiry_days:
            from datetime import timedelta
            expiry_date = datetime.utcnow() + timedelta(days=expiry_days)
        
        doc = CourseAnnouncementDocument(
            announcement_id=announcement_id,
            tenant_id=tenant_id,
            course_id=course_id,
            title=title,
            content=content,
            announced_by=posted_by,
            announced_date=datetime.utcnow(),
            priority=priority,
            expiry_date=expiry_date,
        )
        
        await doc.insert()
        
        logger.info(f"Posted announcement to {course_id}: {title}")
        
        return CourseAnnouncement(
            announcement_id=announcement_id,
            course_id=course_id,
            title=title,
            content=content,
            announced_by=posted_by,
            announced_date=doc.announced_date,
            priority=priority,
            expiry_date=expiry_date,
        )
    
    async def get_course_announcements(
        self,
        tenant_id: str,
        course_id: str,
        limit: int = 20,
    ) -> List[CourseAnnouncement]:
        """Get active announcements for course"""
        now = datetime.utcnow()
        docs = await CourseAnnouncementDocument.find(
            CourseAnnouncementDocument.tenant_id == tenant_id,
            CourseAnnouncementDocument.course_id == course_id,
        ).sort([("announced_date", -1)]).limit(limit).to_list()
        
        return [
            CourseAnnouncement(
                announcement_id=d.announcement_id,
                course_id=d.course_id,
                title=d.title,
                content=d.content,
                announced_by=d.announced_by,
                announced_date=d.announced_date,
                priority=d.priority,
                expiry_date=d.expiry_date,
            )
            for d in docs
            if d.expiry_date is None or d.expiry_date > now
        ]
    
    async def get_course_overview(
        self,
        tenant_id: str,
        course_id: str,
        coordinator_id: str,
    ) -> Dict[str, Any]:
        """Get comprehensive course overview"""
        # Verify coordinator has access
        course = await CoordinatedCourseDocument.find_one(
            CoordinatedCourseDocument.tenant_id == tenant_id,
            CoordinatedCourseDocument.course_id == course_id,
            CoordinatedCourseDocument.coordinator_id == coordinator_id,
        )
        
        if not course:
            raise ValueError("Access denied: Not course coordinator")
        
        resources = await self.get_course_resources(tenant_id, course_id)
        attendance = await self.calculate_attendance_metrics(tenant_id, course_id)
        announcements = await self.get_course_announcements(tenant_id, course_id, limit=5)
        
        return {
            "course_id": course_id,
            "course_code": course.course_code,
            "course_title": course.course_title,
            "total_students": course.total_students,
            "lecturer": course.lecturer_id,
            "tutors": course.tutors,
            "resources": [r.dict() for r in resources],
            "attendance_metrics": attendance.dict(),
            "recent_announcements": [a.dict() for a in announcements],
        }
