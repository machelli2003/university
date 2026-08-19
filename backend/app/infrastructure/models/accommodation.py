from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime

class Hall(Document):
    tenant_id: str
    name: str
    capacity: int
    gender: Optional[str] = None
    is_active: bool = True

    blocks: List[str] = []

    class Settings:
        name = "halls"

class Room(Document):
    tenant_id: str
    hall_id: str
    room_number: str
    room_type: str
    capacity: int

    occupied: int = 0
    students: List[str] = []
    is_active: bool = True

    class Settings:
        name = "rooms"

class Accommodation(Document):
    tenant_id: str
    student_id: str

    housing_type: str = "school_hostel"  # school_hostel, outside_hostel, private_renting
    hall_id: Optional[str] = None
    room_id: Optional[str] = None

    outside_hostel_name: Optional[str] = None
    outside_hostel_address: Optional[str] = None
    outside_hostel_contact: Optional[str] = None

    private_address: Optional[str] = None
    private_city: Optional[str] = None
    private_contact: Optional[str] = None

    allocation_date: datetime = Field(default_factory=datetime.utcnow)
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None

    is_active: bool = True

    class Settings:
        name = "accommodations"

class MaintenanceRequest(Document):
    tenant_id: str
    hall_id: str
    room_id: Optional[str] = None

    reported_by: str
    issue_description: str

    status: str = "pending"
    assigned_to: Optional[str] = None

    created_date: datetime = Field(default_factory=datetime.utcnow)
    resolved_date: Optional[datetime] = None

    class Settings:
        name = "maintenance_requests"
