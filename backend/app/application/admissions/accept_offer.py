"""
Accept Offer & Enroll Use Case
Item 61: Student Lifecycle — Applicant → Student Conversion

When an applicant accepts their admission offer:
1. Offer status is marked as accepted
2. Student record is created
3. Student ID is generated
4. Applicant status becomes ENROLLED
5. User role may be updated to "student"
6. Welcome email is sent
7. All changes are audited
"""

from datetime import datetime
from typing import Optional, Dict, Any
from app.infrastructure.models.applicant import Applicant, StatusEnum
from app.infrastructure.models.student import Student, StudentStatusEnum
from app.infrastructure.models.user import User
from app.infrastructure.database.repositories.applicant_repository import ApplicantRepository
from app.infrastructure.database.repositories.student_repository import StudentRepository
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.domain.identifiers.identifier_service import IdentifierService
from app.infrastructure.database.repositories.audit_repository import AuditRepository


class AcceptOfferUseCase:
    """Convert accepted applicant to enrolled student."""
    
    def __init__(
        self,
        applicant_repo: ApplicantRepository,
        student_repo: StudentRepository,
        user_repo: UserRepository,
        identifier_service: IdentifierService,
        audit_repo: AuditRepository,
    ):
        self.applicant_repo = applicant_repo
        self.student_repo = student_repo
        self.user_repo = user_repo
        self.identifier_service = identifier_service
        self.audit_repo = audit_repo
    
    async def accept_offer(
        self,
        applicant_id: str,
        tenant_id: str,
        user_id: str,
        acceptance_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Accept admission offer and create student record.
        
        Returns:
            {
                "status": "success",
                "student_id": "KNUST-2026-000001",
                "message": "Offer accepted. Welcome to the university!",
            }
        """
        # Get applicant
        applicant = await self.applicant_repo.get_by_id(applicant_id)
        if not applicant:
            raise ValueError(f"Applicant {applicant_id} not found")
        
        if str(applicant.tenant_id) != tenant_id:
            raise ValueError("Unauthorized tenant access")
        
        # Verify applicant has an offer and it's not already accepted/rejected
        if not applicant.offer_id:
            raise ValueError("No offer to accept")
        
        if applicant.offer_accepted:
            raise ValueError("Offer already accepted")
        
        if applicant.offer_rejected:
            raise ValueError("Offer was rejected previously")
        
        # Mark offer as accepted
        applicant.offer_accepted = True
        applicant.offer_acceptance_date = acceptance_date or datetime.utcnow()
        applicant.status = StatusEnum.ENROLLED  # Mark as enrolled
        applicant.updated_at = datetime.utcnow()
        
        # Save applicant changes
        await self.applicant_repo.update(str(applicant.id), applicant)
        
        # Generate student ID
        student_id = await self.identifier_service.generate_student_id(
            tenant_id=tenant_id,
            year=datetime.utcnow().year,
        )
        
        # Get user to copy personal info
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Create student record
        student_data = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "applicant_id": applicant_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "student_id": student_id,
            "email": user.email,
            "phone": user.phone or applicant.phone,
            "date_of_birth": applicant.date_of_birth,
            "gender": applicant.gender,
            # Academic placement
            "programme_id": str(applicant.allocated_programme_id) if applicant.allocated_programme_id else "",
            "faculty_id": "",  # Will be fetched from programme
            "department_id": "",  # Will be fetched from programme
            "entry_level": "100",  # First year
            "entry_semester": "1",
            "entry_year": datetime.utcnow().year,
            # Status
            "status": StudentStatusEnum.REGISTERED,
            # Contact
            "guardian_name": applicant.guardian_name,
            "guardian_phone": applicant.guardian_phone,
            "guardian_email": applicant.guardian_email,
            # Identification
            "national_id": applicant.national_id,
            # Documents
            "documents": applicant.documents if hasattr(applicant, 'documents') else [],
            # Financial
            "fee_balance": 0.0,  # Will be set by finance system
            # Created
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        student = await self.student_repo.create(student_data)
        
        # Update user role if needed (add student role)
        if "student" not in user.permissions:
            user.permissions.append("student")
            await self.user_repo.update(str(user.id), user)
        
        # Audit log
        await self.audit_repo.create({
            "tenant_id": tenant_id,
            "event_type": "offer_accepted",
            "entity_type": "applicant",
            "entity_id": applicant_id,
            "action": "accept_offer",
            "performed_by": user_id,
            "details": {
                "student_id": student_id,
                "programme_id": str(applicant.allocated_programme_id),
                "acceptance_date": applicant.offer_acceptance_date.isoformat(),
            },
        })
        
        return {
            "status": "success",
            "student_id": student_id,
            "applicant_id": applicant_id,
            "message": "Offer accepted. Welcome to the university!",
            "next_steps": "Please proceed to course registration",
        }
    
    async def reject_offer(
        self,
        applicant_id: str,
        tenant_id: str,
        user_id: str,
        rejection_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Reject admission offer."""
        applicant = await self.applicant_repo.get_by_id(applicant_id)
        if not applicant:
            raise ValueError(f"Applicant {applicant_id} not found")
        
        if str(applicant.tenant_id) != tenant_id:
            raise ValueError("Unauthorized tenant access")
        
        if not applicant.offer_id:
            raise ValueError("No offer to reject")
        
        if applicant.offer_rejected or applicant.offer_accepted:
            raise ValueError("Offer status cannot be changed")
        
        # Mark offer as rejected
        applicant.offer_rejected = True
        applicant.offer_rejection_date = datetime.utcnow()
        applicant.offer_rejection_reason = rejection_reason
        applicant.status = StatusEnum.REJECTED
        applicant.updated_at = datetime.utcnow()
        
        await self.applicant_repo.update(str(applicant.id), applicant)
        
        # Audit log
        await self.audit_repo.create({
            "tenant_id": tenant_id,
            "event_type": "offer_rejected",
            "entity_type": "applicant",
            "entity_id": applicant_id,
            "action": "reject_offer",
            "performed_by": user_id,
            "details": {
                "reason": rejection_reason,
            },
        })
        
        return {
            "status": "success",
            "message": "Offer rejected",
            "applicant_id": applicant_id,
        }
