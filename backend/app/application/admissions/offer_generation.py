"""
Offer Generation Service
Items 19-31: Generate and manage admission offers

Creates:
- Admission offers with conditions
- Offer letters (PDF generation ready)
- Acceptance/rejection tracking
- Offer expiration management
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from beanie import Document, Indexed
from pydantic import BaseModel
import uuid
import logging

logger = logging.getLogger(__name__)


class OfferStatus(str):
    """Offer lifecycle states."""
    GENERATED = "generated"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


@dataclass
class OfferCondition:
    """Admission condition (e.g., min GPA, interview pass)."""
    id: str = None
    condition_type: str  # "academic", "interview", "essay", "health"
    description: str  # e.g., "WASSCE A-Level results"
    due_date: Optional[datetime] = None
    status: str = "pending"  # pending, satisfied, not_satisfied


class AdmissionOffer(Document):
    """
    Generated admission offer for accepted applicant.
    
    Tracks offer status, conditions, and applicant response.
    """
    id: str = None  # Default: UUID
    tenant_id: Indexed(str)
    applicant_id: Indexed(str)
    programme_id: Indexed(str)
    
    # Offer details
    offer_letter_number: str  # e.g., "KNUST-OFFER-2026-001234"
    offer_type: str = "provisional"  # provisional, conditional, unconditional
    
    # Academic info
    intake_period: str  # e.g., "2026/2027 Academic Year"
    expected_start_date: datetime
    
    # Admission conditions
    conditions: List[OfferCondition] = []
    conditions_met: bool = False
    
    # Applicant response
    status: str = "generated"  # generated, sent, accepted, rejected, expired
    acceptance_deadline: datetime
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Financial info
    application_fee_paid: bool = False
    acceptance_fee: Optional[float] = None  # Acceptance fee (if applicable)
    acceptance_fee_due_by: Optional[datetime] = None
    
    # Communication
    sent_to_email: Optional[str] = None
    sent_at: Optional[datetime] = None
    
    # Audit
    generated_by: Optional[str] = None  # Admissions officer
    generated_at: datetime = None
    updated_at: datetime = None
    
    class Settings:
        collection = "admission_offers"
        indexes = [
            [("tenant_id", 1)],
            [("applicant_id", 1)],
            [("programme_id", 1)],
            [("status", 1)],
            [("acceptance_deadline", 1)],
        ]


class OfferSchema(BaseModel):
    """Schema for offer API."""
    id: str
    applicant_id: str
    programme_id: str
    offer_letter_number: str
    offer_type: str
    status: str
    expected_start_date: datetime
    acceptance_deadline: datetime
    conditions: List[Dict[str, Any]]
    accepted_at: Optional[datetime]


class GenerateOfferRequest(BaseModel):
    """Request to generate offers."""
    applicant_ids: List[str]
    programme_id: str
    offer_type: str = "provisional"  # provisional or conditional
    conditions: List[Dict[str, Any]] = []
    acceptance_deadline_days: int = 14  # Days from now


class OfferGenerationService:
    """
    Generate and manage admission offers.
    
    Creates offers for:
    - Qualified applicants
    - Admitted via merit ranking
    - Allocated to programmes
    """
    
    def __init__(self):
        self.offer_counter = 1000  # For offer letter numbering
    
    async def generate_offers(
        self,
        tenant_id: str,
        allocated_applicants: List[Dict[str, Any]],
        programme_id: str,
        offer_type: str = "provisional",
        conditions: List[Dict[str, Any]] = None,
        days_until_deadline: int = 14,
        generated_by: Optional[str] = None,
    ) -> List[AdmissionOffer]:
        """
        Generate admission offers for allocated applicants.
        
        Args:
            tenant_id: University tenant
            allocated_applicants: List of applicants to offer admission
            programme_id: Programme being offered
            offer_type: provisional (conditional) or unconditional
            conditions: Admission conditions (if conditional)
            days_until_deadline: Days for applicant to accept
            generated_by: Admissions officer ID
        
        Returns:
            List of created AdmissionOffer documents
        """
        offers = []
        
        for applicant in allocated_applicants:
            # Generate unique offer letter number
            offer_number = await self._generate_offer_number(tenant_id)
            
            # Create conditions
            offer_conditions = []
            if conditions:
                for cond in conditions:
                    condition = OfferCondition(
                        id=str(uuid.uuid4()),
                        condition_type=cond.get("type", "academic"),
                        description=cond.get("description"),
                        due_date=cond.get("due_date"),
                    )
                    offer_conditions.append(condition)
            
            # Calculate dates
            now = datetime.utcnow()
            acceptance_deadline = now + timedelta(days=days_until_deadline)
            expected_start_date = self._get_semester_start_date()
            
            # Create offer
            offer = AdmissionOffer(
                tenant_id=tenant_id,
                applicant_id=applicant["id"],
                programme_id=programme_id,
                offer_letter_number=offer_number,
                offer_type=offer_type,
                conditions=offer_conditions,
                acceptance_deadline=acceptance_deadline,
                expected_start_date=expected_start_date,
                generated_by=generated_by,
                generated_at=now,
                updated_at=now,
            )
            
            await offer.save()
            offers.append(offer)
            
            logger.info(f"✅ Offer {offer_number} generated for applicant {applicant['id']}")
        
        return offers
    
    async def send_offer(
        self,
        offer_id: str,
        tenant_id: str,
        recipient_email: str,
    ) -> Dict[str, Any]:
        """
        Send offer letter to applicant (email).
        
        In production, this would:
        1. Generate PDF from template
        2. Send via email service
        3. Update offer status
        """
        offer = await AdmissionOffer.find_one(
            AdmissionOffer.id == offer_id,
            AdmissionOffer.tenant_id == tenant_id,
        )
        
        if not offer:
            return {"success": False, "error": "Offer not found"}
        
        # TODO: Generate PDF
        # TODO: Send email
        
        offer.sent_to_email = recipient_email
        offer.sent_at = datetime.utcnow()
        offer.status = "sent"
        await offer.save()
        
        logger.info(f"📧 Offer {offer.offer_letter_number} sent to {recipient_email}")
        return {
            "success": True,
            "offer_id": offer_id,
            "sent_to": recipient_email,
            "sent_at": offer.sent_at,
        }
    
    async def accept_offer(
        self,
        offer_id: str,
        tenant_id: str,
        applicant_id: str,
    ) -> Optional[AdmissionOffer]:
        """
        Record applicant's acceptance of offer.
        
        Triggers:
        - Status update to "accepted"
        - Enrollment process initiation
        - Student ID generation
        """
        offer = await AdmissionOffer.find_one(
            AdmissionOffer.id == offer_id,
            AdmissionOffer.tenant_id == tenant_id,
            AdmissionOffer.applicant_id == applicant_id,
        )
        
        if not offer:
            logger.warning(f"❌ Offer {offer_id} not found for applicant {applicant_id}")
            return None
        
        if offer.status == "accepted":
            logger.info(f"ℹ️ Offer already accepted")
            return offer
        
        if offer.acceptance_deadline < datetime.utcnow():
            offer.status = "expired"
            await offer.save()
            logger.warning(f"⏰ Offer {offer_id} has expired")
            return None
        
        offer.status = "accepted"
        offer.accepted_at = datetime.utcnow()
        offer.updated_at = datetime.utcnow()
        await offer.save()
        
        logger.info(f"✅ Applicant {applicant_id} accepted offer {offer.offer_letter_number}")
        return offer
    
    async def reject_offer(
        self,
        offer_id: str,
        tenant_id: str,
        applicant_id: str,
        rejection_reason: Optional[str] = None,
    ) -> Optional[AdmissionOffer]:
        """Record applicant's rejection of offer."""
        offer = await AdmissionOffer.find_one(
            AdmissionOffer.id == offer_id,
            AdmissionOffer.tenant_id == tenant_id,
            AdmissionOffer.applicant_id == applicant_id,
        )
        
        if not offer:
            return None
        
        offer.status = "rejected"
        offer.rejected_at = datetime.utcnow()
        offer.rejection_reason = rejection_reason
        offer.updated_at = datetime.utcnow()
        await offer.save()
        
        logger.info(f"❌ Applicant {applicant_id} rejected offer {offer.offer_letter_number}")
        return offer
    
    async def check_offer_expiry(
        self,
        offer_id: str,
        tenant_id: str,
    ) -> bool:
        """Check if offer has expired."""
        offer = await AdmissionOffer.find_one(
            AdmissionOffer.id == offer_id,
            AdmissionOffer.tenant_id == tenant_id,
        )
        
        if not offer:
            return False
        
        if offer.status in ["accepted", "rejected", "expired"]:
            return False  # Already finalized
        
        if offer.acceptance_deadline < datetime.utcnow():
            offer.status = "expired"
            offer.updated_at = datetime.utcnow()
            await offer.save()
            logger.info(f"⏰ Offer {offer.offer_letter_number} marked as expired")
            return True
        
        return False
    
    async def _generate_offer_number(self, tenant_id: str) -> str:
        """Generate unique offer letter number."""
        # Format: TENANT-OFFER-YEAR-SEQUENCE
        year = datetime.now().year
        sequence = self.offer_counter
        self.offer_counter += 1
        
        return f"{tenant_id[:8]}-OFFER-{year}-{sequence:06d}"
    
    @staticmethod
    def _get_semester_start_date() -> datetime:
        """Get expected semester start date (e.g., next September)."""
        now = datetime.now()
        if now.month < 9:
            # Same year
            return datetime(now.year, 9, 15)
        else:
            # Next year
            return datetime(now.year + 1, 9, 15)


class OfferRepository:
    """Database operations for offers."""
    
    async def get_pending_offers(
        self,
        tenant_id: str,
    ) -> List[AdmissionOffer]:
        """Get all offers awaiting applicant response."""
        return await AdmissionOffer.find(
            AdmissionOffer.tenant_id == tenant_id,
            AdmissionOffer.status == "sent",
        ).to_list()
    
    async def get_expiring_offers(
        self,
        tenant_id: str,
        days_until_expiry: int = 3,
    ) -> List[AdmissionOffer]:
        """Get offers expiring soon (for reminder emails)."""
        threshold = datetime.utcnow() + timedelta(days=days_until_expiry)
        
        return await AdmissionOffer.find(
            AdmissionOffer.tenant_id == tenant_id,
            AdmissionOffer.status == "sent",
            AdmissionOffer.acceptance_deadline <= threshold,
        ).to_list()
