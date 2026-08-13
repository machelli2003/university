"""Section 49: Student Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import get_current_user

router = APIRouter()

class StudentDashboardResponse(BaseModel):
    current_level: str
    enrolled_courses: int
    current_gpa: float
    academic_standing: str
    next_deadline: str

@router.get("/officer/dashboard/student", response_model=StudentDashboardResponse, tags=["student-dashboard"])
async def get_student_dashboard(current_user = Depends(get_current_user)):
    if current_user.get("role") not in ["student", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return StudentDashboardResponse(
        current_level="200",
        enrolled_courses=6,
        current_gpa=3.45,
        academic_standing="good",
        next_deadline="2026-09-15"
    )
