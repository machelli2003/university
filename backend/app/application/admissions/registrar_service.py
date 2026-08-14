"""
Registrar Dashboard Service
Item 41: Student records management, transcripts, academic standing, transfers

Registrar responsibilities:
- Manage student academic records
- Generate official transcripts
- Track transfers and student movements
- Assess academic standing
- Maintain permanent records
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class TransferType(str, Enum):
    """Transfer types for student movements"""
    INTERNAL_TRANSFER = "internal_transfer"  # Between departments
    EXTERNAL_TRANSFER = "external_transfer"  # From another university
    INTER_LEVEL_TRANSFER = "inter_level_transfer"  # Between study levels


class AcademicStanding(str, Enum):
    """Student academic standing status"""
    GOOD_STANDING = "good_standing"  # Meeting academic requirements
    PROBATION = "probation"  # Below minimum GPA but recoverable
    ACADEMIC_DISMISSAL = "academic_dismissal"  # Failing to meet requirements
    SUSPENDED = "suspended"  # Temporarily suspended
    EXCELLENT = "excellent"  # Exceptional performance


class TranscriptFormat(str, Enum):
    """Transcript output formats"""
    OFFICIAL = "official"  # For external submission
    UNOFFICIAL = "unofficial"  # For student viewing
    DETAILED = "detailed"  # With notes and comments


# ==================== MODELS ====================

class StudentAcademicRecord(BaseModel):
    """Core academic record for student"""
    student_id: str
    programme_id: str
    admission_year: int
    expected_graduation_year: int
    cgpa: float = Field(..., ge=0.0, le=5.0)
    total_units_completed: int
    total_units_required: int
    academic_standing: AcademicStanding = AcademicStanding.GOOD_STANDING
    standing_updated_at: datetime = Field(default_factory=datetime.utcnow)
    current_level: int = 100  # 100, 200, 300, 400 etc
    last_level_completed: int = 100
    on_probation_since: Optional[datetime] = None
    probation_notice_sent_at: Optional[datetime] = None


class Transcript(BaseModel):
    """Official transcript record"""
    transcript_id: str
    student_id: str
    programme_id: str
    date_generated: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str  # Registrar email
    status: str = "generated"
    format_type: TranscriptFormat
    seal_date: Optional[datetime] = None
    sealed_by: Optional[str] = None
    courses: List[Dict[str, Any]] = Field(default_factory=list)  # {code, title, grade, units}
    cgpa_at_graduation: float
    graduation_date: Optional[datetime] = None


class StudentTransfer(BaseModel):
    """Student transfer record"""
    transfer_id: str
    student_id: str
    tenant_id: str = Indexed()
    transfer_type: TransferType
    from_programme_id: str
    to_programme_id: str
    from_department_id: Optional[str] = None
    to_department_id: Optional[str] = None
    transfer_date: datetime = Field(default_factory=datetime.utcnow)
    initiated_by: str
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    reason: str
    units_transferred: int
    cgpa_at_transfer: float
    credit_evaluated: bool = False
    credit_evaluation_notes: Optional[str] = None
    status: str = "pending"  # pending, approved, rejected, completed


class RegistrarAuditLog(BaseModel):
    """Audit trail for registrar actions"""
    action: str
    actor: str  # Registrar email
    student_id: str
    record_type: str  # "academic_record", "transcript", "transfer"
    details: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== DOCUMENTS ====================

class StudentAcademicRecordDocument(Document):
    """Student academic record in database"""
    student_id: str = Indexed()
    tenant_id: str = Indexed()
    programme_id: str = Indexed()
    admission_year: int
    expected_graduation_year: int
    cgpa: float
    total_units_completed: int
    total_units_required: int
    academic_standing: AcademicStanding
    standing_updated_at: datetime
    current_level: int
    last_level_completed: int
    on_probation_since: Optional[datetime] = None
    probation_notice_sent_at: Optional[datetime] = None
    last_gpa_update: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "student_academic_records"


class TranscriptDocument(Document):
    """Generated transcript record"""
    transcript_id: str = Indexed()
    student_id: str = Indexed()
    tenant_id: str = Indexed()
    programme_id: str
    date_generated: datetime
    generated_by: str
    status: str  # generated, sealed, archived
    format_type: str
    seal_date: Optional[datetime] = None
    sealed_by: Optional[str] = None
    courses: List[Dict[str, Any]]
    cgpa_at_graduation: float
    graduation_date: Optional[datetime] = None
    
    class Settings:
        collection = "transcripts"


class StudentTransferDocument(Document):
    """Student transfer records"""
    transfer_id: str = Indexed()
    student_id: str = Indexed()
    tenant_id: str = Indexed()
    transfer_type: str
    from_programme_id: str
    to_programme_id: str
    from_department_id: Optional[str] = None
    to_department_id: Optional[str] = None
    transfer_date: datetime
    initiated_by: str
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    reason: str
    units_transferred: int
    cgpa_at_transfer: float
    credit_evaluated: bool
    credit_evaluation_notes: Optional[str] = None
    status: str
    
    class Settings:
        collection = "student_transfers"


class RegistrarAuditLogDocument(Document):
    """Audit trail for registrar operations"""
    action: str = Indexed()
    actor: str
    student_id: str = Indexed()
    tenant_id: str = Indexed()
    record_type: str
    details: Dict[str, Any]
    created_at: datetime = Indexed()
    
    class Settings:
        collection = "registrar_audit_logs"


# ==================== SERVICE ====================

class RegistrarService:
    """Registrar dashboard operations"""
    
    async def get_student_academic_record(
        self,
        tenant_id: str,
        student_id: str,
    ) -> Optional[StudentAcademicRecord]:
        """Get student's academic record"""
        doc = await StudentAcademicRecordDocument.find_one(
            StudentAcademicRecordDocument.tenant_id == tenant_id,
            StudentAcademicRecordDocument.student_id == student_id,
        )
        
        if not doc:
            return None
        
        return StudentAcademicRecord(
            student_id=doc.student_id,
            programme_id=doc.programme_id,
            admission_year=doc.admission_year,
            expected_graduation_year=doc.expected_graduation_year,
            cgpa=doc.cgpa,
            total_units_completed=doc.total_units_completed,
            total_units_required=doc.total_units_required,
            academic_standing=AcademicStanding(doc.academic_standing),
            standing_updated_at=doc.standing_updated_at,
            current_level=doc.current_level,
            last_level_completed=doc.last_level_completed,
            on_probation_since=doc.on_probation_since,
            probation_notice_sent_at=doc.probation_notice_sent_at,
        )
    
    async def update_academic_standing(
        self,
        tenant_id: str,
        student_id: str,
        cgpa: float,
        min_cgpa_threshold: float = 1.5,
    ) -> StudentAcademicRecord:
        """Update student's academic standing based on CGPA"""
        record = await self.get_student_academic_record(tenant_id, student_id)
        
        if not record:
            raise ValueError(f"Student {student_id} not found")
        
        # Determine standing
        if cgpa >= 4.0:
            standing = AcademicStanding.EXCELLENT
        elif cgpa >= 3.0:
            standing = AcademicStanding.GOOD_STANDING
        elif cgpa >= min_cgpa_threshold:
            standing = AcademicStanding.PROBATION
        else:
            standing = AcademicStanding.ACADEMIC_DISMISSAL
        
        # Update record
        doc = await StudentAcademicRecordDocument.find_one(
            StudentAcademicRecordDocument.tenant_id == tenant_id,
            StudentAcademicRecordDocument.student_id == student_id,
        )
        
        doc.cgpa = cgpa
        doc.academic_standing = standing.value
        doc.standing_updated_at = datetime.utcnow()
        
        if standing == AcademicStanding.PROBATION and doc.on_probation_since is None:
            doc.on_probation_since = datetime.utcnow()
        
        await doc.save()
        
        logger.info(
            f"Updated academic standing for {student_id} in tenant {tenant_id}: {standing.value}"
        )
        
        return StudentAcademicRecord(**doc.dict())
    
    async def generate_transcript(
        self,
        tenant_id: str,
        student_id: str,
        registrar_email: str,
        format_type: TranscriptFormat = TranscriptFormat.UNOFFICIAL,
        courses: Optional[List[Dict[str, Any]]] = None,
    ) -> Transcript:
        """Generate student transcript"""
        record = await self.get_student_academic_record(tenant_id, student_id)
        
        if not record:
            raise ValueError(f"Student {student_id} not found")
        
        transcript_id = f"TR-{student_id}-{datetime.utcnow().timestamp()}"
        
        doc = TranscriptDocument(
            transcript_id=transcript_id,
            student_id=student_id,
            tenant_id=tenant_id,
            programme_id=record.programme_id,
            date_generated=datetime.utcnow(),
            generated_by=registrar_email,
            status="generated",
            format_type=format_type.value,
            courses=courses or [],
            cgpa_at_graduation=record.cgpa,
        )
        
        await doc.insert()
        
        logger.info(
            f"Generated {format_type.value} transcript {transcript_id} for {student_id}"
        )
        
        return Transcript(
            transcript_id=transcript_id,
            student_id=student_id,
            programme_id=record.programme_id,
            date_generated=doc.date_generated,
            generated_by=registrar_email,
            format_type=format_type,
            courses=courses or [],
            cgpa_at_graduation=record.cgpa,
        )
    
    async def seal_transcript(
        self,
        tenant_id: str,
        transcript_id: str,
        registrar_email: str,
    ) -> Transcript:
        """Seal transcript (official certification)"""
        doc = await TranscriptDocument.find_one(
            TranscriptDocument.tenant_id == tenant_id,
            TranscriptDocument.transcript_id == transcript_id,
        )
        
        if not doc:
            raise ValueError(f"Transcript {transcript_id} not found")
        
        doc.status = "sealed"
        doc.seal_date = datetime.utcnow()
        doc.sealed_by = registrar_email
        await doc.save()
        
        logger.info(f"Sealed transcript {transcript_id} by {registrar_email}")
        
        return Transcript(
            transcript_id=doc.transcript_id,
            student_id=doc.student_id,
            programme_id=doc.programme_id,
            date_generated=doc.date_generated,
            generated_by=doc.generated_by,
            status=doc.status,
            format_type=TranscriptFormat(doc.format_type),
            seal_date=doc.seal_date,
            sealed_by=doc.sealed_by,
            courses=doc.courses,
            cgpa_at_graduation=doc.cgpa_at_graduation,
            graduation_date=doc.graduation_date,
        )
    
    async def initiate_transfer(
        self,
        tenant_id: str,
        student_id: str,
        transfer_type: TransferType,
        from_programme_id: str,
        to_programme_id: str,
        reason: str,
        initiated_by: str,
        from_department_id: Optional[str] = None,
        to_department_id: Optional[str] = None,
        units_to_transfer: int = 0,
    ) -> StudentTransfer:
        """Initiate student transfer between programmes/departments"""
        record = await self.get_student_academic_record(tenant_id, student_id)
        
        if not record:
            raise ValueError(f"Student {student_id} not found")
        
        transfer_id = f"TRN-{student_id}-{datetime.utcnow().timestamp()}"
        
        doc = StudentTransferDocument(
            transfer_id=transfer_id,
            student_id=student_id,
            tenant_id=tenant_id,
            transfer_type=transfer_type.value,
            from_programme_id=from_programme_id,
            to_programme_id=to_programme_id,
            from_department_id=from_department_id,
            to_department_id=to_department_id,
            transfer_date=datetime.utcnow(),
            initiated_by=initiated_by,
            reason=reason,
            units_transferred=units_to_transfer,
            cgpa_at_transfer=record.cgpa,
            status="pending",
        )
        
        await doc.insert()
        
        logger.info(
            f"Initiated {transfer_type.value} for {student_id}: {from_programme_id} → {to_programme_id}"
        )
        
        return StudentTransfer(
            transfer_id=transfer_id,
            student_id=student_id,
            tenant_id=tenant_id,
            transfer_type=transfer_type,
            from_programme_id=from_programme_id,
            to_programme_id=to_programme_id,
            from_department_id=from_department_id,
            to_department_id=to_department_id,
            transfer_date=doc.transfer_date,
            initiated_by=initiated_by,
            reason=reason,
            units_transferred=units_to_transfer,
            cgpa_at_transfer=record.cgpa,
        )
    
    async def approve_transfer(
        self,
        tenant_id: str,
        transfer_id: str,
        approved_by: str,
        credit_notes: Optional[str] = None,
    ) -> StudentTransfer:
        """Approve student transfer"""
        doc = await StudentTransferDocument.find_one(
            StudentTransferDocument.tenant_id == tenant_id,
            StudentTransferDocument.transfer_id == transfer_id,
        )
        
        if not doc:
            raise ValueError(f"Transfer {transfer_id} not found")
        
        doc.status = "approved"
        doc.approved_by = approved_by
        doc.approval_date = datetime.utcnow()
        doc.credit_evaluated = True
        doc.credit_evaluation_notes = credit_notes
        await doc.save()
        
        logger.info(f"Approved transfer {transfer_id} by {approved_by}")
        
        return StudentTransfer(**doc.dict())
    
    async def get_students_on_probation(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> List[StudentAcademicRecord]:
        """Get all students currently on academic probation"""
        docs = await StudentAcademicRecordDocument.find(
            StudentAcademicRecordDocument.tenant_id == tenant_id,
            StudentAcademicRecordDocument.academic_standing == AcademicStanding.PROBATION.value,
        ).limit(limit).to_list()
        
        return [
            StudentAcademicRecord(
                student_id=d.student_id,
                programme_id=d.programme_id,
                admission_year=d.admission_year,
                expected_graduation_year=d.expected_graduation_year,
                cgpa=d.cgpa,
                total_units_completed=d.total_units_completed,
                total_units_required=d.total_units_required,
                academic_standing=AcademicStanding(d.academic_standing),
                standing_updated_at=d.standing_updated_at,
                current_level=d.current_level,
                last_level_completed=d.last_level_completed,
                on_probation_since=d.on_probation_since,
            )
            for d in docs
        ]
    
    async def get_academically_dismissed_students(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> List[StudentAcademicRecord]:
        """Get students dismissed for academic reasons"""
        docs = await StudentAcademicRecordDocument.find(
            StudentAcademicRecordDocument.tenant_id == tenant_id,
            StudentAcademicRecordDocument.academic_standing == AcademicStanding.ACADEMIC_DISMISSAL.value,
        ).limit(limit).to_list()
        
        return [StudentAcademicRecord(**d.dict()) for d in docs]
    
    async def get_pending_transfers(
        self,
        tenant_id: str,
    ) -> List[StudentTransfer]:
        """Get pending student transfer requests"""
        docs = await StudentTransferDocument.find(
            StudentTransferDocument.tenant_id == tenant_id,
            StudentTransferDocument.status == "pending",
        ).to_list()
        
        return [StudentTransfer(**d.dict()) for d in docs]
    
    async def get_registrar_audit_log(
        self,
        tenant_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get audit log for registrar actions"""
        docs = await RegistrarAuditLogDocument.find(
            RegistrarAuditLogDocument.tenant_id == tenant_id,
        ).sort([("created_at", -1)]).limit(limit).to_list()
        
        return [d.dict() for d in docs]
    
    async def log_action(
        self,
        tenant_id: str,
        action: str,
        actor: str,
        student_id: str,
        record_type: str,
        details: Dict[str, Any],
    ) -> None:
        """Log registrar action for audit trail"""
        doc = RegistrarAuditLogDocument(
            action=action,
            actor=actor,
            student_id=student_id,
            tenant_id=tenant_id,
            record_type=record_type,
            details=details,
            created_at=datetime.utcnow(),
        )
        
        await doc.insert()
