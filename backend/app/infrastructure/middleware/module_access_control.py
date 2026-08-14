"""
Module Access Control Decorator
Check if a module is enabled before allowing access to its endpoints.
"""

from functools import wraps
from fastapi import HTTPException, status, Depends
from app.infrastructure.database.repositories.tenant_repository import TenantRepository
from app.dependencies import get_tenant_repo
from typing import Optional

async def require_module(module_name: str):
    """
    Dependency that checks if a module is enabled for the current tenant.
    
    Usage:
        @router.get("/academic/courses")
        async def list_courses(
            module_check = Depends(require_module("academic")),
        ):
            ...
    """
    async def check_module(
        current_user = Depends(lambda: None),  # Will be injected by FastAPI
        tenant_repo: TenantRepository = Depends(get_tenant_repo),
    ):
        from app.dependencies import get_current_user
        from app.infrastructure.models.user import User
        
        user = await get_current_user()
        
        tenant = await tenant_repo.get_by_id(str(user.tenant_id))
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant not found"
            )
        
        features = tenant.features or {}
        
        # Check if module is enabled
        if not features.get(module_name, True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Module '{module_name}' is not enabled for your organization",
            )
    
    return check_module
