"""Section 48: Student Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
from app.dependencies import get_current_user
from app.infrastructure.models.user import User

router = APIRouter()

@router.get("/officer/dashboard/student", tags=["student-dashboard"])
async def get_student_dashboard(current_user: User = Depends(get_current_user)):
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role not in ["student", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return {
        "student_level": "Level 300",
        "enrolled_courses": 6,
        "current_gpa": 3.75,
        "academic_standing": "First Class Honors",
        "next_important_date": "2026-08-25 (Mid-Semester Exams)",
        "courses": [
            {"course_code": "CS301", "course_name": "Database Systems", "lecturer_name": "Dr. Emmanuel Mensah", "credits": 3, "grade": "A"},
            {"course_code": "CS303", "course_name": "Software Engineering", "lecturer_name": "Prof. Sarah Adjei", "credits": 3, "grade": "A-"},
        ],
        "transcript": [
            {"course_code": "CS101", "grade": "A"},
            {"course_code": "CS102", "grade": "B+"},
            {"course_code": "CS201", "grade": "A"},
        ]
    }
