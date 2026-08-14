"""
Graduation Configuration Service
Item 28: Configure graduation requirements and settings

Universities configure:
- Minimum credits for graduation
- Minimum CGPA
- Clearance requirements (fees, library, etc.)
- Certificate generation
- Transcript settings
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import Document, Indexed
import logging

logger = logging.getLogger(__name__)


class GraduationRequirement(BaseModel):
    """Individual graduation requirement."""
    requirement_type: str  # e.g., "academic_fees", "library_clearance", "health_clearance"
    name: str
    description: str
    is_mandatory: bool = True
    verification_process: str  # How to verify: "automatic", "manual", "system_check"


class ClearanceRequirement(BaseModel):
    """Module that must clear a student before graduation."""
    module_name: str  # "finance", "library", "health", "accommodation"
    status_check_query: str  # Query to verify clearance
    description: str
    is_mandatory: bool = True


class GraduationConfiguration(Document):
    """
    Graduation configuration for university.
    
    Defines requirements for students to graduate:
    - Academic requirements (credits, GPA)
    - Administrative clearances (fees, documents)
    - Certificate & transcript settings
    """
    
    tenant_id: Indexed(str)
    
    # Academic Requirements
    minimum_credits_required: int = 120  # Total credits needed to graduate
    minimum_cgpa: float = 2.0  # Cumulative GPA threshold
    minimum_level_gpa: Optional[float] = None  # Minimum GPA for final level
    
    # Credit breakdown (optional)
    credits_per_level: Optional[Dict[int, int]] = None  # {100: 30, 200: 30, 300: 30, 400: 30}
    minimum_credits_per_level: Optional[Dict[int, int]] = None
    
    # Clearance Requirements
    clearance_modules: List[ClearanceRequirement] = []  # Modules that must clear student
    
    # Financial
    outstanding_fees_allowed: float = 0.0  # Max outstanding balance to graduate (0 = none)
    payment_plan_allowed: bool = False  # Can graduate with payment plan
    
    # Documentation
    required_documents: List[str] = []  # ["transcript_application", "degree_verification"]
    document_deadline_days: int = 14  # Days to provide documents after graduation date
    
    # Certificate & Transcript
    generate_certificate: bool = True
    certificate_template: Optional[str] = None  # Path to template
    generate_transcript: bool = True
    transcript_include_failed_courses: bool = True
    transcript_include_withdrawals: bool = True
    
    # Commencement
    commencement_ceremony: bool = True
    commencement_required_to_graduate: bool = False
    
    # Academic Standing
    academic_standing_required: str = "good"  # good, probation, etc.
    allow_graduation_on_probation: bool = False
    
    # Resit/Carryover
    allow_carryover_courses: bool = False  # Can graduate with carryover courses
    max_carryover_credits: Optional[int] = None
    
    # Graduation Eligibility
    can_graduate_same_year_as_admission: bool = False  # 4-year programme can't graduate in year 1
    minimum_years_required: int = 0
    
    # Status
    is_configured: bool = False
    configured_by: Optional[str] = None
    configured_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Settings:
        collection = "graduation_configurations"
        indexes = [
            [("tenant_id", 1)],
        ]


class GraduationRequirementStatus(BaseModel):
    """Status of a student's graduation requirements."""
    requirement_type: str
    name: str
    is_met: bool
    verification_date: Optional[datetime] = None
    verified_by: Optional[str] = None
    notes: Optional[str] = None


class StudentGraduationEligibility(BaseModel):
    """Whether a student can graduate."""
    student_id: str
    programme_id: str
    can_graduate: bool
    eligibility_score: float  # 0-100
    requirements_status: List[GraduationRequirementStatus] = []
    blocking_issues: List[str] = []  # What's preventing graduation
    warnings: List[str] = []  # Things to note
    clearance_status: Dict[str, bool] = {}  # Module clearance status
    eligible_date: Optional[datetime] = None  # When they become eligible
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== SCHEMAS ====================

class CreateGraduationConfigRequest(BaseModel):
    """Request to create/update graduation configuration."""
    minimum_credits_required: int
    minimum_cgpa: float
    minimum_level_gpa: Optional[float] = None
    outstanding_fees_allowed: float = 0.0
    payment_plan_allowed: bool = False
    clearance_modules: List[Dict[str, Any]] = []
    academic_standing_required: str = "good"
    allow_graduation_on_probation: bool = False
    commencement_required: bool = False


class GraduationConfigResponse(BaseModel):
    """Response model for graduation config."""
    tenant_id: str
    minimum_credits_required: int
    minimum_cgpa: float
    minimum_level_gpa: Optional[float]
    clearance_modules: List[Dict[str, str]]
    academic_standing_required: str
    is_configured: bool
    configured_at: Optional[datetime]


# ==================== SERVICE ====================

class GraduationConfigurationService:
    """Configure and manage graduation requirements."""
    
    async def configure_graduation(
        self,
        tenant_id: str,
        minimum_credits: int,
        minimum_cgpa: float,
        minimum_level_gpa: Optional[float] = None,
        outstanding_fees: float = 0.0,
        payment_plan_allowed: bool = False,
        clearance_modules: Optional[List[Dict[str, Any]]] = None,
        academic_standing: str = "good",
        allow_probation: bool = False,
        commencement_required: bool = False,
        configured_by: Optional[str] = None,
    ) -> GraduationConfiguration:
        """
        Configure graduation requirements for university.
        
        Args:
            tenant_id: University
            minimum_credits: Total credits needed
            minimum_cgpa: Minimum cumulative GPA
            minimum_level_gpa: GPA for final level (optional)
            outstanding_fees: Max outstanding balance allowed
            payment_plan_allowed: Can graduate with payment plan
            clearance_modules: List of modules that must clear
            academic_standing: Required standing
            allow_probation: Can graduate while on academic probation
            commencement_required: Must attend commencement
            configured_by: Admin configuring
        
        Returns:
            GraduationConfiguration
        """
        config = await GraduationConfiguration.find_one(
            GraduationConfiguration.tenant_id == tenant_id,
        )
        
        if not config:
            config = GraduationConfiguration(
                tenant_id=tenant_id,
            )
        
        config.minimum_credits_required = minimum_credits
        config.minimum_cgpa = minimum_cgpa
        config.minimum_level_gpa = minimum_level_gpa
        config.outstanding_fees_allowed = outstanding_fees
        config.payment_plan_allowed = payment_plan_allowed
        config.academic_standing_required = academic_standing
        config.allow_graduation_on_probation = allow_probation
        config.commencement_ceremony = commencement_required
        config.commencement_required_to_graduate = commencement_required
        
        if clearance_modules:
            config.clearance_modules = [
                ClearanceRequirement(**mod) for mod in clearance_modules
            ]
        
        config.is_configured = True
        config.configured_by = configured_by
        config.configured_at = datetime.utcnow()
        config.updated_at = datetime.utcnow()
        
        await config.save()
        logger.info(f"✅ Graduation configuration set for {tenant_id}")
        return config
    
    async def get_configuration(
        self,
        tenant_id: str,
    ) -> Optional[GraduationConfiguration]:
        """Retrieve graduation configuration."""
        return await GraduationConfiguration.find_one(
            GraduationConfiguration.tenant_id == tenant_id,
        )
    
    async def check_graduation_eligibility(
        self,
        student_id: str,
        programme_id: str,
        tenant_id: str,
        student_data: Dict[str, Any],  # From student record
    ) -> StudentGraduationEligibility:
        """
        Check if student meets graduation requirements.
        
        Args:
            student_id: Student ID
            programme_id: Programme enrolled in
            tenant_id: University
            student_data: Student's academic and financial data
        
        Returns:
            StudentGraduationEligibility with status and blocking issues
        """
        config = await self.get_configuration(tenant_id)
        if not config:
            # No graduation config = cannot graduate
            return StudentGraduationEligibility(
                student_id=student_id,
                programme_id=programme_id,
                can_graduate=False,
                eligibility_score=0.0,
                blocking_issues=["Graduation configuration not set"],
            )
        
        requirements_status = []
        blocking_issues = []
        warnings = []
        score = 100.0
        
        # Check academic credits
        credits_earned = student_data.get("total_credits_earned", 0)
        if credits_earned < config.minimum_credits_required:
            blocking_issues.append(
                f"Insufficient credits: {credits_earned}/{config.minimum_credits_required}"
            )
            score -= 30
        else:
            requirements_status.append(GraduationRequirementStatus(
                requirement_type="academic_credits",
                name="Minimum Credits",
                is_met=True,
                verified_at=datetime.utcnow(),
            ))
        
        # Check CGPA
        cgpa = student_data.get("cgpa", 0.0)
        if cgpa < config.minimum_cgpa:
            blocking_issues.append(
                f"CGPA below minimum: {cgpa:.2f} (requires {config.minimum_cgpa})"
            )
            score -= 30
        else:
            requirements_status.append(GraduationRequirementStatus(
                requirement_type="cgpa",
                name="Minimum CGPA",
                is_met=True,
                verified_at=datetime.utcnow(),
            ))
        
        # Check final level GPA
        if config.minimum_level_gpa:
            level_gpa = student_data.get("current_level_gpa", 0.0)
            if level_gpa < config.minimum_level_gpa:
                warnings.append(
                    f"Level GPA {level_gpa:.2f} below preferred {config.minimum_level_gpa}"
                )
        
        # Check academic standing
        academic_standing = student_data.get("academic_standing", "good")
        if academic_standing == "probation" and not config.allow_graduation_on_probation:
            blocking_issues.append("Student on academic probation (not allowed)")
            score -= 20
        
        # Check outstanding fees
        outstanding_fees = student_data.get("outstanding_balance", 0.0)
        if outstanding_fees > config.outstanding_fees_allowed:
            if not config.payment_plan_allowed:
                blocking_issues.append(
                    f"Outstanding fees: GHS {outstanding_fees:.2f}"
                )
                score -= 25
            else:
                warnings.append(f"Outstanding fees: GHS {outstanding_fees:.2f} (payment plan active)")
        
        # Check module clearances (simplified)
        clearance_status = {}
        for module in config.clearance_modules:
            # TODO: Query actual clearance status
            cleared = student_data.get(f"{module.module_name}_cleared", False)
            clearance_status[module.module_name] = cleared
            
            if module.is_mandatory and not cleared:
                blocking_issues.append(f"Not cleared by {module.module_name}")
                score -= 15
        
        can_graduate = len(blocking_issues) == 0 and score >= 50
        
        return StudentGraduationEligibility(
            student_id=student_id,
            programme_id=programme_id,
            can_graduate=can_graduate,
            eligibility_score=max(0, score),
            requirements_status=requirements_status,
            blocking_issues=blocking_issues,
            warnings=warnings,
            clearance_status=clearance_status,
        )
