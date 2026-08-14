"""
University Activation Workflow
Item 32: Transition from APPROVED -> PROVISIONING -> ACTIVE

Process:
1. Super admin approves university (status = APPROVED)
2. System starts provisioning (status = PROVISIONING)
3. Provisioning tasks:
   - Initialize tenant-specific indices in database
   - Create default admin account
   - Configure system defaults
   - Set up initial tenant data
   - Initialize audit log
   - Create sample data (optional)
4. Upon completion, status = ACTIVE
5. University can now be used

Provisioning is either:
- Automatic: Triggered when approval given
- Manual: University admin clicks "Activate" button (requires verification)
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ProvisioningTask(str, Enum):
    """Individual provisioning task."""
    CREATE_INDICES = "create_indices"
    CREATE_DEFAULT_ADMIN = "create_default_admin"
    INITIALIZE_CONFIGS = "initialize_configs"
    SETUP_AUDIT_LOG = "setup_audit_log"
    CREATE_SAMPLE_DATA = "create_sample_data"
    SEND_ACTIVATION_EMAIL = "send_activation_email"


class ProvisioningStatus(BaseModel):
    """Status of provisioning task."""
    task: str
    status: str  # pending, in_progress, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None


class UniversityActivationRequest(BaseModel):
    """Request to activate university."""
    confirmation_code: Optional[str] = None  # For manual activation
    activate_sample_data: bool = False


class UniversityActivationResponse(BaseModel):
    """Response to activation."""
    tenant_id: str
    status: str
    activated_at: Optional[datetime]
    message: str
    admin_dashboard_url: Optional[str] = None
    support_contact: Optional[str] = None


class ProvisioningLog(Document):
    """Log of university provisioning."""
    
    tenant_id: Indexed(str)
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str  # in_progress, completed, failed
    
    # Task tracking
    tasks: List[ProvisioningStatus] = []
    failed_tasks: List[str] = []
    
    # Details
    provisioning_type: str = "automatic"  # automatic, manual
    initiated_by: Optional[str] = None  # Super admin or system
    notes: Optional[str] = None
    
    # Results
    total_duration_seconds: Optional[float] = None
    errors: List[Dict[str, Any]] = []
    
    class Settings:
        collection = "provisioning_logs"
        indexes = [
            [("tenant_id", 1)],
            [("started_at", 1)],
            [("status", 1)],
        ]


# ==================== SCHEMAS ====================

class ActivationChecklistItem(BaseModel):
    """Item in activation checklist."""
    task: str
    name: str
    description: str
    status: str
    completed_at: Optional[datetime] = None


class ActivationStatusResponse(BaseModel):
    """Current activation status."""
    tenant_id: str
    status: str  # pending, provisioning, active
    checklist: List[ActivationChecklistItem]
    completion_percentage: int
    estimated_time_remaining: Optional[int] = None  # seconds


# ==================== SERVICE ====================

class UniversityActivationService:
    """
    Handle university activation.
    
    After super admin approval, system provisions university:
    - Creates database indices
    - Sets up default admin
    - Initializes configuration
    - Sets up audit logging
    - Optionally creates sample data
    """
    
    async def provision_university(
        self,
        tenant_id: str,
        initiated_by: Optional[str] = None,
        include_sample_data: bool = False,
    ) -> UniversityActivationResponse:
        """
        Begin university provisioning.
        
        Transition: APPROVED -> PROVISIONING -> ACTIVE
        
        Args:
            tenant_id: University to provision
            initiated_by: Who initiated (super admin email or 'system')
            include_sample_data: Whether to populate sample data
        
        Returns:
            UniversityActivationResponse
        """
        from app.application.admin.setup_submission import (
            UniversityApplicationDocument, UniversityApplicationStatus
        )
        
        app = await UniversityApplicationDocument.find_one(
            UniversityApplicationDocument.tenant_id == tenant_id
        )
        if not app:
            raise ValueError(f"University not found: {tenant_id}")
        
        if app.status != UniversityApplicationStatus.APPROVED:
            raise ValueError(
                f"Cannot provision: university status is {app.status.value}, "
                f"expected {UniversityApplicationStatus.APPROVED.value}"
            )
        
        # Update application status
        app.status = UniversityApplicationStatus.PROVISIONING
        app.provisioning_started_at = datetime.utcnow()
        app.updated_at = datetime.utcnow()
        await app.save()
        
        # Create provisioning log
        log = ProvisioningLog(
            tenant_id=tenant_id,
            started_at=datetime.utcnow(),
            provisioning_type="automatic",
            initiated_by=initiated_by or "system",
        )
        
        try:
            # Execute provisioning tasks
            await self._execute_provisioning_tasks(
                tenant_id=tenant_id,
                log=log,
                include_sample_data=include_sample_data,
            )
            
            # Mark as complete
            log.status = "completed"
            log.completed_at = datetime.utcnow()
            log.total_duration_seconds = (
                log.completed_at - log.started_at
            ).total_seconds()
            await log.insert()
            
            # Activate university
            app.status = UniversityApplicationStatus.ACTIVE
            app.activated_at = datetime.utcnow()
            app.activated_by = initiated_by or "system"
            app.provisioning_completed_at = datetime.utcnow()
            app.updated_at = datetime.utcnow()
            await app.save()
            
            logger.info(
                f"✅ {app.name} ({tenant_id}) ACTIVATED successfully. "
                f"Provisioning took {log.total_duration_seconds:.1f}s"
            )
            
            # TODO: Send activation email
            
            return UniversityActivationResponse(
                tenant_id=tenant_id,
                status="active",
                activated_at=app.activated_at,
                message=f"{app.name} is now active and ready to use!",
                admin_dashboard_url=f"https://eump.local/admin/{tenant_id}/dashboard",
                support_contact="support@eump.local",
            )
        
        except Exception as e:
            # Provisioning failed
            log.status = "failed"
            log.completed_at = datetime.utcnow()
            log.total_duration_seconds = (
                log.completed_at - log.started_at
            ).total_seconds()
            log.errors = [{
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }]
            await log.insert()
            
            # Revert application status
            app.status = UniversityApplicationStatus.APPROVED
            app.updated_at = datetime.utcnow()
            await app.save()
            
            logger.error(
                f"❌ Provisioning failed for {tenant_id}: {str(e)}"
            )
            
            raise ValueError(f"Provisioning failed: {str(e)}")
    
    async def _execute_provisioning_tasks(
        self,
        tenant_id: str,
        log: ProvisioningLog,
        include_sample_data: bool = False,
    ) -> None:
        """Execute individual provisioning tasks."""
        
        tasks = [
            (ProvisioningTask.CREATE_INDICES.value, self._create_database_indices),
            (ProvisioningTask.CREATE_DEFAULT_ADMIN.value, self._create_default_admin),
            (ProvisioningTask.INITIALIZE_CONFIGS.value, self._initialize_configs),
            (ProvisioningTask.SETUP_AUDIT_LOG.value, self._setup_audit_log),
        ]
        
        if include_sample_data:
            tasks.append(
                (ProvisioningTask.CREATE_SAMPLE_DATA.value, self._create_sample_data)
            )
        
        tasks.append(
            (ProvisioningTask.SEND_ACTIVATION_EMAIL.value, self._send_activation_email)
        )
        
        for task_name, task_func in tasks:
            status = ProvisioningStatus(
                task=task_name,
                status="in_progress",
                started_at=datetime.utcnow(),
            )
            
            try:
                await task_func(tenant_id)
                status.status = "completed"
                status.completed_at = datetime.utcnow()
                status.duration_seconds = (
                    status.completed_at - status.started_at
                ).total_seconds()
                
                logger.info(
                    f"  ✅ {task_name}: {status.duration_seconds:.2f}s"
                )
            
            except Exception as e:
                status.status = "failed"
                status.completed_at = datetime.utcnow()
                status.error_message = str(e)
                status.duration_seconds = (
                    status.completed_at - status.started_at
                ).total_seconds()
                
                logger.error(
                    f"  ❌ {task_name} failed: {str(e)}"
                )
                
                log.failed_tasks.append(task_name)
                log.errors.append({
                    "task": task_name,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                })
                
                # Continue with other tasks even if one fails
            
            log.tasks.append(status)
    
    async def _create_database_indices(self, tenant_id: str) -> None:
        """Create tenant-specific database indices."""
        # TODO: Create indices for all collections
        # - applicants: index on (tenant_id, status, created_at)
        # - students: index on (tenant_id, student_id, programme_id)
        # - staff: index on (tenant_id, staff_id, department)
        # - payments: index on (tenant_id, status, due_date)
        # etc.
        logger.debug(f"Creating database indices for {tenant_id}")
    
    async def _create_default_admin(self, tenant_id: str) -> None:
        """Create default super admin account for university."""
        # TODO: Create super_admin user with temporary password
        # Send password reset link to admin email
        logger.debug(f"Creating default admin for {tenant_id}")
    
    async def _initialize_configs(self, tenant_id: str) -> None:
        """Initialize system configuration defaults."""
        # TODO: Create default configurations for:
        # - GradeConfiguration
        # - FinanceConfiguration
        # - AcademicCalendar
        # - etc.
        logger.debug(f"Initializing configurations for {tenant_id}")
    
    async def _setup_audit_log(self, tenant_id: str) -> None:
        """Set up audit logging for tenant."""
        # TODO: Initialize audit log collection
        # Create initial audit entry for activation
        logger.debug(f"Setting up audit logging for {tenant_id}")
    
    async def _create_sample_data(self, tenant_id: str) -> None:
        """Optionally create sample data (colleges, programmes, courses)."""
        # TODO: Create sample academic structure if requested
        logger.debug(f"Creating sample data for {tenant_id}")
    
    async def _send_activation_email(self, tenant_id: str) -> None:
        """Send activation confirmation email to university admin."""
        from app.application.admin.setup_submission import UniversityApplicationDocument
        
        app = await UniversityApplicationDocument.find_one(
            UniversityApplicationDocument.tenant_id == tenant_id
        )
        if app:
            logger.debug(
                f"Sending activation email to {app.admin_email}"
            )
            # TODO: Send email via EmailService
    
    async def get_activation_status(
        self,
        tenant_id: str,
    ) -> ActivationStatusResponse:
        """Get current activation status and checklist."""
        from app.application.admin.setup_submission import UniversityApplicationDocument
        
        app = await UniversityApplicationDocument.find_one(
            UniversityApplicationDocument.tenant_id == tenant_id
        )
        if not app:
            raise ValueError(f"University not found: {tenant_id}")
        
        # Get provisioning log if provisioning is in progress or complete
        log = await ProvisioningLog.find_one(
            ProvisioningLog.tenant_id == tenant_id
        ).sort([("started_at", -1)])
        
        checklist = []
        completion_percentage = 0
        
        if log:
            for task in log.tasks:
                checklist.append(ActivationChecklistItem(
                    task=task.task,
                    name=task.task.replace("_", " ").title(),
                    description="",
                    status=task.status,
                    completed_at=task.completed_at,
                ))
            
            completed = sum(1 for t in log.tasks if t.status == "completed")
            completion_percentage = int((completed / len(log.tasks)) * 100) if log.tasks else 0
        
        return ActivationStatusResponse(
            tenant_id=tenant_id,
            status=app.status.value,
            checklist=checklist,
            completion_percentage=completion_percentage,
        )
