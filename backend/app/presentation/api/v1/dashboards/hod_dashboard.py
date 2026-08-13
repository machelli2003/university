"""Section 43: HOD Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from app.dependencies import get_current_user

router = APIRouter()

class HODDashboardResponse(BaseModel):
    total_courses: int
    total_lecturers: int
    total_students: int
    avg_course_satisfaction: float
    pending_approvals: int

@router.get("/officer/dashboard/hod", response_model=HODDashboardResponse, tags=["hod-dashboard"])
async def get_hod_dashboard(current_user = Depends(get_current_user)):
    if current_user.get("role") not in ["head_of_department", "dean", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return HODDashboardResponse(
        total_courses=15,
        total_lecturers=8,
        total_students=250,
        avg_course_satisfaction=4.2,
        pending_approvals=5
    )
