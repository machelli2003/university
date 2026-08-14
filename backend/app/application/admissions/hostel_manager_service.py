"""
Hostel Manager Dashboard Service
Item 47: Accommodation and hostel management

Hostel Manager responsibilities:
- Manage hostel allocations
- Track room occupancy
- Handle maintenance requests
- Generate accommodation reports
- Manage hostel staff
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class HostelType(str, Enum):
    """Types of hostels"""
    MALE = "male"
    FEMALE = "female"
    MIXED = "mixed"


class RoomStatus(str, Enum):
    """Room occupancy status"""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"


class MaintenanceStatus(str, Enum):
    """Maintenance request status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ==================== MODELS ====================

class HostelInfo(BaseModel):
    """Hostel information"""
    hostel_id: str
    hostel_name: str
    hostel_type: HostelType
    total_rooms: int
    caretaker_id: str
    manager_id: str
    location: str
    capacity: int


class RoomAllocation(BaseModel):
    """Room allocation record"""
    allocation_id: str
    room_id: str
    hostel_id: str
    student_id: str
    allocation_date: datetime
    checkout_date: Optional[datetime] = None
    status: RoomStatus
    room_number: str
    occupants: List[str] = Field(default_factory=list)


class MaintenanceRequest(BaseModel):
    """Hostel maintenance request"""
    request_id: str
    hostel_id: str
    room_id: Optional[str] = None
    issue_type: str  # electrical, plumbing, structural, furniture, cleaning
    description: str
    reported_by: str
    reported_date: datetime
    status: MaintenanceStatus
    assigned_to: Optional[str] = None
    completion_date: Optional[datetime] = None
    cost_estimate: Optional[float] = None


class HostelOccupancyReport(BaseModel):
    """Occupancy report"""
    report_id: str
    hostel_id: str
    report_date: datetime
    total_rooms: int
    occupied_rooms: int
    available_rooms: int
    occupancy_rate: float  # percentage
    maintenance_rooms: int


class HostelStaff(BaseModel):
    """Hostel staff member"""
    staff_id: str
    hostel_id: str
    name: str
    role: str  # caretaker, cleaner, maintenance
    contact_number: str
    email: str
    employed_date: datetime
    status: str = "active"


# ==================== DOCUMENTS ====================

class HostelDocument(Document):
    """Hostel records"""
    hostel_id: str = Indexed()
    tenant_id: str = Indexed()
    hostel_name: str
    hostel_type: str
    total_rooms: int
    caretaker_id: str
    manager_id: str
    location: str
    capacity: int
    
    class Settings:
        collection = "hostels"


class RoomAllocationDocument(Document):
    """Room allocations"""
    allocation_id: str = Indexed()
    tenant_id: str = Indexed()
    room_id: str = Indexed()
    hostel_id: str = Indexed()
    student_id: str = Indexed()
    allocation_date: datetime
    checkout_date: Optional[datetime] = None
    status: str
    room_number: str
    occupants: List[str]
    
    class Settings:
        collection = "room_allocations"


class MaintenanceRequestDocument(Document):
    """Maintenance requests"""
    request_id: str = Indexed()
    tenant_id: str = Indexed()
    hostel_id: str = Indexed()
    room_id: Optional[str] = None
    issue_type: str
    description: str
    reported_by: str
    reported_date: datetime
    status: str
    assigned_to: Optional[str] = None
    completion_date: Optional[datetime] = None
    cost_estimate: Optional[float] = None
    
    class Settings:
        collection = "maintenance_requests"


class HostelOccupancyReportDocument(Document):
    """Occupancy reports"""
    report_id: str = Indexed()
    tenant_id: str = Indexed()
    hostel_id: str = Indexed()
    report_date: datetime
    total_rooms: int
    occupied_rooms: int
    available_rooms: int
    occupancy_rate: float
    maintenance_rooms: int
    
    class Settings:
        collection = "hostel_occupancy_reports"


class HostelStaffDocument(Document):
    """Hostel staff"""
    staff_id: str = Indexed()
    tenant_id: str = Indexed()
    hostel_id: str = Indexed()
    name: str
    role: str
    contact_number: str
    email: str
    employed_date: datetime
    status: str
    
    class Settings:
        collection = "hostel_staff"


# ==================== SERVICE ====================

class HostelManagerService:
    """Hostel Manager operations"""
    
    async def get_hostel_info(
        self,
        tenant_id: str,
        hostel_id: str,
    ) -> Optional[HostelInfo]:
        """Get hostel information"""
        doc = await HostelDocument.find_one(
            HostelDocument.tenant_id == tenant_id,
            HostelDocument.hostel_id == hostel_id,
        )
        
        if not doc:
            return None
        
        return HostelInfo(
            hostel_id=doc.hostel_id,
            hostel_name=doc.hostel_name,
            hostel_type=HostelType(doc.hostel_type),
            total_rooms=doc.total_rooms,
            caretaker_id=doc.caretaker_id,
            manager_id=doc.manager_id,
            location=doc.location,
            capacity=doc.capacity,
        )
    
    async def allocate_room(
        self,
        tenant_id: str,
        hostel_id: str,
        room_id: str,
        room_number: str,
        student_id: str,
        manager_id: str,
    ) -> RoomAllocation:
        """Allocate room to student"""
        allocation_id = f"ALLOC-{room_id}-{student_id}"
        
        doc = RoomAllocationDocument(
            allocation_id=allocation_id,
            tenant_id=tenant_id,
            room_id=room_id,
            hostel_id=hostel_id,
            student_id=student_id,
            allocation_date=datetime.utcnow(),
            status=RoomStatus.OCCUPIED.value,
            room_number=room_number,
            occupants=[student_id],
        )
        
        await doc.insert()
        
        logger.info(f"Allocated room {room_number} to student {student_id}")
        
        return RoomAllocation(
            allocation_id=allocation_id,
            room_id=room_id,
            hostel_id=hostel_id,
            student_id=student_id,
            allocation_date=doc.allocation_date,
            status=RoomStatus.OCCUPIED,
            room_number=room_number,
            occupants=doc.occupants,
        )
    
    async def deallocate_room(
        self,
        tenant_id: str,
        allocation_id: str,
        manager_id: str,
    ) -> RoomAllocation:
        """Remove student from room"""
        doc = await RoomAllocationDocument.find_one(
            RoomAllocationDocument.tenant_id == tenant_id,
            RoomAllocationDocument.allocation_id == allocation_id,
        )
        
        if not doc:
            raise ValueError(f"Allocation {allocation_id} not found")
        
        doc.checkout_date = datetime.utcnow()
        doc.status = RoomStatus.AVAILABLE.value
        doc.occupants = []
        await doc.save()
        
        logger.info(f"Deallocated allocation {allocation_id}")
        
        return RoomAllocation(**doc.dict())
    
    async def get_hostel_occupancy(
        self,
        tenant_id: str,
        hostel_id: str,
    ) -> HostelOccupancyReport:
        """Get hostel occupancy statistics"""
        hostel = await self.get_hostel_info(tenant_id, hostel_id)
        
        if not hostel:
            raise ValueError(f"Hostel {hostel_id} not found")
        
        # Get allocations
        allocations = await RoomAllocationDocument.find(
            RoomAllocationDocument.tenant_id == tenant_id,
            RoomAllocationDocument.hostel_id == hostel_id,
            RoomAllocationDocument.status == RoomStatus.OCCUPIED.value,
        ).to_list()
        
        occupied = len(allocations)
        available = hostel.total_rooms - occupied
        
        # Count maintenance rooms
        maintenance = await MaintenanceRequestDocument.find(
            MaintenanceRequestDocument.tenant_id == tenant_id,
            MaintenanceRequestDocument.hostel_id == hostel_id,
            MaintenanceRequestDocument.status == MaintenanceStatus.IN_PROGRESS.value,
        ).count()
        
        occupancy_rate = (occupied / hostel.total_rooms * 100) if hostel.total_rooms > 0 else 0
        
        report = HostelOccupancyReport(
            report_id=f"OCC-{hostel_id}-{datetime.utcnow().timestamp()}",
            hostel_id=hostel_id,
            report_date=datetime.utcnow(),
            total_rooms=hostel.total_rooms,
            occupied_rooms=occupied,
            available_rooms=available,
            occupancy_rate=round(occupancy_rate, 2),
            maintenance_rooms=maintenance,
        )
        
        # Store report
        doc = HostelOccupancyReportDocument(
            report_id=report.report_id,
            tenant_id=tenant_id,
            hostel_id=hostel_id,
            report_date=report.report_date,
            total_rooms=report.total_rooms,
            occupied_rooms=report.occupied_rooms,
            available_rooms=report.available_rooms,
            occupancy_rate=report.occupancy_rate,
            maintenance_rooms=report.maintenance_rooms,
        )
        
        await doc.insert()
        
        return report
    
    async def report_maintenance(
        self,
        tenant_id: str,
        hostel_id: str,
        issue_type: str,
        description: str,
        reported_by: str,
        room_id: Optional[str] = None,
    ) -> MaintenanceRequest:
        """Report maintenance issue"""
        request_id = f"MAINT-{hostel_id}-{datetime.utcnow().timestamp()}"
        
        doc = MaintenanceRequestDocument(
            request_id=request_id,
            tenant_id=tenant_id,
            hostel_id=hostel_id,
            room_id=room_id,
            issue_type=issue_type,
            description=description,
            reported_by=reported_by,
            reported_date=datetime.utcnow(),
            status=MaintenanceStatus.PENDING.value,
        )
        
        await doc.insert()
        
        logger.info(f"Maintenance request {request_id}: {issue_type}")
        
        return MaintenanceRequest(
            request_id=request_id,
            hostel_id=hostel_id,
            room_id=room_id,
            issue_type=issue_type,
            description=description,
            reported_by=reported_by,
            reported_date=doc.reported_date,
            status=MaintenanceStatus.PENDING,
        )
    
    async def assign_maintenance(
        self,
        tenant_id: str,
        request_id: str,
        assigned_to: str,
        cost_estimate: Optional[float] = None,
    ) -> MaintenanceRequest:
        """Assign maintenance staff to request"""
        doc = await MaintenanceRequestDocument.find_one(
            MaintenanceRequestDocument.tenant_id == tenant_id,
            MaintenanceRequestDocument.request_id == request_id,
        )
        
        if not doc:
            raise ValueError(f"Request {request_id} not found")
        
        doc.status = MaintenanceStatus.IN_PROGRESS.value
        doc.assigned_to = assigned_to
        doc.cost_estimate = cost_estimate
        await doc.save()
        
        logger.info(f"Assigned maintenance {request_id} to {assigned_to}")
        
        return MaintenanceRequest(**doc.dict())
    
    async def complete_maintenance(
        self,
        tenant_id: str,
        request_id: str,
    ) -> MaintenanceRequest:
        """Mark maintenance as completed"""
        doc = await MaintenanceRequestDocument.find_one(
            MaintenanceRequestDocument.tenant_id == tenant_id,
            MaintenanceRequestDocument.request_id == request_id,
        )
        
        if not doc:
            raise ValueError(f"Request {request_id} not found")
        
        doc.status = MaintenanceStatus.COMPLETED.value
        doc.completion_date = datetime.utcnow()
        await doc.save()
        
        logger.info(f"Completed maintenance {request_id}")
        
        return MaintenanceRequest(**doc.dict())
    
    async def get_pending_maintenance(
        self,
        tenant_id: str,
        hostel_id: str,
    ) -> List[MaintenanceRequest]:
        """Get pending maintenance requests"""
        docs = await MaintenanceRequestDocument.find(
            MaintenanceRequestDocument.tenant_id == tenant_id,
            MaintenanceRequestDocument.hostel_id == hostel_id,
            MaintenanceRequestDocument.status == MaintenanceStatus.PENDING.value,
        ).to_list()
        
        return [MaintenanceRequest(**d.dict()) for d in docs]
    
    async def get_hostel_staff(
        self,
        tenant_id: str,
        hostel_id: str,
    ) -> List[HostelStaff]:
        """Get hostel staff"""
        docs = await HostelStaffDocument.find(
            HostelStaffDocument.tenant_id == tenant_id,
            HostelStaffDocument.hostel_id == hostel_id,
            HostelStaffDocument.status == "active",
        ).to_list()
        
        return [
            HostelStaff(
                staff_id=d.staff_id,
                hostel_id=d.hostel_id,
                name=d.name,
                role=d.role,
                contact_number=d.contact_number,
                email=d.email,
                employed_date=d.employed_date,
                status=d.status,
            )
            for d in docs
        ]
    
    async def get_hostel_overview(
        self,
        tenant_id: str,
        hostel_id: str,
        manager_id: str,
    ) -> Dict[str, Any]:
        """Get comprehensive hostel overview"""
        hostel = await self.get_hostel_info(tenant_id, hostel_id)
        
        if not hostel:
            raise ValueError("Hostel not found")
        
        occupancy = await self.get_hostel_occupancy(tenant_id, hostel_id)
        pending_maintenance = await self.get_pending_maintenance(tenant_id, hostel_id)
        staff = await self.get_hostel_staff(tenant_id, hostel_id)
        
        return {
            "hostel_id": hostel_id,
            "hostel_name": hostel.hostel_name,
            "hostel_type": hostel.hostel_type.value,
            "location": hostel.location,
            "capacity": hostel.capacity,
            "occupancy": occupancy.dict(),
            "pending_maintenance": len(pending_maintenance),
            "maintenance_requests": [m.dict() for m in pending_maintenance],
            "staff_count": len(staff),
            "staff": [s.dict() for s in staff],
        }
