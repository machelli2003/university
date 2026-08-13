"""Compatibility package for repository imports.

This project historically imported repositories from app.infrastructure.repositories.
Some modules still point there, while the active implementations live under
app.infrastructure.database.repositories. Re-export the canonical classes here so
legacy imports continue to work without duplicating implementations.
"""

from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.infrastructure.database.repositories.university_application_repository import (
    UniversityApplicationRepository,
    IdentifierSequenceRepository,
)

__all__ = [
    "TenantRepository",
    "UniversityApplicationRepository",
    "IdentifierSequenceRepository",
]
