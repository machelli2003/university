"""Section 46: Hostel Admin Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
from app.dependencies import get_current_user
from app.infrastructure.models.user import User

router = APIRouter()

@router.get("/officer/dashboard/hostel", tags=["hostel-dashboard"])
async def get_hostel_dashboard(current_user: User = Depends(get_current_user)):
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role not in ["hostel_administrator", "hostel_admin", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return {
        "total_hostels": 4,
        "total_beds": 400,
        "occupied_beds": 340,
        "occupancy_rate": 85.0,
        "pending_requests": 12,
        "pending_maintenance": 5,
        "hostels": [
            {"hostel_id": "h-01", "hostel_name": "Nelson Mandela Hall", "total_beds": 100, "occupied_beds": 95},
            {"hostel_id": "h-02", "hostel_name": "Kwame Nkrumah Hall", "total_beds": 100, "occupied_beds": 82},
            {"hostel_id": "h-03", "hostel_name": "Kofi Annan Hall", "total_beds": 100, "occupied_beds": 88},
            {"hostel_id": "h-04", "hostel_name": "W.E.B. DuBois Hall", "total_beds": 100, "occupied_beds": 75},
        ],
        "maintenance_requests": [
            {"request_id": "MAINT-001", "hostel_name": "Nelson Mandela Hall", "issue": "Plumbing repair in Block A", "status": "pending", "submitted_date": "2026-08-15"},
            {"request_id": "MAINT-002", "hostel_name": "Kwame Nkrumah Hall", "issue": "Electrical socket replacement", "status": "in-progress", "submitted_date": "2026-08-16"},
            {"request_id": "MAINT-003", "hostel_name": "Kofi Annan Hall", "issue": "AC maintenance in room 204", "status": "completed", "submitted_date": "2026-08-14"},
        ],
        "bed_requests": [
            {"request_id": "REQ-001", "student_name": "Kofi Mensah", "hostel_preference": "Nelson Mandela Hall", "status": "pending"},
            {"request_id": "REQ-002", "student_name": "Ama Serwaa", "hostel_preference": "Kwame Nkrumah Hall", "status": "approved"},
            {"request_id": "REQ-003", "student_name": "Kwaku Addo", "hostel_preference": "Kofi Annan Hall", "status": "rejected"},
        ]
    }

