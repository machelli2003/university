"""Section 44: Dean Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import get_current_user

router = APIRouter()

class DeanDashboardResponse(BaseModel):
    total_departments: int
    total_programmes: int
    total_students: int
    total_staff: int
    pending_decisions: int

@router.get("/officer/dashboard/dean", response_model=DeanDashboardResponse, tags=["dean-dashboard"])
async def get_dean_dashboard(current_user = Depends(get_current_user)):
    if current_user.get("role") not in ["dean", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return DeanDashboardResponse(
        total_departments=6,
        total_programmes=18,
        total_students=1200,
        total_staff=60,
        pending_decisions=8
    )
