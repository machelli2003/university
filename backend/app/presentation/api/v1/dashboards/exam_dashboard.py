"""Section 48: Exam Officer Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import get_current_user

router = APIRouter()

class ExamDashboardResponse(BaseModel):
    total_exams: int
    scheduled_exams: int
    completed_exams: int
    pending_results: int
    verification_rate: float

@router.get("/officer/dashboard/exam", response_model=ExamDashboardResponse, tags=["exam-dashboard"])
async def get_exam_dashboard(current_user = Depends(get_current_user)):
    if current_user.get("role") not in ["exam_officer", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return ExamDashboardResponse(
        total_exams=125,
        scheduled_exams=12,
        completed_exams=108,
        pending_results=5,
        verification_rate=98.5
    )
