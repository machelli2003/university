from datetime import datetime
from typing import Optional
from app.infrastructure.database.repositories.university_application_repository import IdentifierSequenceRepository
from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.infrastructure.models.tenant import Tenant


class IdentifierService:
    def __init__(self, sequence_repo: IdentifierSequenceRepository, tenant_repo: TenantRepository):
        self.sequence_repo = sequence_repo
        self.tenant_repo = tenant_repo

    async def _build_formatted_id(self, format_string: str, tenant: Tenant, sequence: int, year: Optional[int] = None) -> str:
        year_value = year or datetime.utcnow().year
        return format_string.format(
            SCHOOL_CODE=tenant.school_code.upper() if tenant.school_code else "",
            YEAR=year_value,
            SEQUENCE=str(sequence).zfill(6),
        )

    async def generate_university_application_id(self, year: Optional[int] = None) -> str:
        current_year = year or datetime.utcnow().year
        sequence = await self.sequence_repo.next_sequence(None, "university_application", current_year)
        return f"UAPP-{current_year}-{str(sequence).zfill(6)}"

    async def generate_applicant_id(self, tenant_id: str, year: Optional[int] = None) -> str:
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ValueError("Invalid tenant")
        format_string = tenant.identifier_formats.get("applicant_id", "{SCHOOL_CODE}-APP-{YEAR}-{SEQUENCE}")
        sequence = await self.sequence_repo.next_sequence(tenant_id, "applicant", year or datetime.utcnow().year)
        return await self._build_formatted_id(format_string, tenant, sequence, year)

    async def generate_student_id(self, tenant_id: str, year: Optional[int] = None) -> str:
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ValueError("Invalid tenant")
        format_string = tenant.identifier_formats.get("student_id", "{SCHOOL_CODE}-{YEAR}-{SEQUENCE}")
        sequence = await self.sequence_repo.next_sequence(tenant_id, "student", year or datetime.utcnow().year)
        return await self._build_formatted_id(format_string, tenant, sequence, year)

    async def generate_staff_id(self, tenant_id: str, year: Optional[int] = None) -> str:
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ValueError("Invalid tenant")
        format_string = tenant.identifier_formats.get("staff_id", "{SCHOOL_CODE}-STF-{SEQUENCE}")
        sequence = await self.sequence_repo.next_sequence(tenant_id, "staff", year or datetime.utcnow().year)
        return await self._build_formatted_id(format_string, tenant, sequence, year)
