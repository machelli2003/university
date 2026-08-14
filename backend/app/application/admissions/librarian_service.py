"""
Librarian Dashboard Service
Item 48: Library resource and circulation management

Librarian responsibilities:
- Manage library resources (books, journals, materials)
- Track item circulation (checkout/return)
- Handle fines and overdue items
- Generate library reports
- Manage library staff
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class ResourceType(str, Enum):
    """Library resource types"""
    BOOK = "book"
    JOURNAL = "journal"
    REFERENCE = "reference"
    PERIODICAL = "periodical"
    THESIS = "thesis"
    MULTIMEDIA = "multimedia"


class CheckoutStatus(str, Enum):
    """Checkout status"""
    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"
    RESERVED = "reserved"
    LOST = "lost"


# ==================== MODELS ====================

class LibraryResource(BaseModel):
    """Library resource record"""
    resource_id: str
    title: str
    author: str
    isbn: str
    resource_type: ResourceType
    call_number: str
    location: str
    total_copies: int
    available_copies: int
    acquisition_date: datetime
    status: str = "active"


class CheckoutRecord(BaseModel):
    """Resource checkout record"""
    checkout_id: str
    resource_id: str
    student_id: str
    checkout_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str  # active, returned
    fine_amount: float = 0.0


class LibraryFine(BaseModel):
    """Library fine record"""
    fine_id: str
    student_id: str
    resource_id: str
    fine_amount: float
    reason: str  # overdue, lost_book, damage
    imposed_date: datetime
    due_date: datetime
    paid_date: Optional[datetime] = None
    paid_amount: Optional[float] = None
    status: str  # pending, partial, paid, waived


class LibraryReport(BaseModel):
    """Library statistics report"""
    report_id: str
    report_type: str  # daily, monthly, annual
    period: str
    total_resources: int
    available_resources: int
    total_checkouts: int
    total_returns: int
    overdue_items: int
    total_fines_collected: float
    generated_date: datetime


class LibraryStaff(BaseModel):
    """Library staff member"""
    staff_id: str
    name: str
    role: str  # librarian, assistant, technician
    email: str
    phone: str
    employed_date: datetime
    status: str = "active"


# ==================== DOCUMENTS ====================

class LibraryResourceDocument(Document):
    """Library resources"""
    resource_id: str = Indexed()
    tenant_id: str = Indexed()
    title: str
    author: str
    isbn: str = Indexed()
    resource_type: str
    call_number: str
    location: str
    total_copies: int
    available_copies: int
    acquisition_date: datetime
    status: str
    
    class Settings:
        collection = "library_resources"


class CheckoutRecordDocument(Document):
    """Checkout records"""
    checkout_id: str = Indexed()
    tenant_id: str = Indexed()
    resource_id: str = Indexed()
    student_id: str = Indexed()
    checkout_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str
    fine_amount: float
    
    class Settings:
        collection = "checkout_records"


class LibraryFineDocument(Document):
    """Library fines"""
    fine_id: str = Indexed()
    tenant_id: str = Indexed()
    student_id: str = Indexed()
    resource_id: str
    fine_amount: float
    reason: str
    imposed_date: datetime
    due_date: datetime
    paid_date: Optional[datetime] = None
    paid_amount: Optional[float] = None
    status: str
    
    class Settings:
        collection = "library_fines"


class LibraryReportDocument(Document):
    """Library reports"""
    report_id: str = Indexed()
    tenant_id: str = Indexed()
    report_type: str
    period: str
    total_resources: int
    available_resources: int
    total_checkouts: int
    total_returns: int
    overdue_items: int
    total_fines_collected: float
    generated_date: datetime
    
    class Settings:
        collection = "library_reports"


class LibraryStaffDocument(Document):
    """Library staff"""
    staff_id: str = Indexed()
    tenant_id: str = Indexed()
    name: str
    role: str
    email: str
    phone: str
    employed_date: datetime
    status: str
    
    class Settings:
        collection = "library_staff"


# ==================== SERVICE ====================

class LibrarianService:
    """Librarian operations"""
    
    async def get_resource(
        self,
        tenant_id: str,
        resource_id: str,
    ) -> Optional[LibraryResource]:
        """Get resource information"""
        doc = await LibraryResourceDocument.find_one(
            LibraryResourceDocument.tenant_id == tenant_id,
            LibraryResourceDocument.resource_id == resource_id,
        )
        
        if not doc:
            return None
        
        return LibraryResource(
            resource_id=doc.resource_id,
            title=doc.title,
            author=doc.author,
            isbn=doc.isbn,
            resource_type=ResourceType(doc.resource_type),
            call_number=doc.call_number,
            location=doc.location,
            total_copies=doc.total_copies,
            available_copies=doc.available_copies,
            acquisition_date=doc.acquisition_date,
            status=doc.status,
        )
    
    async def checkout_resource(
        self,
        tenant_id: str,
        resource_id: str,
        student_id: str,
        checkout_days: int = 14,
    ) -> CheckoutRecord:
        """Check out resource to student"""
        resource = await self.get_resource(tenant_id, resource_id)
        
        if not resource or resource.available_copies == 0:
            raise ValueError("Resource not available")
        
        checkout_id = f"CHK-{resource_id}-{student_id}-{datetime.utcnow().timestamp()}"
        from datetime import timedelta
        due_date = datetime.utcnow() + timedelta(days=checkout_days)
        
        doc = CheckoutRecordDocument(
            checkout_id=checkout_id,
            tenant_id=tenant_id,
            resource_id=resource_id,
            student_id=student_id,
            checkout_date=datetime.utcnow(),
            due_date=due_date,
            status="active",
            fine_amount=0.0,
        )
        
        await doc.insert()
        
        # Update available copies
        resource_doc = await LibraryResourceDocument.find_one(
            LibraryResourceDocument.tenant_id == tenant_id,
            LibraryResourceDocument.resource_id == resource_id,
        )
        resource_doc.available_copies -= 1
        await resource_doc.save()
        
        logger.info(f"Checked out {resource_id} to {student_id}")
        
        return CheckoutRecord(
            checkout_id=checkout_id,
            resource_id=resource_id,
            student_id=student_id,
            checkout_date=doc.checkout_date,
            due_date=due_date,
            status="active",
        )
    
    async def return_resource(
        self,
        tenant_id: str,
        checkout_id: str,
    ) -> CheckoutRecord:
        """Return resource from student"""
        doc = await CheckoutRecordDocument.find_one(
            CheckoutRecordDocument.tenant_id == tenant_id,
            CheckoutRecordDocument.checkout_id == checkout_id,
        )
        
        if not doc:
            raise ValueError(f"Checkout {checkout_id} not found")
        
        # Calculate fine if overdue
        fine_amount = 0.0
        if datetime.utcnow() > doc.due_date:
            days_overdue = (datetime.utcnow() - doc.due_date).days
            fine_amount = days_overdue * 1.0  # $1 per day fine
            
            # Create fine record
            fine_doc = LibraryFineDocument(
                fine_id=f"FINE-{doc.resource_id}-{doc.student_id}",
                tenant_id=tenant_id,
                student_id=doc.student_id,
                resource_id=doc.resource_id,
                fine_amount=fine_amount,
                reason="overdue",
                imposed_date=datetime.utcnow(),
                due_date=datetime.utcnow() + __import__('datetime').timedelta(days=7),
                status="pending",
            )
            await fine_doc.insert()
        
        doc.return_date = datetime.utcnow()
        doc.status = "returned"
        doc.fine_amount = fine_amount
        await doc.save()
        
        # Update available copies
        resource_doc = await LibraryResourceDocument.find_one(
            LibraryResourceDocument.tenant_id == tenant_id,
            LibraryResourceDocument.resource_id == doc.resource_id,
        )
        resource_doc.available_copies += 1
        await resource_doc.save()
        
        logger.info(f"Returned {doc.resource_id} from {doc.student_id}, fine: ${fine_amount}")
        
        return CheckoutRecord(**doc.dict())
    
    async def get_student_overdue_items(
        self,
        tenant_id: str,
        student_id: str,
    ) -> List[CheckoutRecord]:
        """Get overdue items for student"""
        now = datetime.utcnow()
        docs = await CheckoutRecordDocument.find(
            CheckoutRecordDocument.tenant_id == tenant_id,
            CheckoutRecordDocument.student_id == student_id,
            CheckoutRecordDocument.status == "active",
        ).to_list()
        
        overdue = [
            CheckoutRecord(**d.dict())
            for d in docs
            if d.due_date < now
        ]
        
        return overdue
    
    async def get_student_fines(
        self,
        tenant_id: str,
        student_id: str,
    ) -> List[LibraryFine]:
        """Get fines for student"""
        docs = await LibraryFineDocument.find(
            LibraryFineDocument.tenant_id == tenant_id,
            LibraryFineDocument.student_id == student_id,
        ).to_list()
        
        return [LibraryFine(**d.dict()) for d in docs]
    
    async def pay_fine(
        self,
        tenant_id: str,
        fine_id: str,
        amount_paid: float,
    ) -> LibraryFine:
        """Record fine payment"""
        doc = await LibraryFineDocument.find_one(
            LibraryFineDocument.tenant_id == tenant_id,
            LibraryFineDocument.fine_id == fine_id,
        )
        
        if not doc:
            raise ValueError(f"Fine {fine_id} not found")
        
        if amount_paid >= doc.fine_amount:
            doc.status = "paid"
        else:
            doc.status = "partial"
        
        doc.paid_date = datetime.utcnow()
        doc.paid_amount = amount_paid
        await doc.save()
        
        logger.info(f"Paid fine {fine_id}: ${amount_paid}")
        
        return LibraryFine(**doc.dict())
    
    async def generate_library_report(
        self,
        tenant_id: str,
        report_type: str,  # daily, monthly, annual
        period: str,
    ) -> LibraryReport:
        """Generate library statistics report"""
        # Count resources
        resources = await LibraryResourceDocument.find(
            LibraryResourceDocument.tenant_id == tenant_id,
        ).to_list()
        
        total_resources = len(resources)
        available_resources = sum(r.available_copies for r in resources)
        
        # Count checkouts and returns
        checkouts = await CheckoutRecordDocument.find(
            CheckoutRecordDocument.tenant_id == tenant_id,
        ).to_list()
        
        total_checkouts = len(checkouts)
        total_returns = len([c for c in checkouts if c.status == "returned"])
        
        # Count overdue
        now = datetime.utcnow()
        overdue = len([c for c in checkouts if c.status == "active" and c.due_date < now])
        
        # Sum fines
        fines = await LibraryFineDocument.find(
            LibraryFineDocument.tenant_id == tenant_id,
        ).to_list()
        
        total_fines = sum(f.paid_amount for f in fines if f.status == "paid")
        
        report_id = f"REP-LIB-{report_type}-{period}"
        
        doc = LibraryReportDocument(
            report_id=report_id,
            tenant_id=tenant_id,
            report_type=report_type,
            period=period,
            total_resources=total_resources,
            available_resources=available_resources,
            total_checkouts=total_checkouts,
            total_returns=total_returns,
            overdue_items=overdue,
            total_fines_collected=total_fines,
            generated_date=datetime.utcnow(),
        )
        
        await doc.insert()
        
        logger.info(
            f"Generated {report_type} library report: {total_resources} resources, "
            f"{overdue} overdue, ${total_fines} fines collected"
        )
        
        return LibraryReport(
            report_id=report_id,
            report_type=report_type,
            period=period,
            total_resources=total_resources,
            available_resources=available_resources,
            total_checkouts=total_checkouts,
            total_returns=total_returns,
            overdue_items=overdue,
            total_fines_collected=total_fines,
            generated_date=doc.generated_date,
        )
    
    async def get_library_overview(
        self,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """Get comprehensive library overview"""
        resources = await LibraryResourceDocument.find(
            LibraryResourceDocument.tenant_id == tenant_id,
            LibraryResourceDocument.status == "active",
        ).to_list()
        
        checkouts = await CheckoutRecordDocument.find(
            CheckoutRecordDocument.tenant_id == tenant_id,
        ).to_list()
        
        now = datetime.utcnow()
        overdue = [c for c in checkouts if c.status == "active" and c.due_date < now]
        
        return {
            "total_resources": len(resources),
            "available_resources": sum(r.available_copies for r in resources),
            "checked_out": sum(r.total_copies - r.available_copies for r in resources),
            "total_checkouts": len(checkouts),
            "active_checkouts": len([c for c in checkouts if c.status == "active"]),
            "overdue_count": len(overdue),
            "resource_types": {
                rt: len([r for r in resources if r.resource_type == rt.value])
                for rt in ResourceType
            }
        }
