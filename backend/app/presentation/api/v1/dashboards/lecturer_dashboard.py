"""
Section 42: Lecturer Dashboard
Backend aggregation endpoints for lecturer role.

Aggregates:
- Assigned courses and students
- Class attendance summary
- Grades submission status
- Course materials management
- Student performance metrics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List
from datetime import datetime

from app.dependencies import get_current_user
from app.infrastructure.database.repositories import ApplicantRepository

router = APIRouter()

applicant_repo = ApplicantRepository()


class CourseInfo(BaseModel):
    course_id: str
    course_code: str
    course_name: str
    student_count: int
    attendance_rate: float
    grades_submitted: int
    assignment_pending: int


class StudentPerformance(BaseModel):
    student_id: str
    student_name: str
    course: str
    current_grade: str
    attendance: float
    assignment_count: int


class LecturerDashboardResponse(BaseModel):
    total_courses: int
    total_students: int
    avg_attendance_rate: float
    courses: List[CourseInfo]
    recent_grades: List[StudentPerformance]
    attendance_alerts: List[StudentPerformance]
    pending_assignments: int


@router.get(
    "/officer/dashboard/lecturer",
    response_model=LecturerDashboardResponse,
    tags=["lecturer-dashboard"],
    summary="Lecturer Dashboard Data"
)
async def get_lecturer_dashboard(current_user = Depends(get_current_user)):
    """
    Get comprehensive dashboard data for lecturer.
    
    Requires: role = 'lecturer'
    Shows courses, students, attendance, grades
    """
    
    if current_user.get("role") not in ["lecturer", "head_of_department", "dean"]:
        raise HTTPException(status_code=403, detail="Only lecturers can access this")
    
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")
    
    try:
        # Placeholder data - in production, query actual course/grade data
        return LecturerDashboardResponse(
            total_courses=5,
            total_students=150,
            avg_attendance_rate=87.5,
            courses=[
                CourseInfo(
                    course_id="cs101",
                    course_code="CS 101",
                    course_name="Programming Fundamentals",
                    student_count=45,
                    attendance_rate=92.0,
                    grades_submitted=40,
                    assignment_pending=5
                ),
                CourseInfo(
                    course_id="cs201",
                    course_code="CS 201",
                    course_name="Data Structures",
                    student_count=42,
                    attendance_rate=85.0,
                    grades_submitted=30,
                    assignment_pending=12
                )
            ],
            recent_grades=[],
            attendance_alerts=[],
            pending_assignments=17
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard: {str(e)}")
