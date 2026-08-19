"""Section 46: Hostel Admin Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
from app.dependencies import get_current_user
from app.infrastructure.models.user import User
from app.infrastructure.models.accommodation import Hall, Room, Accommodation, MaintenanceRequest
from app.infrastructure.models.student import Student

router = APIRouter()

@router.get("/officer/dashboard/hostel", tags=["hostel-dashboard"])
async def get_hostel_dashboard(current_user: User = Depends(get_current_user)):
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role not in ["hostel_administrator", "hostel_admin", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    tenant_id = current_user.tenant_id or "single-university"

    # Query Halls for tenant
    halls = await Hall.find({"tenant_id": tenant_id}).to_list()
    if not halls and (not current_user.tenant_id or current_user.tenant_id in ["default", "single-university"]):
        halls = await Hall.find({"is_active": True}).to_list()
        if not halls:
            halls = await Hall.find_all().to_list()

    # Query Rooms for tenant
    rooms = await Room.find({"tenant_id": tenant_id}).to_list()
    if not rooms:
        rooms = await Room.find_all().to_list()

    # Build Map of Rooms per Hall
    rooms_by_hall: Dict[str, List[Room]] = {}
    for r in rooms:
        rooms_by_hall.setdefault(r.hall_id, []).append(r)

    hostels_summary = []
    total_beds_sum = 0
    occupied_beds_sum = 0

    for hall in halls:
        hall_id_str = str(hall.id)
        hall_rooms = rooms_by_hall.get(hall_id_str, [])

        if hall_rooms:
            h_total = sum(r.capacity for r in hall_rooms)
            h_occupied = sum(r.occupied for r in hall_rooms)
        else:
            h_total = hall.capacity or 0
            h_occupied = 0

        total_beds_sum += h_total
        occupied_beds_sum += h_occupied

        hostels_summary.append({
            "hostel_id": hall_id_str,
            "hostel_name": hall.name,
            "total_beds": h_total,
            "occupied_beds": h_occupied,
        })

    # Query Maintenance Requests
    maint_query = {"tenant_id": tenant_id} if current_user.tenant_id else {}
    maint_docs = await MaintenanceRequest.find(maint_query).to_list()
    if not maint_docs:
        maint_docs = await MaintenanceRequest.find_all().to_list()

    halls_map = {str(h.id): h.name for h in halls}

    maintenance_requests_formatted = []
    pending_maint_count = 0

    for m in maint_docs:
        status_val = (m.status or "pending").lower()
        if status_val in ["pending", "in-progress", "open"]:
            pending_maint_count += 1

        hostel_name = halls_map.get(m.hall_id, "Main Campus Hostel")
        maintenance_requests_formatted.append({
            "request_id": str(m.id),
            "hostel_name": hostel_name,
            "issue": m.issue_description or "General Maintenance",
            "status": status_val,
            "submitted_date": m.created_date.strftime("%Y-%m-%d") if getattr(m, "created_date", None) else "",
        })

    # Query Accommodations / Bed Requests
    accom_query = {"tenant_id": tenant_id} if current_user.tenant_id else {}
    accom_docs = await Accommodation.find(accom_query).to_list()
    if not accom_docs:
        accom_docs = await Accommodation.find_all().to_list()

    student_ids = [a.student_id for a in accom_docs if getattr(a, "student_id", None)]
    students_map = {}
    if student_ids:
        try:
            st_docs = await Student.find({"_id": {"$in": student_ids}}).to_list()
            for s in st_docs:
                students_map[str(s.id)] = f"{s.first_name} {s.last_name}" if getattr(s, "first_name", None) else (s.student_id or str(s.id))
        except Exception:
            pass

    bed_requests_formatted = []
    for a in accom_docs:
        student_name = students_map.get(a.student_id, f"Student ({a.student_id[:6] if a.student_id else 'N/A'})")
        pref_name = halls_map.get(a.hall_id, a.outside_hostel_name or "Campus Accommodation")
        status_str = "approved" if getattr(a, "is_active", True) else "pending"

        bed_requests_formatted.append({
            "request_id": str(a.id),
            "student_name": student_name,
            "hostel_preference": pref_name,
            "status": status_str,
        })

    occupancy_rate = (occupied_beds_sum / total_beds_sum * 100.0) if total_beds_sum > 0 else 0.0

    return {
        "total_hostels": len(halls),
        "total_beds": total_beds_sum,
        "occupied_beds": occupied_beds_sum,
        "occupancy_rate": round(occupancy_rate, 1),
        "pending_requests": len(bed_requests_formatted),
        "pending_maintenance": pending_maint_count,
        "hostels": hostels_summary,
        "maintenance_requests": maintenance_requests_formatted,
        "bed_requests": bed_requests_formatted,
    }


