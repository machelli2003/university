"""Section 52: Super Admin Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import get_current_user

router = APIRouter()

class SuperAdminDashboardResponse(BaseModel):
    total_tenants: int
    active_tenants: int
    total_users_system_wide: int
    system_health: float
    total_data_gb: float

@router.get("/officer/dashboard/super-admin", response_model=SuperAdminDashboardResponse, tags=["super-admin-dashboard"])
async def get_super_admin_dashboard(current_user = Depends(get_current_user)):
    if current_user.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admin")
    return SuperAdminDashboardResponse(
        total_tenants=12,
        active_tenants=11,
        total_users_system_wide=4500,
        system_health=99.2,
        total_data_gb=520.8
    )
