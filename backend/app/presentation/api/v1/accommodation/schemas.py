from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CreateHallRequest(BaseModel):
    name: str
    capacity: int
    gender: Optional[str] = None

class CreateRoomRequest(BaseModel):
    hall_id: str
    room_number: str
    room_type: str
    capacity: int

class AllocateRoomRequest(BaseModel):
    student_id: str
    hall_id: str
    room_id: str

class MaintenanceRequestCreate(BaseModel):
    hall_id: str
    room_id: Optional[str] = None
    issue_description: str

class UpdateHallRequest(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    gender: Optional[str] = None
    is_active: Optional[bool] = None

class HallResponse(BaseModel):
    id: str
    name: str
    capacity: int
    gender: Optional[str] = None
    is_active: bool

class UpdateRoomRequest(BaseModel):
    room_number: Optional[str] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None

class RoomResponse(BaseModel):
    id: str
    hall_id: str
    room_number: str
    room_type: str
    capacity: int
    occupied: int
    is_active: bool

class DeallocateRequest(BaseModel):
    student_id: str

class RoomOccupantResponse(BaseModel):
    student_id: str
    hall_id: str
    room_id: str
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    is_active: bool

class MaintenanceRequestResponse(BaseModel):
    id: str
    hall_id: str
    room_id: Optional[str] = None
    reported_by: str
    issue_description: str
    status: str
    assigned_to: Optional[str] = None
    created_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None

class OccupancyHallBreakdown(BaseModel):
    hall_id: str
    hall_name: str
    room_count: int
    capacity: int
    occupied: int

class OccupancySummaryResponse(BaseModel):
    total_halls: int
    total_rooms: int
    total_capacity: int
    total_occupied: int
    vacancy_rate: float
    halls: List[OccupancyHallBreakdown]

class AssignMaintenanceRequest(BaseModel):
    assignee_id: str

class HousingSelectionRequest(BaseModel):
    housing_type: str  # "school_hostel", "outside_hostel", "private_renting"
    
    # For school_hostel
    hall_id: Optional[str] = None
    room_id: Optional[str] = None

    # For outside_hostel
    outside_hostel_name: Optional[str] = None
    outside_hostel_address: Optional[str] = None
    outside_hostel_contact: Optional[str] = None

    # For private_renting
    private_address: Optional[str] = None
    private_city: Optional[str] = None
    private_contact: Optional[str] = None

class StudentHousingStatusResponse(BaseModel):
    student_id: str
    school_fee_paid: bool
    hostel_fee_paid: bool
    housing_status: str  # "unassigned", "school_hostel", "outside_hostel", "private_renting"
    
    hall_id: Optional[str] = None
    hall_name: Optional[str] = None
    room_id: Optional[str] = None
    room_number: Optional[str] = None
    
    outside_hostel_name: Optional[str] = None
    outside_hostel_address: Optional[str] = None
    outside_hostel_contact: Optional[str] = None

    private_address: Optional[str] = None
    private_city: Optional[str] = None
    private_contact: Optional[str] = None

