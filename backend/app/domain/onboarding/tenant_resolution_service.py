"""
Tenant Resolution Service
Resolves university tenant by school_code for applicant portal access.
Section 33: UNIVERSITY APPLICATION URL
"""

from typing import Optional
from app.infrastructure.repositories.tenant_repository import TenantRepository
from app.infrastructure.repositories.university_application_repository import UniversityApplicationRepository
from app.infrastructure.models.university_application import UniversityApplicationStatusEnum


class TenantResolutionService:
    """Service to resolve tenant by school_code for multi-tenant access."""
    
    def __init__(
        self,
        tenant_repo: TenantRepository,
        university_application_repo: UniversityApplicationRepository,
    ):
        self.tenant_repo = tenant_repo
        self.university_application_repo = university_application_repo
    
    async def resolve_tenant_by_school_code(self, school_code: str) -> dict:
        """
        Resolve tenant by school_code.
        
        Args:
            school_code: University school code (e.g., 'knust')
        
        Returns:
            dict with tenant_id, university_application_id, display_name
        
        Raises:
            ValueError: If school_code not found, inactive, or invalid
        """
        if not school_code or not isinstance(school_code, str):
            raise ValueError("school_code must be a non-empty string")
        
        # Search for active university with this school_code
        application = await self.university_application_repo.find_one({
            "school_code": school_code.lower(),
            "status": UniversityApplicationStatusEnum.ACTIVE,
        })
        
        if not application:
            raise ValueError(
                f"University with school code '{school_code}' not found or not yet active. "
                "Please contact support."
            )
        
        # Verify tenant exists and is active
        tenant = await self.tenant_repo.get_by_id(str(application.tenant_id))
        if not tenant:
            raise ValueError("University tenant configuration not found")
        
        if not getattr(tenant, "is_active", True):
            raise ValueError("University is currently inactive")
        
        return {
            "tenant_id": str(application.tenant_id),
            "university_application_id": application.university_application_id,
            "display_name": application.display_name,
            "school_code": application.school_code,
            "legal_name": application.legal_name,
        }
    
    async def validate_school_code_access(self, school_code: str, user_id: Optional[str] = None) -> bool:
        """
        Validate if a school_code is accessible (university is ACTIVE).
        
        Args:
            school_code: University school code
            user_id: Optional user ID for additional access control
        
        Returns:
            True if school_code is valid and active
        """
        try:
            await self.resolve_tenant_by_school_code(school_code)
            return True
        except ValueError:
            return False
    
    async def get_university_info_for_applicant_portal(self, school_code: str) -> dict:
        """
        Get public university information for applicant portal.
        Used to display university name, logo, and portal branding.
        
        Args:
            school_code: University school code
        
        Returns:
            dict with university public information
        """
        resolution = await self.resolve_tenant_by_school_code(school_code)
        tenant = await self.tenant_repo.get_by_id(resolution["tenant_id"])
        
        return {
            "display_name": resolution["display_name"],
            "legal_name": resolution["legal_name"],
            "school_code": resolution["school_code"],
            "logo_url": getattr(tenant, "logo_url", None),
            "primary_color": getattr(tenant, "primary_color", "#1E40AF"),
            "secondary_color": getattr(tenant, "secondary_color", "#60A5FA"),
            "website": getattr(tenant, "website", None),
            "contact_email": getattr(tenant, "contact_email", None),
            "contact_phone": getattr(tenant, "contact_phone", None),
        }
