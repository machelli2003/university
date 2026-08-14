"""
Super Admin Impersonation Use Case
Item 63: Impersonation - Short-lived, auditable user impersonation

Requirements:
- Only super admins can impersonate
- Impersonation tokens are short-lived (15-60 minutes)
- All actions under impersonation are audited
- Original admin is logged as the actual actor
- Impersonation events trigger notifications
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.infrastructure.models.user import User
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.audit_repository import AuditRepository
from app.infrastructure.database.repositories.blacklist_repository import BlacklistedToken
from app.domain.security.token_service import TokenService
import logging

logger = logging.getLogger(__name__)


class ImpersonationUseCase:
    """Handle super admin impersonation of users."""
    
    def __init__(
        self,
        user_repo: UserRepository,
        audit_repo: AuditRepository,
        token_service: TokenService,
        impersonation_ttl_minutes: int = 30,  # Impersonation tokens valid for 30 minutes
    ):
        self.user_repo = user_repo
        self.audit_repo = audit_repo
        self.token_service = token_service
        self.impersonation_ttl = timedelta(minutes=impersonation_ttl_minutes)
    
    async def start_impersonation(
        self,
        target_user_id: str,
        impersonating_admin_id: str,
        tenant_id: str,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Create an impersonation token for a super admin to act as another user.
        
        Args:
            target_user_id: User to impersonate
            impersonating_admin_id: Super admin performing impersonation
            tenant_id: Tenant context
            reason: Reason for impersonation (support ticket, investigation, etc.)
        
        Returns:
            {
                "impersonation_token": "...",
                "expires_at": "2024-01-15T12:30:00Z",
                "impersonation_id": "...",
                "warning": "You are now impersonating user...",
            }
        """
        # Get target user
        target_user = await self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise ValueError(f"User {target_user_id} not found")
        
        # Verify both users are in same tenant
        if str(target_user.tenant_id) != tenant_id:
            raise ValueError("Cross-tenant impersonation not allowed")
        
        # Get impersonating admin
        admin_user = await self.user_repo.get_by_id(impersonating_admin_id)
        if not admin_user:
            raise ValueError(f"Admin {impersonating_admin_id} not found")
        
        if str(admin_user.tenant_id) != tenant_id:
            raise ValueError("Admin not in same tenant")
        
        # Verify admin is super admin
        if admin_user.role.value != "super_admin":
            raise ValueError("Only super admins can impersonate users")
        
        # Create impersonation token
        expiration = datetime.utcnow() + self.impersonation_ttl
        impersonation_token = self.token_service.create_token(
            user_id=target_user_id,
            tenant_id=tenant_id,
            expires_at=expiration,
            extra_claims={
                "impersonated_by": impersonating_admin_id,
                "impersonation_reason": reason,
                "is_impersonation": True,
            },
        )
        
        # Generate unique impersonation ID for audit trail
        impersonation_id = f"IMP-{datetime.utcnow().timestamp()}-{target_user_id}"
        
        # Audit log
        await self.audit_repo.create({
            "tenant_id": tenant_id,
            "event_type": "impersonation_started",
            "entity_type": "user",
            "entity_id": target_user_id,
            "action": f"impersonate_user",
            "performed_by": impersonating_admin_id,
            "details": {
                "impersonation_id": impersonation_id,
                "target_user": {
                    "id": target_user_id,
                    "name": f"{target_user.first_name} {target_user.last_name}",
                    "email": target_user.email,
                    "role": target_user.role.value,
                },
                "admin": {
                    "id": impersonating_admin_id,
                    "name": f"{admin_user.first_name} {admin_user.last_name}",
                    "email": admin_user.email,
                },
                "reason": reason,
                "token_expires_at": expiration.isoformat(),
            },
        })
        
        logger.warning(
            f"Impersonation started: {impersonating_admin_id} → {target_user_id} "
            f"(Reason: {reason})"
        )
        
        return {
            "status": "success",
            "impersonation_token": impersonation_token,
            "expires_at": expiration.isoformat(),
            "impersonation_id": impersonation_id,
            "target_user": {
                "id": target_user_id,
                "name": f"{target_user.first_name} {target_user.last_name}",
                "email": target_user.email,
            },
            "warning": (
                "⚠️ IMPERSONATION ACTIVE: You are now acting as another user. "
                "All actions are being audited. Impersonation will expire "
                f"at {expiration.isoformat()}."
            ),
        }
    
    async def end_impersonation(
        self,
        impersonation_id: str,
        impersonating_admin_id: str,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """End an active impersonation session."""
        # Find the original impersonation audit log
        audit_logs = await self.audit_repo.find({
            "tenant_id": tenant_id,
            "event_type": "impersonation_started",
            "details.impersonation_id": impersonation_id,
        })
        
        if not audit_logs:
            raise ValueError(f"Impersonation {impersonation_id} not found")
        
        original_impersonation = audit_logs[0]
        target_user_id = original_impersonation.entity_id
        
        # Audit log
        await self.audit_repo.create({
            "tenant_id": tenant_id,
            "event_type": "impersonation_ended",
            "entity_type": "user",
            "entity_id": target_user_id,
            "action": "end_impersonation",
            "performed_by": impersonating_admin_id,
            "details": {
                "impersonation_id": impersonation_id,
                "duration_seconds": (
                    datetime.utcnow() - original_impersonation.created_at
                ).total_seconds(),
            },
        })
        
        logger.info(f"Impersonation ended: {impersonation_id}")
        
        return {
            "status": "success",
            "message": "Impersonation session ended",
            "impersonation_id": impersonation_id,
        }
    
    async def get_active_impersonations(
        self,
        tenant_id: str,
        admin_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List active impersonation sessions.
        
        Args:
            tenant_id: Tenant to query
            admin_id: Optional filter by admin performing impersonation
        """
        # Find active impersonation tokens
        # (This would require a separate tracking collection in production)
        query = {
            "tenant_id": tenant_id,
            "event_type": "impersonation_started",
            "details.token_expires_at": {"$gte": datetime.utcnow().isoformat()},
        }
        
        if admin_id:
            query["performed_by"] = admin_id
        
        active_impersonations = await self.audit_repo.find(query)
        
        return {
            "active_impersonations": [
                {
                    "impersonation_id": log.details.get("impersonation_id"),
                    "target_user": log.details.get("target_user"),
                    "admin": log.details.get("admin"),
                    "started_at": log.created_at.isoformat(),
                    "expires_at": log.details.get("token_expires_at"),
                    "reason": log.details.get("reason"),
                }
                for log in active_impersonations
            ],
        }
