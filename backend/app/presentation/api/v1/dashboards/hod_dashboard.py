"""Section 43: HOD Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
from app.dependencies import get_current_user
from app.infrastructure.models.user import User

router = APIRouter()

@router.get("/officer/dashboard/hod", tags=["hod-dashboard"])
async def get_hod_dashboard(current_user: User = Depends(get_current_user)):
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role not in ["head_of_department", "dean", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return {
        "total_courses": 24,
        "total_lecturers": 15,
        "total_students": 450,
        "avg_course_satisfaction": 4.6,
        "pending_approvals": 3,
        "courses": [
            {"course_id": "CRS-001", "course_code": "CS101", "course_name": "Intro to Programming", "lecturer_name": "Dr. Emmanuel Mensah", "enrolled_students": 120},
            {"course_id": "CRS-002", "course_code": "CS202", "course_name": "Data Structures", "lecturer_name": "Prof. Sarah Adjei", "enrolled_students": 95},
        ],
        "staff": [
            {"staff_id": "STF-001", "staff_name": "Dr. Emmanuel Mensah", "position": "Senior Lecturer"},
            {"staff_id": "STF-002", "staff_name": "Prof. Sarah Adjei", "position": "Associate Professor"},
        ],
        "students_by_level": [
            {"level": "Level 100", "count": 140},
            {"level": "Level 200", "count": 110},
            {"level": "Level 300", "count": 100},
            {"level": "Level 400", "count": 100},
        ]
    }
