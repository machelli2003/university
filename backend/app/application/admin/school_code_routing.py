"""
School Code Routing
Item 33: Public application portal routing

Process:
1. Applicant visits https://eump.local/apply/{school_code}
2. System resolves school_code to university tenant
3. Returns university-specific application form
4. Applicant fills and submits form
5. System records application under that tenant

Supports:
- Short codes (e.g., "KNUST", "UCC")
- Custom application URLs per university (e.g., university.edu/apply)
- Multi-domain routing via DNS/reverse proxy

This enables public-facing application portal without revealing backend URLs.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from beanie import Document, Indexed
import logging

logger = logging.getLogger(__name__)


class SchoolCode(BaseModel):
    """School code mapping."""
    school_code: str
    tenant_id: str
    university_name: str
    is_active: bool


class UniversityApplicationPortal(BaseModel):
    """University's public application portal details."""
    tenant_id: str
    school_code: str
    university_name: str
    application_url: str  # /apply/{school_code}
    custom_domain: Optional[str] = None  # e.g., apply.university.edu
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    application_fee: Optional[float] = None
    application_deadline: Optional[datetime] = None
    is_accepting_applications: bool
    intake_period: str  # e.g., "2024/2025 Academic Year"
    programmes_available: int
    total_applications: int


class SchoolCodeRegistry(Document):
    """
    Registry of school codes to tenant mapping.
    
    Enables applicants to access correct university via /apply/{code}
    """
    
    school_code: Indexed(str, unique=True)
    tenant_id: Indexed(str)
    
    # University info (denormalized for quick lookup)
    university_name: str
    
    # Portal configuration
    custom_domain: Optional[str] = None  # For custom domain routing
    logo_url: Optional[str] = None
    banner_color: Optional[str] = None  # Branding
    
    # Status
    is_active: bool = True
    accepting_applications: bool = True
    
    # Dates
    created_at: datetime
    updated_at: datetime
    
    class Settings:
        collection = "school_code_registry"
        indexes = [
            [("school_code", 1)],
            [("tenant_id", 1)],
            [("is_active", 1)],
            [("custom_domain", 1)],  # For domain-based routing
        ]


# ==================== SCHEMAS ====================

class ResolveSchoolCodeRequest(BaseModel):
    """Request to resolve school code to tenant."""
    school_code: str
    domain: Optional[str] = None  # For domain-based routing


class ResolveSchoolCodeResponse(BaseModel):
    """Response with tenant info."""
    tenant_id: str
    school_code: str
    university_name: str
    application_url: str
    accepting_applications: bool
    intake_period: Optional[str] = None
    can_apply: bool
    message: Optional[str] = None


class SchoolCodeResponse(BaseModel):
    """School code details."""
    school_code: str
    tenant_id: str
    university_name: str
    is_active: bool
    accepting_applications: bool
    custom_domain: Optional[str] = None


# ==================== SERVICE ====================

class SchoolCodeResolutionService:
    """
    Resolve school codes to university tenants.
    
    Enables public-facing application portal routing.
    """
    
    async def resolve_school_code(
        self,
        school_code: str,
    ) -> ResolveSchoolCodeResponse:
        """
        Resolve school code to tenant.
        
        Called when applicant visits /apply/{school_code}
        
        Args:
            school_code: Code provided by applicant (case-insensitive)
        
        Returns:
            ResolveSchoolCodeResponse with tenant info
        
        Raises:
            ValueError: If school code not found or inactive
        """
        
        # Normalize code
        code = school_code.upper().strip()
        
        # Look up in registry
        registry = await SchoolCodeRegistry.find_one(
            SchoolCodeRegistry.school_code == code,
            SchoolCodeRegistry.is_active == True,
        )
        
        if not registry:
            # Check if code exists but is inactive
            inactive = await SchoolCodeRegistry.find_one(
                SchoolCodeRegistry.school_code == code
            )
            
            if inactive:
                raise ValueError(
                    f"Applications for {inactive.university_name} are currently closed"
                )
            else:
                raise ValueError(f"University code '{school_code}' not found")
        
        # Check if accepting applications
        if not registry.accepting_applications:
            from app.application.admin.setup_submission import UniversityApplicationDocument
            
            app = await UniversityApplicationDocument.find_one(
                UniversityApplicationDocument.tenant_id == registry.tenant_id
            )
            
            return ResolveSchoolCodeResponse(
                tenant_id=registry.tenant_id,
                school_code=registry.school_code,
                university_name=registry.university_name,
                application_url=f"/apply/{registry.school_code}",
                accepting_applications=False,
                can_apply=False,
                message="Applications are currently closed for this university",
            )
        
        return ResolveSchoolCodeResponse(
            tenant_id=registry.tenant_id,
            school_code=registry.school_code,
            university_name=registry.university_name,
            application_url=f"/apply/{registry.school_code}",
            accepting_applications=True,
            can_apply=True,
        )
    
    async def resolve_by_domain(
        self,
        domain: str,
    ) -> ResolveSchoolCodeResponse:
        """
        Resolve custom domain to tenant.
        
        For universities with custom domains (e.g., apply.university.edu)
        
        Args:
            domain: Custom domain (case-insensitive)
        
        Returns:
            ResolveSchoolCodeResponse
        
        Raises:
            ValueError: If domain not found
        """
        
        domain_lower = domain.lower().strip()
        
        registry = await SchoolCodeRegistry.find_one(
            SchoolCodeRegistry.custom_domain == domain_lower,
            SchoolCodeRegistry.is_active == True,
        )
        
        if not registry:
            raise ValueError(f"Domain '{domain}' not associated with any university")
        
        return ResolveSchoolCodeResponse(
            tenant_id=registry.tenant_id,
            school_code=registry.school_code,
            university_name=registry.university_name,
            application_url=f"https://{domain}/apply",
            accepting_applications=registry.accepting_applications,
            can_apply=registry.accepting_applications,
        )
    
    async def register_school_code(
        self,
        tenant_id: str,
        school_code: str,
        university_name: str,
        custom_domain: Optional[str] = None,
        logo_url: Optional[str] = None,
        banner_color: Optional[str] = None,
    ) -> SchoolCodeResponse:
        """
        Register school code for university.
        
        Called during university activation (Item 32).
        
        Args:
            tenant_id: University
            school_code: Code (e.g., "KNUST", "UCC")
            university_name: University name
            custom_domain: Optional custom domain
            logo_url: Optional logo URL
            banner_color: Optional branding color
        
        Returns:
            SchoolCodeResponse
        """
        
        code_upper = school_code.upper().strip()
        
        # Check if code already exists
        existing = await SchoolCodeRegistry.find_one(
            SchoolCodeRegistry.school_code == code_upper
        )
        if existing:
            raise ValueError(f"School code '{code_upper}' already registered")
        
        # Create registry entry
        registry = SchoolCodeRegistry(
            school_code=code_upper,
            tenant_id=tenant_id,
            university_name=university_name,
            custom_domain=custom_domain.lower() if custom_domain else None,
            logo_url=logo_url,
            banner_color=banner_color,
            is_active=True,
            accepting_applications=False,  # Admin enables later
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        await registry.insert()
        
        logger.info(
            f"✅ Registered school code '{code_upper}' for {university_name} ({tenant_id})"
        )
        
        return SchoolCodeResponse(
            school_code=registry.school_code,
            tenant_id=registry.tenant_id,
            university_name=registry.university_name,
            is_active=registry.is_active,
            accepting_applications=registry.accepting_applications,
            custom_domain=registry.custom_domain,
        )
    
    async def enable_applications(
        self,
        school_code: str,
    ) -> SchoolCodeResponse:
        """
        Enable application acceptance for school code.
        
        Called by university admin to open applications.
        """
        
        registry = await SchoolCodeRegistry.find_one(
            SchoolCodeRegistry.school_code == school_code.upper()
        )
        if not registry:
            raise ValueError(f"School code not found: {school_code}")
        
        registry.accepting_applications = True
        registry.updated_at = datetime.utcnow()
        await registry.save()
        
        logger.info(f"✅ Applications enabled for {school_code}")
        
        return SchoolCodeResponse(
            school_code=registry.school_code,
            tenant_id=registry.tenant_id,
            university_name=registry.university_name,
            is_active=registry.is_active,
            accepting_applications=registry.accepting_applications,
            custom_domain=registry.custom_domain,
        )
    
    async def disable_applications(
        self,
        school_code: str,
        reason: Optional[str] = None,
    ) -> SchoolCodeResponse:
        """
        Disable application acceptance for school code.
        
        Called by university admin to close applications.
        """
        
        registry = await SchoolCodeRegistry.find_one(
            SchoolCodeRegistry.school_code == school_code.upper()
        )
        if not registry:
            raise ValueError(f"School code not found: {school_code}")
        
        registry.accepting_applications = False
        registry.updated_at = datetime.utcnow()
        await registry.save()
        
        logger.info(f"❌ Applications disabled for {school_code}: {reason or 'no reason'}")
        
        return SchoolCodeResponse(
            school_code=registry.school_code,
            tenant_id=registry.tenant_id,
            university_name=registry.university_name,
            is_active=registry.is_active,
            accepting_applications=registry.accepting_applications,
            custom_domain=registry.custom_domain,
        )
    
    async def get_school_code(
        self,
        school_code: str,
    ) -> SchoolCodeResponse:
        """Get school code details."""
        
        registry = await SchoolCodeRegistry.find_one(
            SchoolCodeRegistry.school_code == school_code.upper()
        )
        if not registry:
            raise ValueError(f"School code not found: {school_code}")
        
        return SchoolCodeResponse(
            school_code=registry.school_code,
            tenant_id=registry.tenant_id,
            university_name=registry.university_name,
            is_active=registry.is_active,
            accepting_applications=registry.accepting_applications,
            custom_domain=registry.custom_domain,
        )
    
    async def list_all_codes(
        self,
        active_only: bool = False,
    ) -> list[SchoolCodeResponse]:
        """List all registered school codes."""
        
        query = SchoolCodeRegistry.find()
        if active_only:
            query = query.find(SchoolCodeRegistry.is_active == True)
        
        registries = await query.sort([("school_code", 1)]).to_list()
        
        return [
            SchoolCodeResponse(
                school_code=r.school_code,
                tenant_id=r.tenant_id,
                university_name=r.university_name,
                is_active=r.is_active,
                accepting_applications=r.accepting_applications,
                custom_domain=r.custom_domain,
            )
            for r in registries
        ]
