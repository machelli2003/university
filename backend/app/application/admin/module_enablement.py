"""
Module Enablement Service
Item 65: Module Enablement - Tenants can enable/disable features

Allowed modules:
- admissions: Application & admissions workflows
- finance: Fee management & payments
- academic: Course registration & results
- exam: Exam scheduling & result management
- accommodation: Hall allocation & management
- library: Book catalog & borrowing
- hr: Staff management
- health: Health center services
- research: Research management
- alumni: Alumni portal & engagement
"""

from typing import Dict, List, Any, Optional
from app.infrastructure.models.tenant import Tenant
from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.infrastructure.database.repositories.audit_repository import AuditRepository
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Valid module names
VALID_MODULES = {
    "admissions",
    "finance",
    "academic",
    "exam",
    "accommodation",
    "library",
    "hr",
    "health",
    "research",
    "alumni",
}

# Module dependencies (if A is disabled, also disable B)
MODULE_DEPENDENCIES = {
    "finance": [],
    "admissions": ["finance"],  # Can't have admissions without finance (fees)
    "academic": ["admissions"],  # Need admitted students for academic
    "exam": ["academic"],  # Need academic for exams
    "accommodation": [],
    "library": [],
    "hr": [],
    "health": [],
    "research": [],
    "alumni": ["academic"],  # Alumni from students
}


class ModuleEnablementService:
    """Manage which modules are enabled for a tenant."""
    
    def __init__(
        self,
        tenant_repo: TenantRepository,
        audit_repo: AuditRepository,
    ):
        self.tenant_repo = tenant_repo
        self.audit_repo = audit_repo
    
    async def get_enabled_modules(
        self,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """Get list of enabled and disabled modules."""
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        features = tenant.features or {}
        
        enabled = [m for m in VALID_MODULES if features.get(m, True)]
        disabled = [m for m in VALID_MODULES if not features.get(m, True)]
        
        return {
            "tenant_id": tenant_id,
            "enabled_modules": enabled,
            "disabled_modules": disabled,
            "total_modules": len(VALID_MODULES),
            "enabled_count": len(enabled),
            "module_details": {
                module: {
                    "enabled": features.get(module, True),
                    "description": self._get_module_description(module),
                    "dependencies": MODULE_DEPENDENCIES.get(module, []),
                }
                for module in VALID_MODULES
            },
        }
    
    async def enable_module(
        self,
        tenant_id: str,
        module_name: str,
        admin_id: str,
    ) -> Dict[str, Any]:
        """
        Enable a module for a tenant.
        
        Also enables required dependencies.
        """
        if module_name not in VALID_MODULES:
            raise ValueError(f"Invalid module: {module_name}")
        
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        features = tenant.features or {}
        
        # If already enabled, return
        if features.get(module_name, True):
            return {
                "status": "already_enabled",
                "message": f"Module '{module_name}' is already enabled",
            }
        
        # Enable the module
        features[module_name] = True
        
        # Enable dependencies
        dependencies_enabled = []
        for dep in MODULE_DEPENDENCIES.get(module_name, []):
            if not features.get(dep, True):
                features[dep] = True
                dependencies_enabled.append(dep)
        
        # Update tenant
        tenant.features = features
        tenant.updated_at = datetime.utcnow()
        await self.tenant_repo.update(tenant_id, tenant)
        
        # Audit log
        await self.audit_repo.create({
            "tenant_id": tenant_id,
            "event_type": "module_enabled",
            "entity_type": "tenant",
            "entity_id": tenant_id,
            "action": "enable_module",
            "performed_by": admin_id,
            "details": {
                "module": module_name,
                "dependencies_enabled": dependencies_enabled,
            },
        })
        
        logger.info(
            f"Module '{module_name}' enabled for tenant {tenant_id} by {admin_id}"
        )
        
        return {
            "status": "success",
            "message": f"Module '{module_name}' enabled successfully",
            "module": module_name,
            "dependencies_enabled": dependencies_enabled,
        }
    
    async def disable_module(
        self,
        tenant_id: str,
        module_name: str,
        admin_id: str,
    ) -> Dict[str, Any]:
        """
        Disable a module for a tenant.
        
        Also disables dependent modules.
        """
        if module_name not in VALID_MODULES:
            raise ValueError(f"Invalid module: {module_name}")
        
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        features = tenant.features or {}
        
        # If already disabled, return
        if not features.get(module_name, True):
            return {
                "status": "already_disabled",
                "message": f"Module '{module_name}' is already disabled",
            }
        
        # Find all modules that depend on this one
        dependents = [
            m for m, deps in MODULE_DEPENDENCIES.items()
            if module_name in deps
        ]
        
        # Disable the module
        features[module_name] = False
        
        # Disable dependents
        dependents_disabled = []
        for dependent in dependents:
            if features.get(dependent, True):
                features[dependent] = False
                dependents_disabled.append(dependent)
        
        # Update tenant
        tenant.features = features
        tenant.updated_at = datetime.utcnow()
        await self.tenant_repo.update(tenant_id, tenant)
        
        # Audit log
        await self.audit_repo.create({
            "tenant_id": tenant_id,
            "event_type": "module_disabled",
            "entity_type": "tenant",
            "entity_id": tenant_id,
            "action": "disable_module",
            "performed_by": admin_id,
            "details": {
                "module": module_name,
                "dependents_disabled": dependents_disabled,
            },
        })
        
        logger.warning(
            f"Module '{module_name}' disabled for tenant {tenant_id} by {admin_id}. "
            f"Dependents disabled: {dependents_disabled}"
        )
        
        return {
            "status": "success",
            "message": f"Module '{module_name}' disabled successfully",
            "module": module_name,
            "dependents_disabled": dependents_disabled,
        }
    
    async def is_module_enabled(
        self,
        tenant_id: str,
        module_name: str,
    ) -> bool:
        """Check if a module is enabled for a tenant."""
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            return False
        
        features = tenant.features or {}
        # Default to True (enabled) if not specified
        return features.get(module_name, True)
    
    def _get_module_description(self, module: str) -> str:
        """Get description for a module."""
        descriptions = {
            "admissions": "Application & admissions workflows",
            "finance": "Fee management & payments",
            "academic": "Course registration & results",
            "exam": "Exam scheduling & results",
            "accommodation": "Hall allocation & management",
            "library": "Book catalog & borrowing",
            "hr": "Staff management",
            "health": "Health center services",
            "research": "Research management",
            "alumni": "Alumni portal & engagement",
        }
        return descriptions.get(module, "")
