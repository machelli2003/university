"""Section 44: Dean Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
from app.dependencies import get_current_user
from app.infrastructure.models.user import User

router = APIRouter()

@router.get("/officer/dashboard/dean", tags=["dean-dashboard"])
async def get_dean_dashboard(current_user: User = Depends(get_current_user)):
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role not in ["dean", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return {
        "total_departments": 6,
        "total_programmes": 18,
        "total_students": 1200,
        "total_staff": 60,
        "pending_decisions": 8,
        "departments": [
            {"department_id": "DEP-01", "department_name": "Computer Science", "hod_name": "Dr. Emmanuel Mensah", "student_count": 350},
            {"department_id": "DEP-02", "department_name": "Electrical Engineering", "hod_name": "Dr. Samuel Kuffour", "student_count": 280},
            {"department_id": "DEP-03", "department_name": "Mathematics", "hod_name": "Dr. Agnes Appiah", "student_count": 220},
        ],
        "programmes": [
            {"programme_id": "PRG-01", "programme_code": "BSC-CS", "programme_name": "B.Sc. Computer Science", "enrolled_students": 250},
            {"programme_id": "PRG-02", "programme_code": "BSC-EE", "programme_name": "B.Sc. Electrical Engineering", "enrolled_students": 180},
        ],
        "department_performance": [
            {"department_name": "Computer Science", "avg_gpa": 3.42},
            {"department_name": "Electrical Engineering", "avg_gpa": 3.28},
            {"department_name": "Mathematics", "avg_gpa": 3.15},
        ]
    }

