"""
Result Verification Service - Abstract Base
Section 38: FUTURE WAEC INTEGRATION

Abstract interface for result verification to support:
- Current: ManualVerificationService
- Future: WAECVerificationService
- Future: Any other verification provider
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from enum import Enum
from datetime import datetime


class VerificationStatusEnum(str, Enum):
    """WASSCE verification status throughout the workflow."""
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    REJECTED = "rejected"
    REQUIRES_CORRECTION = "requires_correction"


class ResultVerificationService(ABC):
    """Abstract base class for result verification."""
    
    @abstractmethod
    async def verify_results(
        self,
        applicant_id: str,
        examination_type: str,
        examination_year: int,
        index_number: str,
        subjects: Dict[str, str],  # subject -> grade mapping
    ) -> Dict:
        """
        Verify WASSCE results.
        
        Args:
            applicant_id: ID of applicant
            examination_type: Type of exam (e.g., WASSCE)
            examination_year: Year of examination
            index_number: Student index number
            subjects: Dictionary of subject -> grade mappings
        
        Returns:
            dict with verification result and status
        """
        pass
    
    @abstractmethod
    async def reject_results(
        self,
        applicant_id: str,
        reason: str,
        rejected_by: str,
    ) -> Dict:
        """
        Reject WASSCE results.
        
        Args:
            applicant_id: ID of applicant
            reason: Reason for rejection
            rejected_by: ID of staff member rejecting
        
        Returns:
            dict with rejection status
        """
        pass
    
    @abstractmethod
    async def request_correction(
        self,
        applicant_id: str,
        correction_reason: str,
        requested_by: str,
    ) -> Dict:
        """
        Request applicant to correct/resubmit results.
        
        Args:
            applicant_id: ID of applicant
            correction_reason: Reason for requesting correction
            requested_by: ID of staff member requesting correction
        
        Returns:
            dict with request status
        """
        pass
    
    @abstractmethod
    async def get_verification_status(
        self,
        applicant_id: str,
    ) -> Dict:
        """
        Get current verification status for an applicant.
        
        Returns:
            dict with status, verified_by, verified_at, notes
        """
        pass


class ManualVerificationService(ResultVerificationService):
    """
    Manual verification service.
    Admissions officers manually verify WASSCE results.
    Section 36: WASSCE VERIFICATION WORKFLOW
    """
    
    def __init__(self, applicant_repo):
        self.applicant_repo = applicant_repo
    
    async def verify_results(
        self,
        applicant_id: str,
        examination_type: str,
        examination_year: int,
        index_number: str,
        subjects: Dict[str, str],
        verified_by: str,
        verification_notes: Optional[str] = None,
    ) -> Dict:
        """
        Manually verify WASSCE results.
        Staff member reviews evidence and marks as VERIFIED.
        """
        applicant = await self.applicant_repo.get_by_id(applicant_id)
        if not applicant:
            raise ValueError(f"Applicant {applicant_id} not found")
        
        # Update applicant with verification details
        applicant.verification_status = VerificationStatusEnum.VERIFIED
        applicant.verified_by = verified_by
        applicant.verified_at = datetime.utcnow()
        applicant.verification_notes = verification_notes or ""
        applicant.exam_type = examination_type
        applicant.exam_year = examination_year
        applicant.index_number = index_number
        applicant.results = subjects
        
        applicant = await self.applicant_repo.update(applicant_id, applicant)
        
        return {
            "status": "success",
            "message": "Results verified successfully",
            "applicant_id": applicant_id,
            "verification_status": VerificationStatusEnum.VERIFIED,
            "verified_at": applicant.verified_at.isoformat(),
        }
    
    async def reject_results(
        self,
        applicant_id: str,
        reason: str,
        rejected_by: str,
    ) -> Dict:
        """
        Reject WASSCE results.
        Officer marks as REJECTED with reason.
        """
        applicant = await self.applicant_repo.get_by_id(applicant_id)
        if not applicant:
            raise ValueError(f"Applicant {applicant_id} not found")
        
        applicant.verification_status = VerificationStatusEnum.REJECTED
        applicant.verified_by = rejected_by
        applicant.verified_at = datetime.utcnow()
        applicant.verification_notes = f"Rejected: {reason}"
        
        applicant = await self.applicant_repo.update(applicant_id, applicant)
        
        return {
            "status": "success",
            "message": "Results rejected",
            "applicant_id": applicant_id,
            "verification_status": VerificationStatusEnum.REJECTED,
            "reason": reason,
        }
    
    async def request_correction(
        self,
        applicant_id: str,
        correction_reason: str,
        requested_by: str,
    ) -> Dict:
        """
        Request applicant to correct/resubmit results.
        """
        applicant = await self.applicant_repo.get_by_id(applicant_id)
        if not applicant:
            raise ValueError(f"Applicant {applicant_id} not found")
        
        applicant.verification_status = VerificationStatusEnum.REQUIRES_CORRECTION
        applicant.verified_by = requested_by
        applicant.verified_at = datetime.utcnow()
        applicant.verification_notes = f"Correction needed: {correction_reason}"
        
        applicant = await self.applicant_repo.update(applicant_id, applicant)
        
        return {
            "status": "success",
            "message": "Correction requested from applicant",
            "applicant_id": applicant_id,
            "verification_status": VerificationStatusEnum.REQUIRES_CORRECTION,
            "reason": correction_reason,
        }
    
    async def get_verification_status(
        self,
        applicant_id: str,
    ) -> Dict:
        """
        Get current verification status.
        """
        applicant = await self.applicant_repo.get_by_id(applicant_id)
        if not applicant:
            raise ValueError(f"Applicant {applicant_id} not found")
        
        return {
            "applicant_id": applicant_id,
            "verification_status": getattr(applicant, "verification_status", VerificationStatusEnum.PENDING_VERIFICATION).value,
            "verified_by": getattr(applicant, "verified_by", None),
            "verified_at": getattr(applicant, "verified_at", None),
            "verification_notes": getattr(applicant, "verification_notes", None),
            "exam_type": applicant.exam_type,
            "exam_year": applicant.exam_year,
            "index_number": applicant.index_number,
            "results": applicant.results,
        }
