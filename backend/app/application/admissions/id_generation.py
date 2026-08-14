"""
ID Configuration & Generation Service
Items 19-31: Configure and generate Student, Staff, and Applicant IDs

Each university configures:
- ID format patterns
- Prefix/suffix
- Sequence numbering
- Uniqueness rules
- Academic year inclusion
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from beanie import Document, Indexed
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class IDConfigurationDocument(Document):
    """Configure ID generation rules per university."""
    
    tenant_id: Indexed(str)
    
    # Student ID Config
    student_id_format: str = "{PREFIX}-STU-{YEAR}-{SEQUENCE}"  # e.g., KNUST-STU-2024-000001
    student_id_prefix: str = "KNUST"
    student_id_include_year: bool = True
    student_id_include_department: bool = False
    student_id_department_mapping: Dict[str, str] = {}  # e.g., {"CS": "01", "ENG": "02"}
    student_id_next_sequence: int = 1
    student_id_reset_yearly: bool = True
    
    # Staff ID Config
    staff_id_format: str = "{PREFIX}-STF-{SEQUENCE}"  # e.g., KNUST-STF-000001
    staff_id_prefix: str = "KNUST"
    staff_id_include_department: bool = False
    staff_id_department_mapping: Dict[str, str] = {}
    staff_id_next_sequence: int = 1
    
    # Applicant ID Config
    applicant_id_format: str = "{PREFIX}-APP-{YEAR}-{SEQUENCE}"
    applicant_id_prefix: str = "KNUST"
    applicant_id_include_cycle: bool = True
    applicant_id_next_sequence: int = 1
    applicant_id_reset_yearly: bool = True
    
    # Audit
    configured_by: Optional[str] = None
    configured_at: datetime = None
    updated_at: datetime = None
    
    class Settings:
        collection = "id_configurations"
        indexes = [
            [("tenant_id", 1)],
        ]


class StudentIDRequest(BaseModel):
    """Request to generate student ID."""
    student_record_id: str
    first_name: str
    last_name: str
    department_id: Optional[str] = None
    academic_year: Optional[int] = None


class StaffIDRequest(BaseModel):
    """Request to generate staff ID."""
    staff_record_id: str
    first_name: str
    last_name: str
    department_id: Optional[str] = None
    staff_type: str  # lecturer, registrar, etc.


class ApplicantIDRequest(BaseModel):
    """Request to generate applicant ID."""
    applicant_record_id: str
    admission_cycle_id: str


@dataclass
class GeneratedID:
    """Generated ID and associated metadata."""
    id_string: str  # The actual generated ID
    record_id: str  # MongoDB record ID
    id_type: str  # student, staff, applicant
    generated_at: datetime
    pattern_used: str


class IDGenerationService:
    """
    Generate Student, Staff, and Applicant IDs.
    
    Per-university configuration ensures:
    - Consistent naming
    - Uniqueness
    - Meaningful IDs that encode metadata
    """
    
    async def generate_student_id(
        self,
        tenant_id: str,
        student_record_id: str,
        first_name: str,
        last_name: str,
        department_id: Optional[str] = None,
        academic_year: Optional[int] = None,
    ) -> GeneratedID:
        """
        Generate Student ID.
        
        Example: KNUST-STU-2024-000001
        or: KNUST-STU-01-000001 (with department code)
        
        Args:
            tenant_id: University
            student_record_id: MongoDB student record ID
            first_name: Student first name
            last_name: Student last name
            department_id: Optional department (for department-coded IDs)
            academic_year: Academic year (e.g., 2024)
        
        Returns:
            GeneratedID with the generated ID string
        """
        config = await self._get_config(tenant_id)
        if not config:
            raise ValueError(f"ID configuration not found for tenant {tenant_id}")
        
        # Get next sequence
        sequence = config.student_id_next_sequence
        
        # Build ID from template
        id_string = config.student_id_format
        
        # Replace template variables
        id_string = id_string.replace("{PREFIX}", config.student_id_prefix)
        
        if config.student_id_include_year and academic_year:
            id_string = id_string.replace("{YEAR}", str(academic_year))
        else:
            id_string = id_string.replace("-{YEAR}", "")
        
        if config.student_id_include_department and department_id:
            dept_code = config.student_id_department_mapping.get(
                department_id,
                department_id[:2].upper()
            )
            id_string = id_string.replace("{DEPT}", dept_code)
        else:
            id_string = id_string.replace("-{DEPT}", "")
        
        id_string = id_string.replace("{SEQUENCE}", f"{sequence:06d}")
        
        # Increment sequence
        config.student_id_next_sequence = sequence + 1
        if config.student_id_reset_yearly:
            # Check if year changed - reset if so
            pass  # TODO: Implement yearly reset
        
        await config.save()
        
        logger.info(f"✅ Student ID generated: {id_string}")
        
        return GeneratedID(
            id_string=id_string,
            record_id=student_record_id,
            id_type="student",
            generated_at=datetime.utcnow(),
            pattern_used=config.student_id_format,
        )
    
    async def generate_staff_id(
        self,
        tenant_id: str,
        staff_record_id: str,
        first_name: str,
        last_name: str,
        department_id: Optional[str] = None,
        staff_type: str = "lecturer",
    ) -> GeneratedID:
        """
        Generate Staff ID.
        
        Example: KNUST-STF-000001
        """
        config = await self._get_config(tenant_id)
        if not config:
            raise ValueError(f"ID configuration not found for tenant {tenant_id}")
        
        sequence = config.staff_id_next_sequence
        
        id_string = config.staff_id_format
        id_string = id_string.replace("{PREFIX}", config.staff_id_prefix)
        id_string = id_string.replace("{SEQUENCE}", f"{sequence:06d}")
        
        config.staff_id_next_sequence = sequence + 1
        await config.save()
        
        logger.info(f"✅ Staff ID generated: {id_string}")
        
        return GeneratedID(
            id_string=id_string,
            record_id=staff_record_id,
            id_type="staff",
            generated_at=datetime.utcnow(),
            pattern_used=config.staff_id_format,
        )
    
    async def generate_applicant_id(
        self,
        tenant_id: str,
        applicant_record_id: str,
        admission_cycle_id: str,
    ) -> GeneratedID:
        """
        Generate Applicant ID.
        
        Example: KNUST-APP-2024-000001
        (Fresh for each admission cycle)
        """
        config = await self._get_config(tenant_id)
        if not config:
            raise ValueError(f"ID configuration not found for tenant {tenant_id}")
        
        sequence = config.applicant_id_next_sequence
        year = datetime.now().year
        
        id_string = config.applicant_id_format
        id_string = id_string.replace("{PREFIX}", config.applicant_id_prefix)
        id_string = id_string.replace("{YEAR}", str(year))
        id_string = id_string.replace("{SEQUENCE}", f"{sequence:06d}")
        
        config.applicant_id_next_sequence = sequence + 1
        await config.save()
        
        logger.info(f"✅ Applicant ID generated: {id_string}")
        
        return GeneratedID(
            id_string=id_string,
            record_id=applicant_record_id,
            id_type="applicant",
            generated_at=datetime.utcnow(),
            pattern_used=config.applicant_id_format,
        )
    
    async def _get_config(
        self,
        tenant_id: str,
    ) -> Optional[IDConfigurationDocument]:
        """Get ID configuration for tenant."""
        config = await IDConfigurationDocument.find_one(
            IDConfigurationDocument.tenant_id == tenant_id,
        )
        
        if not config:
            # Create default config
            config = IDConfigurationDocument(
                tenant_id=tenant_id,
                configured_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            await config.save()
            logger.info(f"📝 Default ID configuration created for {tenant_id}")
        
        return config


class IDConfigurationService:
    """Allow universities to configure ID generation."""
    
    async def configure_student_ids(
        self,
        tenant_id: str,
        id_format: str,
        prefix: str,
        include_year: bool = True,
        include_department: bool = False,
        department_mapping: Optional[Dict[str, str]] = None,
        reset_yearly: bool = True,
        configured_by: Optional[str] = None,
    ) -> IDConfigurationDocument:
        """Configure Student ID generation."""
        config = await IDConfigurationDocument.find_one(
            IDConfigurationDocument.tenant_id == tenant_id,
        )
        
        if not config:
            config = IDConfigurationDocument(tenant_id=tenant_id)
        
        config.student_id_format = id_format
        config.student_id_prefix = prefix
        config.student_id_include_year = include_year
        config.student_id_include_department = include_department
        config.student_id_department_mapping = department_mapping or {}
        config.student_id_reset_yearly = reset_yearly
        config.configured_by = configured_by
        config.updated_at = datetime.utcnow()
        
        await config.save()
        logger.info(f"✅ Student ID configuration updated for {tenant_id}")
        return config
    
    async def configure_staff_ids(
        self,
        tenant_id: str,
        id_format: str,
        prefix: str,
        include_department: bool = False,
        department_mapping: Optional[Dict[str, str]] = None,
        configured_by: Optional[str] = None,
    ) -> IDConfigurationDocument:
        """Configure Staff ID generation."""
        config = await IDConfigurationDocument.find_one(
            IDConfigurationDocument.tenant_id == tenant_id,
        )
        
        if not config:
            config = IDConfigurationDocument(tenant_id=tenant_id)
        
        config.staff_id_format = id_format
        config.staff_id_prefix = prefix
        config.staff_id_include_department = include_department
        config.staff_id_department_mapping = department_mapping or {}
        config.configured_by = configured_by
        config.updated_at = datetime.utcnow()
        
        await config.save()
        logger.info(f"✅ Staff ID configuration updated for {tenant_id}")
        return config
    
    async def configure_applicant_ids(
        self,
        tenant_id: str,
        id_format: str,
        prefix: str,
        include_cycle: bool = True,
        reset_yearly: bool = True,
        configured_by: Optional[str] = None,
    ) -> IDConfigurationDocument:
        """Configure Applicant ID generation."""
        config = await IDConfigurationDocument.find_one(
            IDConfigurationDocument.tenant_id == tenant_id,
        )
        
        if not config:
            config = IDConfigurationDocument(tenant_id=tenant_id)
        
        config.applicant_id_format = id_format
        config.applicant_id_prefix = prefix
        config.applicant_id_include_cycle = include_cycle
        config.applicant_id_reset_yearly = reset_yearly
        config.configured_by = configured_by
        config.updated_at = datetime.utcnow()
        
        await config.save()
        logger.info(f"✅ Applicant ID configuration updated for {tenant_id}")
        return config
