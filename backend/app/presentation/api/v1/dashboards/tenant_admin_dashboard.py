"""Section 51: Tenant Admin Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import get_current_user

router = APIRouter()

class TenantAdminDashboardResponse(BaseModel):
    total_users: int
    active_users: int
    system_health: float
    pending_approvals: int
    data_usage_gb: float

@router.get("/officer/dashboard/tenant-admin", response_model=TenantAdminDashboardResponse, tags=["tenant-admin-dashboard"])
async def get_tenant_admin_dashboard(current_user = Depends(get_current_user)):
    if current_user.get("role") not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return TenantAdminDashboardResponse(
        total_users=450,
        active_users=380,
        system_health=98.5,
        pending_approvals=6,
        data_usage_gb=85.3
    )
