"""Section 46: Hostel Admin Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import get_current_user

router = APIRouter()

class HostelDashboardResponse(BaseModel):
    total_beds: int
    occupied_beds: int
    occupancy_rate: float
    pending_requests: int
    maintenance_issues: int

@router.get("/officer/dashboard/hostel", response_model=HostelDashboardResponse, tags=["hostel-dashboard"])
async def get_hostel_dashboard(current_user = Depends(get_current_user)):
    if current_user.get("role") not in ["hostel_administrator", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return HostelDashboardResponse(
        total_beds=400,
        occupied_beds=380,
        occupancy_rate=95.0,
        pending_requests=12,
        maintenance_issues=3
    )
