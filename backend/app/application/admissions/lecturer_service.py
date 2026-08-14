"""
Lecturer Workspace Service
Item 42: Course management, student attendance, grade submission

Lecturer responsibilities:
- Manage assigned courses
- Track student attendance
- Submit course grades
- Generate performance reports
- Provide student support
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class AttendanceStatus(str, Enum):
    """Student attendance status"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class GradeStatus(str, Enum):
    """Course grade status"""
    NOT_GRADED = "not_graded"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"


# ==================== MODELS ====================

class LecturerAssignment(BaseModel):
    """Lecturer assignment to course"""
    lecturer_id: str
    course_id: str
    course_code: str
    course_title: str
    department_id: str
    semester: int
    academic_year: int
    student_count: int
    assigned_date: datetime


class AttendanceRecord(BaseModel):
    """Student attendance record"""
    attendance_id: str
    course_id: str
    student_id: str
    date: datetime
    status: AttendanceStatus
    recorded_by: str
    notes: Optional[str] = None


class CourseGrade(BaseModel):
    """Student grade in course"""
    grade_id: str
    course_id: str
    student_id: str
    continuous_assessment: float = Field(..., ge=0.0, le=100.0)
    exam_score: float = Field(..., ge=0.0, le=100.0)
    final_grade: float = Field(..., ge=0.0, le=100.0)
    letter_grade: str  # A, B, C, D, F
    gpa_points: float = Field(..., ge=0.0, le=5.0)
    submitted_by: str
    submitted_date: datetime
    status: GradeStatus = GradeStatus.NOT_GRADED


class CoursePerformanceStats(BaseModel):
    """Course performance statistics"""
    course_id: str
    total_students: int
    attendance_rate: float  # 0-100%
    average_grade: float
    grade_distribution: Dict[str, int]  # {"A": 5, "B": 10, ...}
    highest_score: float
    lowest_score: float
    pass_rate: float  # percentage


# ==================== DOCUMENTS ====================

class LecturerAssignmentDocument(Document):
    """Lecturer course assignment"""
    lecturer_id: str = Indexed()
    tenant_id: str = Indexed()
    course_id: str = Indexed()
    course_code: str
    course_title: str
    department_id: str = Indexed()
    semester: int
    academic_year: int
    student_count: int
    assigned_date: datetime
    
    class Settings:
        collection = "lecturer_assignments"


class AttendanceRecordDocument(Document):
    """Attendance records per student per class"""
    attendance_id: str = Indexed()
    tenant_id: str = Indexed()
    course_id: str = Indexed()
    student_id: str = Indexed()
    date: datetime = Indexed()
    status: str  # present, absent, late, excused
    recorded_by: str
    notes: Optional[str] = None
    
    class Settings:
        collection = "attendance_records"


class CourseGradeDocument(Document):
    """Student grades per course"""
    grade_id: str = Indexed()
    tenant_id: str = Indexed()
    course_id: str = Indexed()
    student_id: str = Indexed()
    continuous_assessment: float
    exam_score: float
    final_grade: float
    letter_grade: str
    gpa_points: float
    submitted_by: str
    submitted_date: datetime
    status: str
    
    class Settings:
        collection = "course_grades"


class CoursePerformanceDocument(Document):
    """Aggregate course performance data"""
    performance_id: str = Indexed()
    tenant_id: str = Indexed()
    course_id: str = Indexed()
    total_students: int
    attendance_rate: float
    average_grade: float
    grade_distribution: Dict[str, int]
    highest_score: float
    lowest_score: float
    pass_rate: float
    calculated_at: datetime = Indexed()
    
    class Settings:
        collection = "course_performance"


# ==================== SERVICE ====================

class LecturerService:
    """Lecturer workspace operations"""
    
    async def get_my_courses(
        self,
        tenant_id: str,
        lecturer_id: str,
        academic_year: int,
    ) -> List[LecturerAssignment]:
        """Get courses assigned to lecturer"""
        docs = await LecturerAssignmentDocument.find(
            LecturerAssignmentDocument.tenant_id == tenant_id,
            LecturerAssignmentDocument.lecturer_id == lecturer_id,
            LecturerAssignmentDocument.academic_year == academic_year,
        ).to_list()
        
        return [
            LecturerAssignment(
                lecturer_id=d.lecturer_id,
                course_id=d.course_id,
                course_code=d.course_code,
                course_title=d.course_title,
                department_id=d.department_id,
                semester=d.semester,
                academic_year=d.academic_year,
                student_count=d.student_count,
                assigned_date=d.assigned_date,
            )
            for d in docs
        ]
    
    async def get_course_students(
        self,
        tenant_id: str,
        course_id: str,
        lecturer_id: str,
    ) -> List[Dict[str, Any]]:
        """Get enrolled students in lecturer's course"""
        # Verify lecturer has access to this course
        assignment = await LecturerAssignmentDocument.find_one(
            LecturerAssignmentDocument.tenant_id == tenant_id,
            LecturerAssignmentDocument.lecturer_id == lecturer_id,
            LecturerAssignmentDocument.course_id == course_id,
        )
        
        if not assignment:
            raise ValueError("Access denied: Not assigned to this course")
        
        # Query course enrollments
        # NOTE: This assumes CourseEnrollmentDocument exists in your app
        # Adjust query to match your actual schema
        logger.info(f"Retrieved students for course {course_id}")
        
        return []  # Return from CourseEnrollmentDocument query
    
    async def record_attendance(
        self,
        tenant_id: str,
        course_id: str,
        lecturer_id: str,
        attendance_data: List[Dict[str, Any]],  # [{student_id, status, date, notes}]
    ) -> List[AttendanceRecord]:
        """Record student attendance"""
        # Verify lecturer assigned to course
        assignment = await LecturerAssignmentDocument.find_one(
            LecturerAssignmentDocument.tenant_id == tenant_id,
            LecturerAssignmentDocument.lecturer_id == lecturer_id,
            LecturerAssignmentDocument.course_id == course_id,
        )
        
        if not assignment:
            raise ValueError("Access denied: Not assigned to this course")
        
        records = []
        for data in attendance_data:
            attendance_id = f"ATT-{course_id}-{data['student_id']}-{datetime.utcnow().timestamp()}"
            
            doc = AttendanceRecordDocument(
                attendance_id=attendance_id,
                tenant_id=tenant_id,
                course_id=course_id,
                student_id=data["student_id"],
                date=data.get("date", datetime.utcnow()),
                status=data["status"],
                recorded_by=lecturer_id,
                notes=data.get("notes"),
            )
            
            await doc.insert()
            
            records.append(
                AttendanceRecord(
                    attendance_id=attendance_id,
                    course_id=course_id,
                    student_id=data["student_id"],
                    date=doc.date,
                    status=AttendanceStatus(data["status"]),
                    recorded_by=lecturer_id,
                    notes=data.get("notes"),
                )
            )
        
        logger.info(f"Recorded {len(records)} attendance records for {course_id}")
        
        return records
    
    async def get_course_attendance_summary(
        self,
        tenant_id: str,
        course_id: str,
    ) -> Dict[str, Any]:
        """Get attendance summary for course"""
        records = await AttendanceRecordDocument.find(
            AttendanceRecordDocument.tenant_id == tenant_id,
            AttendanceRecordDocument.course_id == course_id,
        ).to_list()
        
        # Calculate statistics
        total_records = len(records)
        present_count = len([r for r in records if r.status == AttendanceStatus.PRESENT.value])
        absent_count = len([r for r in records if r.status == AttendanceStatus.ABSENT.value])
        
        attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
        
        return {
            "course_id": course_id,
            "total_attendance_records": total_records,
            "present": present_count,
            "absent": absent_count,
            "attendance_rate": round(attendance_rate, 2),
        }
    
    async def submit_grades(
        self,
        tenant_id: str,
        course_id: str,
        lecturer_id: str,
        grades: List[Dict[str, Any]],  # [{student_id, ca, exam_score}]
    ) -> List[CourseGrade]:
        """Submit course grades"""
        # Verify lecturer assigned to course
        assignment = await LecturerAssignmentDocument.find_one(
            LecturerAssignmentDocument.tenant_id == tenant_id,
            LecturerAssignmentDocument.lecturer_id == lecturer_id,
            LecturerAssignmentDocument.course_id == course_id,
        )
        
        if not assignment:
            raise ValueError("Access denied: Not assigned to this course")
        
        submitted_grades = []
        for grade_data in grades:
            ca = grade_data["ca"]
            exam = grade_data["exam_score"]
            
            # Calculate final grade (typical: CA 40%, Exam 60%)
            final_grade = (ca * 0.4) + (exam * 0.6)
            
            # Letter grade conversion
            if final_grade >= 70:
                letter_grade = "A"
                gpa = 5.0
            elif final_grade >= 60:
                letter_grade = "B"
                gpa = 4.0
            elif final_grade >= 50:
                letter_grade = "C"
                gpa = 3.0
            elif final_grade >= 40:
                letter_grade = "D"
                gpa = 2.0
            else:
                letter_grade = "F"
                gpa = 0.0
            
            grade_id = f"GRD-{course_id}-{grade_data['student_id']}-{datetime.utcnow().timestamp()}"
            
            doc = CourseGradeDocument(
                grade_id=grade_id,
                tenant_id=tenant_id,
                course_id=course_id,
                student_id=grade_data["student_id"],
                continuous_assessment=ca,
                exam_score=exam,
                final_grade=final_grade,
                letter_grade=letter_grade,
                gpa_points=gpa,
                submitted_by=lecturer_id,
                submitted_date=datetime.utcnow(),
                status=GradeStatus.SUBMITTED.value,
            )
            
            await doc.insert()
            
            submitted_grades.append(
                CourseGrade(
                    grade_id=grade_id,
                    course_id=course_id,
                    student_id=grade_data["student_id"],
                    continuous_assessment=ca,
                    exam_score=exam,
                    final_grade=final_grade,
                    letter_grade=letter_grade,
                    gpa_points=gpa,
                    submitted_by=lecturer_id,
                    submitted_date=doc.submitted_date,
                    status=GradeStatus.SUBMITTED,
                )
            )
        
        logger.info(f"Submitted {len(submitted_grades)} grades for {course_id} by {lecturer_id}")
        
        return submitted_grades
    
    async def get_course_grades(
        self,
        tenant_id: str,
        course_id: str,
    ) -> List[CourseGrade]:
        """Get all grades for course"""
        docs = await CourseGradeDocument.find(
            CourseGradeDocument.tenant_id == tenant_id,
            CourseGradeDocument.course_id == course_id,
        ).to_list()
        
        return [CourseGrade(**d.dict()) for d in docs]
    
    async def get_student_grade(
        self,
        tenant_id: str,
        course_id: str,
        student_id: str,
    ) -> Optional[CourseGrade]:
        """Get student's grade in course"""
        doc = await CourseGradeDocument.find_one(
            CourseGradeDocument.tenant_id == tenant_id,
            CourseGradeDocument.course_id == course_id,
            CourseGradeDocument.student_id == student_id,
        )
        
        if not doc:
            return None
        
        return CourseGrade(**doc.dict())
    
    async def calculate_course_performance(
        self,
        tenant_id: str,
        course_id: str,
    ) -> CoursePerformanceStats:
        """Calculate performance statistics for course"""
        # Get grades
        grades = await self.get_course_grades(tenant_id, course_id)
        
        if not grades:
            return CoursePerformanceStats(
                course_id=course_id,
                total_students=0,
                attendance_rate=0,
                average_grade=0,
                grade_distribution={},
                highest_score=0,
                lowest_score=0,
                pass_rate=0,
            )
        
        # Calculate statistics
        final_grades = [g.final_grade for g in grades]
        letter_grades = [g.letter_grade for g in grades]
        
        average = sum(final_grades) / len(final_grades)
        highest = max(final_grades)
        lowest = min(final_grades)
        
        # Grade distribution
        distribution = {}
        for letter in ["A", "B", "C", "D", "F"]:
            distribution[letter] = sum(1 for g in grades if g.letter_grade == letter)
        
        # Pass rate (A, B, C, D = pass; F = fail)
        pass_count = sum(1 for g in grades if g.letter_grade != "F")
        pass_rate = (pass_count / len(grades) * 100) if grades else 0
        
        # Attendance rate
        attendance = await self.get_course_attendance_summary(tenant_id, course_id)
        attendance_rate = attendance.get("attendance_rate", 0)
        
        stats = CoursePerformanceStats(
            course_id=course_id,
            total_students=len(grades),
            attendance_rate=attendance_rate,
            average_grade=round(average, 2),
            grade_distribution=distribution,
            highest_score=highest,
            lowest_score=lowest,
            pass_rate=round(pass_rate, 2),
        )
        
        # Store stats
        perf_doc = CoursePerformanceDocument(
            performance_id=f"PERF-{course_id}-{datetime.utcnow().timestamp()}",
            tenant_id=tenant_id,
            course_id=course_id,
            **stats.dict()
        )
        
        await perf_doc.insert()
        
        logger.info(f"Calculated performance for {course_id}: {stats.pass_rate}% pass rate")
        
        return stats
    
    async def get_student_attendance_in_course(
        self,
        tenant_id: str,
        course_id: str,
        student_id: str,
    ) -> Dict[str, Any]:
        """Get student's attendance record in specific course"""
        records = await AttendanceRecordDocument.find(
            AttendanceRecordDocument.tenant_id == tenant_id,
            AttendanceRecordDocument.course_id == course_id,
            AttendanceRecordDocument.student_id == student_id,
        ).to_list()
        
        if not records:
            return {
                "student_id": student_id,
                "course_id": course_id,
                "attendance_rate": 0,
                "total_classes": 0,
                "present": 0,
                "absent": 0,
            }
        
        present = sum(1 for r in records if r.status == AttendanceStatus.PRESENT.value)
        absent = sum(1 for r in records if r.status == AttendanceStatus.ABSENT.value)
        attendance_rate = (present / len(records) * 100) if records else 0
        
        return {
            "student_id": student_id,
            "course_id": course_id,
            "total_classes": len(records),
            "present": present,
            "absent": absent,
            "attendance_rate": round(attendance_rate, 2),
            "records": [
                {
                    "date": r.date,
                    "status": r.status,
                    "notes": r.notes,
                }
                for r in sorted(records, key=lambda x: x.date)
            ]
        }
