"""Section 45: Exam Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
from app.dependencies import get_current_user
from app.infrastructure.models.user import User

router = APIRouter()

@router.get("/officer/dashboard/exam", tags=["exam-dashboard"])
async def get_exam_dashboard(current_user: User = Depends(get_current_user)):
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role not in ["exam_officer", "registrar", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return {
        "total_exams": 45,
        "scheduled_exams": 12,
        "completed_exams": 33,
        "pending_results": 5,
        "verification_rate": 92.5,
        "exams": [
            {"exam_id": "EXM-001", "course_code": "CS101", "course_name": "Intro to Programming", "exam_date": "2026-08-20", "status": "scheduled"},
            {"exam_id": "EXM-002", "course_code": "MATH201", "course_name": "Calculus II", "exam_date": "2026-08-10", "status": "completed"},
        ],
        "results_verification": [
            {"result_id": "RES-001", "course_code": "CS101", "verified": True, "verified_date": "2026-08-12"},
            {"result_id": "RES-002", "course_code": "MATH201", "verified": False, "verified_date": None},
        ]
    }
