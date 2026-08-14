"""
WASSCE Verification Workflow
Items 35-37: Manual WASSCE result verification

Workflow:
1. Applicant submits WASSCE details (exam year, index number, subjects, grades)
2. Applicant uploads result evidence (scanned document)
3. Admissions officer reviews submitted data
4. Officer compares against uploaded evidence
5. Officer verifies manually or requests correction
6. Status tracked: PENDING_VERIFICATION → VERIFIED | REJECTED | REQUIRES_CORRECTION

No WAEC API currently available - this is manual verification.
Design layer for future WAEC API integration.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class VerificationStatus(str, Enum):
    """Status of WASSCE verification."""
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    REJECTED = "rejected"
    REQUIRES_CORRECTION = "requires_correction"


class WAESSEGrade(BaseModel):
    """Individual WASSCE subject result."""
    subject: str  # e.g., "English", "Core Mathematics"
    grade: str    # A1, A2, B2, B3, C4, C5, D7, E8, F9
    evidence: Optional[str] = None  # Path to evidence document if needed


class WAESSSESection(BaseModel):
    """Applicant's submitted WASSCE results."""
    examination_type: str  # "WASSCE", "SSSCE", etc.
    examination_year: int  # 2025, 2024, etc.
    index_number: str
    candidate_name: str
    candidate_dob: Optional[datetime] = None
    subjects: List[WAESSEGrade]
    total_score: Optional[int] = None
    result_document_path: Optional[str] = None  # Scanned/uploaded document


class WAESSSEVerificationRecord(Document):
    """
    WASSCE verification audit record.
    
    Tracks manual verification decisions by admissions officers.
    Enables verification history and appeals.
    """
    
    tenant_id: Indexed(str)
    application_id: Indexed(str)
    applicant_id: Indexed(str)
    
    # Submitted data
    submitted_wassce: WAESSSESection
    submitted_at: datetime
    
    # Verification
    verification_status: Indexed(str) = VerificationStatus.PENDING_VERIFICATION.value
    verified_by: Optional[str] = None  # Officer email
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    
    # Verification details
    subjects_verified: List[str] = []  # Which subjects were verified
    subjects_rejected: List[str] = []  # Which subjects failed verification
    inconsistencies_found: List[str] = []  # Issues noted
    
    # Correction requests
    requires_correction_for: List[str] = []  # Which subjects need correction
    correction_deadline: Optional[datetime] = None
    correction_notes: Optional[str] = None
    
    # Audit
    reviewed_document_path: Optional[str] = None
    review_decision_timestamp: Optional[datetime] = None
    verification_method: str = "manual"  # manual, external_api, hybrid
    
    class Settings:
        collection = "wassce_verification_records"
        indexes = [
            [("tenant_id", 1)],
            [("application_id", 1)],
            [("applicant_id", 1)],
            [("verification_status", 1)],
            [("verified_at", 1)],
        ]


class VerificationRequest(BaseModel):
    """Request to verify WASSCE results."""
    application_id: str
    applicant_id: str
    action: str  # verify, reject, request_correction
    verified_subjects: Optional[List[str]] = None
    rejected_subjects: Optional[List[str]] = None
    inconsistencies: Optional[List[str]] = None
    correction_deadline_days: Optional[int] = 7
    notes: Optional[str] = None


class VerificationResponse(BaseModel):
    """Response from verification."""
    verification_status: str
    verified_at: datetime
    verified_by: str
    message: str
    subjects_verified: List[str]
    subjects_rejected: List[str]
    requires_correction_for: List[str]
    next_steps: List[str]


# ==================== SERVICE ====================

class WAESSSEVerificationService:
    """
    Manual WASSCE verification service.
    
    Current implementation: Manual verification by admissions officer
    Future implementation: Integration with WAEC API (abstract layer ready)
    """
    
    async def submit_wassce(
        self,
        application_id: str,
        applicant_id: str,
        tenant_id: str,
        examination_type: str,
        examination_year: int,
        index_number: str,
        candidate_name: str,
        subjects: List[Dict[str, Any]],
        result_document_path: Optional[str] = None,
    ) -> WAESSSEVerificationRecord:
        """
        Record applicant's submitted WASSCE results.
        
        Creates pending verification record.
        Officer will review and verify later.
        
        Args:
            application_id: Application ID
            applicant_id: Applicant ID
            tenant_id: University
            examination_type: WASSCE, SSSCE, etc.
            examination_year: 2025, 2024, etc.
            index_number: WAEC index number
            candidate_name: Name on result
            subjects: List of {subject, grade}
            result_document_path: Path to uploaded scanned result
        
        Returns:
            WAESSSEVerificationRecord in PENDING_VERIFICATION status
        """
        
        wassce_data = WAESSSESection(
            examination_type=examination_type,
            examination_year=examination_year,
            index_number=index_number,
            candidate_name=candidate_name,
            subjects=[
                WAESSEGrade(subject=s["subject"], grade=s["grade"])
                for s in subjects
            ],
            result_document_path=result_document_path,
        )
        
        record = WAESSSEVerificationRecord(
            tenant_id=tenant_id,
            application_id=application_id,
            applicant_id=applicant_id,
            submitted_wassce=wassce_data,
            submitted_at=datetime.utcnow(),
            verification_status=VerificationStatus.PENDING_VERIFICATION.value,
        )
        
        await record.insert()
        
        logger.info(
            f"📝 WASSCE submitted for {applicant_id}: "
            f"{examination_type} {examination_year}, index {index_number}"
        )
        
        return record
    
    async def get_pending_verifications(
        self,
        tenant_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[WAESSSEVerificationRecord]:
        """Get WASSCE results awaiting officer verification."""
        
        return await WAESSSEVerificationRecord.find(
            WAESSSEVerificationRecord.tenant_id == tenant_id,
            WAESSSEVerificationRecord.verification_status == VerificationStatus.PENDING_VERIFICATION.value,
        ).sort([("submitted_at", 1)]).skip(offset).limit(limit).to_list()
    
    async def verify_wassce(
        self,
        application_id: str,
        verified_by: str,
        subjects_verified: List[str],
        subjects_rejected: Optional[List[str]] = None,
        inconsistencies: Optional[List[str]] = None,
        verification_notes: Optional[str] = None,
    ) -> VerificationResponse:
        """
        Officer verifies WASSCE results.
        
        Args:
            application_id: Application ID
            verified_by: Officer email
            subjects_verified: List of verified subjects
            subjects_rejected: List of rejected subjects
            inconsistencies: List of issues found
            verification_notes: Officer's notes
        
        Returns:
            VerificationResponse with updated status
        """
        
        record = await WAESSSEVerificationRecord.find_one(
            WAESSSEVerificationRecord.application_id == application_id
        )
        if not record:
            raise ValueError(f"Verification record not found: {application_id}")
        
        record.verification_status = VerificationStatus.VERIFIED.value
        record.verified_by = verified_by
        record.verified_at = datetime.utcnow()
        record.verification_notes = verification_notes
        record.subjects_verified = subjects_verified or []
        record.subjects_rejected = subjects_rejected or []
        record.inconsistencies_found = inconsistencies or []
        
        await record.save()
        
        logger.info(
            f"✅ WASSCE VERIFIED for application {application_id} by {verified_by}. "
            f"Verified subjects: {subjects_verified}"
        )
        
        return VerificationResponse(
            verification_status="verified",
            verified_at=record.verified_at,
            verified_by=verified_by,
            message="WASSCE results verified successfully",
            subjects_verified=subjects_verified or [],
            subjects_rejected=subjects_rejected or [],
            requires_correction_for=[],
            next_steps=[
                "Application proceeds to eligibility check",
                "Admissions officer reviews application",
            ]
        )
    
    async def reject_wassce(
        self,
        application_id: str,
        rejected_by: str,
        rejection_reason: str,
        subjects_rejected: List[str],
        rejection_notes: Optional[str] = None,
    ) -> VerificationResponse:
        """
        Officer rejects WASSCE results.
        
        Application cannot proceed until corrected or resubmitted.
        """
        
        record = await WAESSSEVerificationRecord.find_one(
            WAESSSEVerificationRecord.application_id == application_id
        )
        if not record:
            raise ValueError(f"Verification record not found: {application_id}")
        
        record.verification_status = VerificationStatus.REJECTED.value
        record.verified_by = rejected_by
        record.verified_at = datetime.utcnow()
        record.verification_notes = f"REJECTED: {rejection_reason}\n{rejection_notes or ''}"
        record.subjects_rejected = subjects_rejected
        
        await record.save()
        
        logger.warning(
            f"❌ WASSCE REJECTED for application {application_id}. "
            f"Reason: {rejection_reason}"
        )
        
        return VerificationResponse(
            verification_status="rejected",
            verified_at=record.verified_at,
            verified_by=rejected_by,
            message=f"WASSCE results rejected: {rejection_reason}",
            subjects_verified=[],
            subjects_rejected=subjects_rejected,
            requires_correction_for=[],
            next_steps=[
                "Contact admissions office for clarification",
                "Resubmit corrected WASSCE information",
                "Appeal if you believe this is an error",
            ]
        )
    
    async def request_correction(
        self,
        application_id: str,
        officer_email: str,
        subjects_requiring_correction: List[str],
        correction_deadline_days: int = 7,
        correction_notes: Optional[str] = None,
    ) -> VerificationResponse:
        """
        Officer requests applicant to correct WASSCE data.
        
        Applicant has deadline to resubmit corrected information.
        """
        
        record = await WAESSSEVerificationRecord.find_one(
            WAESSSEVerificationRecord.application_id == application_id
        )
        if not record:
            raise ValueError(f"Verification record not found: {application_id}")
        
        deadline = datetime.utcnow()
        from datetime import timedelta
        deadline += timedelta(days=correction_deadline_days)
        
        record.verification_status = VerificationStatus.REQUIRES_CORRECTION.value
        record.verified_by = officer_email
        record.verified_at = datetime.utcnow()
        record.requires_correction_for = subjects_requiring_correction
        record.correction_deadline = deadline
        record.correction_notes = correction_notes
        
        await record.save()
        
        logger.info(
            f"🔄 WASSCE correction requested for application {application_id}. "
            f"Subjects: {subjects_requiring_correction}, Deadline: {deadline}"
        )
        
        return VerificationResponse(
            verification_status="requires_correction",
            verified_at=record.verified_at,
            verified_by=officer_email,
            message=f"WASSCE requires correction for: {', '.join(subjects_requiring_correction)}",
            subjects_verified=[],
            subjects_rejected=[],
            requires_correction_for=subjects_requiring_correction,
            next_steps=[
                f"Resubmit corrected WASSCE information by {deadline.strftime('%Y-%m-%d')}",
                f"Upload new result document",
                "Contact admissions for questions",
            ]
        )
    
    async def get_verification_record(
        self,
        application_id: str,
    ) -> Optional[WAESSSEVerificationRecord]:
        """Get verification record for application."""
        
        return await WAESSSEVerificationRecord.find_one(
            WAESSSEVerificationRecord.application_id == application_id
        )


# ==================== ABSTRACTION FOR FUTURE WAEC API ====================

class ResultVerificationProvider:
    """
    Abstract base for result verification.
    
    Current: ManualVerificationProvider (human review)
    Future: WAECVerificationProvider (official WAEC API)
    """
    
    async def verify_result(
        self,
        index_number: str,
        candidate_name: str,
        examination_year: int,
    ) -> Dict[str, Any]:
        """Verify result against official records."""
        raise NotImplementedError


class ManualVerificationProvider(ResultVerificationProvider):
    """
    Manual verification provider.
    
    Officer reviews submitted documents and marks verified.
    """
    
    async def verify_result(
        self,
        index_number: str,
        candidate_name: str,
        examination_year: int,
    ) -> Dict[str, Any]:
        """Return pending status - requires manual review."""
        return {
            "status": "pending_manual_review",
            "message": "Result awaiting manual officer verification",
            "requires_officer_approval": True,
        }


class WAECVerificationProvider(ResultVerificationProvider):
    """
    Official WAEC API verification provider.
    
    TODO: Implement when WAEC API becomes available.
    """
    
    async def verify_result(
        self,
        index_number: str,
        candidate_name: str,
        examination_year: int,
    ) -> Dict[str, Any]:
        """Verify against official WAEC records."""
        # TODO: Call WAEC API
        # TODO: Return official verification result
        raise NotImplementedError("WAEC API not yet available")
