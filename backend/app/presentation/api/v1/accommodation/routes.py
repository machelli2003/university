from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.presentation.api.v1.accommodation.schemas import (
    AllocateRoomRequest,
    AssignMaintenanceRequest,
    CreateHallRequest,
    CreateRoomRequest,
    DeallocateRequest,
    HallResponse,
    MaintenanceRequestCreate,
    MaintenanceRequestResponse,
    OccupancyHallBreakdown,
    OccupancySummaryResponse,
    RoomOccupantResponse,
    RoomResponse,
    UpdateHallRequest,
    UpdateRoomRequest,
)
from app.infrastructure.database.repositories.accommodation_repository import (
    HallRepository, RoomRepository, AccommodationRepository, MaintenanceRequestRepository
)
from app.dependencies import get_current_user, require_roles
from app.infrastructure.models.user import User
from datetime import datetime

router = APIRouter()

def get_hall_repo() -> HallRepository:
    return HallRepository()

def get_room_repo() -> RoomRepository:
    return RoomRepository()

def get_accommodation_repo() -> AccommodationRepository:
    return AccommodationRepository()

def get_maintenance_repo() -> MaintenanceRequestRepository:
    return MaintenanceRequestRepository()

@router.post("/halls", response_model=HallResponse)
async def create_hall(
    request: CreateHallRequest,
    current_user: User = Depends(require_roles("hostel_administrator", "university_admin", "super_admin")),
    hall_repo=Depends(get_hall_repo),
):
    hall = await hall_repo.create({"tenant_id": current_user.tenant_id or "default", **request.dict()})
    return HallResponse(
        id=str(hall.id),
        name=hall.name,
        capacity=hall.capacity,
        gender=getattr(hall, "gender", None),
        is_active=getattr(hall, "is_active", True),
    )

@router.get("/halls", response_model=List[HallResponse])
async def list_halls(
    current_user: User = Depends(get_current_user),
    hall_repo=Depends(get_hall_repo),
):
    halls = await hall_repo.get_all_for_tenant(current_user.tenant_id or "default")
    return [HallResponse(id=str(h.id), name=h.name, capacity=h.capacity, gender=h.gender, is_active=h.is_active) for h in halls]

@router.post("/rooms", response_model=RoomResponse)
async def create_room(
    request: CreateRoomRequest,
    current_user: User = Depends(require_roles("hostel_administrator", "university_admin", "super_admin")),
    room_repo=Depends(get_room_repo),
):
    room = await room_repo.create({"tenant_id": current_user.tenant_id or "default", **request.dict()})
    return RoomResponse(
        id=str(room.id),
        hall_id=request.hall_id,
        room_number=room.room_number,
        room_type=room.room_type,
        capacity=room.capacity,
        occupied=room.occupied,
        is_active=getattr(room, "is_active", True),
    )

@router.get("/rooms/hall/{hall_id}", response_model=List[RoomResponse])
async def list_rooms(
    hall_id: str,
    current_user: User = Depends(get_current_user),
    room_repo=Depends(get_room_repo),
):
    rooms = await room_repo.get_by_hall(hall_id)
    return [
        RoomResponse(id=str(r.id), hall_id=r.hall_id, room_number=r.room_number, room_type=r.room_type,
                     capacity=r.capacity, occupied=r.occupied, is_active=r.is_active)
        for r in rooms
    ]

@router.post("/allocate")
async def allocate_room(
    request: AllocateRoomRequest,
    current_user: User = Depends(require_roles("hostel_administrator", "university_admin", "super_admin")),
    accommodation_repo=Depends(get_accommodation_repo),
    room_repo=Depends(get_room_repo),
):
    room = await room_repo.get_by_id(request.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    if room.occupied >= room.capacity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room is full")

    accommodation = await accommodation_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "student_id": request.student_id,
        "hall_id": request.hall_id,
        "room_id": request.room_id,
        "check_in_date": datetime.utcnow(),
    })

    await room_repo.update(request.room_id, {
        "occupied": room.occupied + 1,
        "students": room.students + [request.student_id]
    })

    return {"accommodation_id": str(accommodation.id), "status": "allocated"}

@router.put("/halls/{hall_id}", response_model=HallResponse)
async def update_hall(
    hall_id: str,
    request: UpdateHallRequest,
    current_user: User = Depends(require_roles("hostel_administrator", "university_admin", "super_admin")),
    hall_repo=Depends(get_hall_repo),
):
    hall = await hall_repo.get_by_id(hall_id)
    if not hall or hall.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hall not found")

    update_data = {k: v for k, v in request.dict().items() if v is not None}
    hall = await hall_repo.update(hall_id, update_data)
    return HallResponse(
        id=str(hall.id), name=hall.name, capacity=hall.capacity,
        gender=hall.gender, is_active=hall.is_active,
    )

@router.put("/rooms/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: str,
    request: UpdateRoomRequest,
    current_user: User = Depends(require_roles("hostel_administrator", "university_admin", "super_admin")),
    room_repo=Depends(get_room_repo),
):
    room = await room_repo.get_by_id(room_id)
    if not room or room.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    update_data = {k: v for k, v in request.dict().items() if v is not None}
    room = await room_repo.update(room_id, update_data)
    return RoomResponse(
        id=str(room.id), hall_id=room.hall_id, room_number=room.room_number,
        room_type=room.room_type, capacity=room.capacity, occupied=room.occupied,
        is_active=room.is_active,
    )

@router.post("/deallocate")
async def deallocate_room(
    request: DeallocateRequest,
    current_user: User = Depends(require_roles("hostel_administrator", "university_admin", "super_admin")),
    accommodation_repo=Depends(get_accommodation_repo),
    room_repo=Depends(get_room_repo),
):
    accommodation = await accommodation_repo.get_by_student(current_user.tenant_id or "default", request.student_id)
    if not accommodation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active accommodation not found")

    room = await room_repo.get_by_id(accommodation.room_id)
    if room:
        new_students = [s for s in room.students if s != request.student_id]
        await room_repo.update(room.id, {
            "occupied": max(0, room.occupied - 1),
            "students": new_students,
        })

    await accommodation_repo.update(str(accommodation.id), {
        "check_out_date": datetime.utcnow(),
        "is_active": False,
    })

    return {"status": "deallocated", "student_id": request.student_id}

@router.get("/rooms/{room_id}/occupants", response_model=List[RoomOccupantResponse])
async def list_room_occupants(
    room_id: str,
    current_user: User = Depends(require_roles("hostel_administrator", "university_admin", "super_admin")),
    accommodation_repo=Depends(get_accommodation_repo),
):
    accommodations = await accommodation_repo.get_by_room(room_id)
    return [
        RoomOccupantResponse(
            student_id=a.student_id,
            hall_id=a.hall_id,
            room_id=a.room_id,
            check_in_date=a.check_in_date,
            check_out_date=a.check_out_date,
            is_active=a.is_active,
        )
        for a in accommodations
    ]

@router.post("/maintenance", response_model=MaintenanceRequestResponse)
async def report_maintenance(
    request: MaintenanceRequestCreate,
    current_user: User = Depends(get_current_user),
    maintenance_repo=Depends(get_maintenance_repo),
):
    maintenance = await maintenance_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "hall_id": request.hall_id,
        "room_id": request.room_id,
        "reported_by": str(current_user.id),
        "issue_description": request.issue_description,
    })
    return {
        "id": str(maintenance.id),
        "hall_id": request.hall_id,
        "room_id": request.room_id,
        "reported_by": str(current_user.id),
        "issue_description": maintenance.issue_description,
        "status": getattr(maintenance, "status", "pending"),
        "assigned_to": getattr(maintenance, "assigned_to", None),
        "created_date": getattr(maintenance, "created_date", None),
        "resolved_date": getattr(maintenance, "resolved_date", None),
    }


@router.get("/maintenance")
async def list_all_maintenance(
    current_user: User = Depends(require_roles("hostel_administrator", "university_admin", "super_admin")),
    maintenance_repo=Depends(get_maintenance_repo),
):
    requests = await maintenance_repo.get_all(tenant_id=current_user.tenant_id or "default")
    return [
        {
            "id": str(r.id),
            "hall_id": r.hall_id,
            "room_id": r.room_id,
            "reported_by": r.reported_by,
            "issue_description": r.issue_description,
            "status": r.status,
            "assigned_to": r.assigned_to,
            "created_date": r.created_date,
            "resolved_date": r.resolved_date,
        }
        for r in requests
    ]

@router.get("/summary", response_model=OccupancySummaryResponse)
async def get_occupancy_summary(
    current_user: User = Depends(require_roles("hostel_administrator", "university_admin", "super_admin")),
    hall_repo=Depends(get_hall_repo),
    room_repo=Depends(get_room_repo),
):
    halls = await hall_repo.get_all_for_tenant(current_user.tenant_id or "default")
    total_rooms = 0
    total_capacity = 0
    total_occupied = 0
    hall_breakdowns = []

    for hall in halls:
        rooms = await room_repo.get_by_hall(hall.id)
        room_count = len(rooms)
        capacity = sum(r.capacity for r in rooms)
        occupied = sum(r.occupied for r in rooms)
        total_rooms += room_count
        total_capacity += capacity
        total_occupied += occupied
        hall_breakdowns.append(OccupancyHallBreakdown(
            hall_id=str(hall.id), hall_name=hall.name,
            room_count=room_count, capacity=capacity, occupied=occupied,
        ))

    vacancy_rate = 0.0
    if total_capacity > 0:
        vacancy_rate = max(0.0, (total_capacity - total_occupied) / total_capacity)

    return OccupancySummaryResponse(
        total_halls=len(halls),
        total_rooms=total_rooms,
        total_capacity=total_capacity,
        total_occupied=total_occupied,
        vacancy_rate=vacancy_rate,
        halls=hall_breakdowns,
    )

@router.get("/maintenance/pending")
async def list_pending_maintenance(
    current_user: User = Depends(require_roles("hostel_administrator", "university_admin", "super_admin")),
    maintenance_repo=Depends(get_maintenance_repo),
):
    requests = await maintenance_repo.get_pending_requests(current_user.tenant_id or "default")
    return [
        {
            "id": str(r.id),
            "hall_id": getattr(r, "hall_id", None),
            "room_id": getattr(r, "room_id", None),
            "reported_by": getattr(r, "reported_by", ""),
            "issue_description": getattr(r, "issue_description", ""),
            "status": getattr(r, "status", "pending"),
            "assigned_to": getattr(r, "assigned_to", None),
            "created_date": getattr(r, "created_date", None),
            "resolved_date": getattr(r, "resolved_date", None),
        }
        for r in requests
    ]

@router.post("/maintenance/{maintenance_id}/assign")
async def assign_maintenance(
    maintenance_id: str,
    request: AssignMaintenanceRequest,
    current_user: User = Depends(require_roles("hostel_administrator", "university_admin", "super_admin")),
    maintenance_repo=Depends(get_maintenance_repo),
):
    m = await maintenance_repo.get_by_id(maintenance_id)
    if not m or getattr(m, 'tenant_id', None) != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance request not found")
    updated = await maintenance_repo.update(maintenance_id, {"status": "assigned", "assignee_id": request.assignee_id, "assigned_at": datetime.utcnow()})
    return {"id": str(updated.id), "status": updated.status}


@router.post("/maintenance/{maintenance_id}/resolve")
async def resolve_maintenance(
    maintenance_id: str,
    current_user: User = Depends(require_roles("hostel_administrator", "university_admin", "super_admin")),
    maintenance_repo=Depends(get_maintenance_repo),
):
    m = await maintenance_repo.get_by_id(maintenance_id)
    if not m or getattr(m, 'tenant_id', None) != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance request not found")
    updated = await maintenance_repo.update(maintenance_id, {"status": "resolved", "resolved_by": str(current_user.id), "resolved_at": datetime.utcnow()})
    return {"id": str(updated.id), "status": updated.status}
