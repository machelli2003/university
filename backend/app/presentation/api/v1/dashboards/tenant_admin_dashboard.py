"""Section 51: Tenant Admin Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
from app.dependencies import get_current_user
from app.infrastructure.models.user import User

router = APIRouter()

@router.get("/officer/dashboard/tenant-admin", tags=["tenant-admin-dashboard"])
@router.get("/officer/dashboard/tenant_admin", tags=["tenant-admin-dashboard"])
@router.get("/admin/dashboard/tenant", tags=["tenant-admin-dashboard"])
async def get_tenant_admin_dashboard(current_user: User = Depends(get_current_user)):
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role not in ["tenant_admin", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return {
        "total_users": 450,
        "active_users": 420,
        "system_health": 99.5,
        "pending_approvals": 6,
        "data_usage_gb": 85.3,
        "users": [
            {"user_id": "USR-001", "name": "Dr. Emmanuel Mensah", "email": "e.mensah@university.edu", "role": "head_of_department", "status": "active"},
            {"user_id": "USR-002", "name": "Prof. Sarah Adjei", "email": "s.adjei@university.edu", "role": "dean", "status": "active"},
            {"user_id": "USR-003", "name": "Grace Quaye", "email": "g.quaye@university.edu", "role": "finance_officer", "status": "active"},
        ],
        "pending_requests": [
            {"approval_id": "APP-001", "request_type": "Course Syllabus Update", "requester_name": "Dr. Emmanuel Mensah", "submitted_date": "2026-08-14"},
            {"approval_id": "APP-002", "request_type": "New Staff Account", "requester_name": "HR Department", "submitted_date": "2026-08-15"},
        ]
    }

