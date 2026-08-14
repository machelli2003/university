"""
Audit Logging & Reporting Endpoints
Item 62: Comprehensive audit trail access for compliance

Provides endpoints to:
- Query audit logs by filters (date range, user, entity, action)
- Export audit logs
- Generate compliance reports
- Monitor sensitive operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, timedelta
from app.dependencies import get_current_user, get_audit_repo, require_roles
from app.infrastructure.models.user import User
from pydantic import BaseModel

router = APIRouter()

ADMIN_ROLES = {"super_admin", "university_admin", "registrar"}


class AuditLogResponse(BaseModel):
    id: str
    tenant_id: str
    event_type: str
    entity_type: str
    entity_id: Optional[str]
    action: str
    performed_by: Optional[str]
    details: dict
    ip_address: Optional[str]
    request_id: Optional[str]
    created_at: str


@router.get("/audit-logs")
async def list_audit_logs(
    current_user: User = Depends(get_current_user),
    audit_repo=Depends(get_audit_repo),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    performed_by: Optional[str] = Query(None, description="Filter by user"),
    days: int = Query(30, ge=1, le=365, description="Last N days"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
):
    """
    List audit logs (admin only).
    
    Filters:
    - event_type: api_request, offer_accepted, payment_confirmed, etc.
    - entity_type: applicant, student, payment, etc.
    - performed_by: user_id
    - days: last N days of logs
    """
    # Require admin role
    if current_user.role.value not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view audit logs"
        )
    
    # Build query
    query = {"tenant_id": str(current_user.tenant_id)}
    
    # Date range filter
    since = datetime.utcnow() - timedelta(days=days)
    query["created_at"] = {"$gte": since}
    
    # Optional filters
    if event_type:
        query["event_type"] = event_type
    if entity_type:
        query["entity_type"] = entity_type
    if performed_by:
        query["performed_by"] = performed_by
    
    # Execute query
    logs = await audit_repo.find(query, skip=skip, limit=limit)
    total = await audit_repo.count(query)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "logs": [
            AuditLogResponse(
                id=str(log.id),
                tenant_id=log.tenant_id,
                event_type=log.event_type,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                action=log.action,
                performed_by=log.performed_by,
                details=log.details,
                ip_address=log.ip_address,
                request_id=log.request_id,
                created_at=log.created_at.isoformat(),
            )
            for log in logs
        ],
    }


@router.get("/audit-logs/summary")
async def audit_logs_summary(
    current_user: User = Depends(get_current_user),
    audit_repo=Depends(get_audit_repo),
    days: int = Query(7, ge=1, le=365),
):
    """Get audit activity summary for the last N days."""
    if current_user.role.value not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Get stats
    query = {
        "tenant_id": str(current_user.tenant_id),
        "created_at": {"$gte": since}
    }
    
    # Count by event type
    event_stats = await audit_repo.collection.aggregate([
        {"$match": query},
        {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
    ]).to_list(None)
    
    # Count by user
    user_stats = await audit_repo.collection.aggregate([
        {"$match": query},
        {"$group": {"_id": "$performed_by", "count": {"$sum": 1}}},
    ]).to_list(None)
    
    # Total logs
    total = await audit_repo.count(query)
    
    return {
        "days": days,
        "total_events": total,
        "by_event_type": {stat["_id"]: stat["count"] for stat in event_stats},
        "by_user": {stat["_id"]: stat["count"] for stat in user_stats},
    }


@router.get("/audit-logs/sensitive-operations")
async def sensitive_operations(
    current_user: User = Depends(get_current_user),
    audit_repo=Depends(get_audit_repo),
    days: int = Query(7, ge=1, le=365),
):
    """Get log of sensitive operations (deletions, role changes, etc.)."""
    if current_user.role.value not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Sensitive event types
    sensitive_events = [
        "user_deleted",
        "role_changed",
        "permission_modified",
        "payment_refunded",
        "student_expelled",
        "record_modified",
    ]
    
    query = {
        "tenant_id": str(current_user.tenant_id),
        "event_type": {"$in": sensitive_events},
        "created_at": {"$gte": since},
    }
    
    logs = await audit_repo.find(query, limit=100)
    
    return {
        "sensitive_operations": [
            {
                "id": str(log.id),
                "event_type": log.event_type,
                "entity_type": log.entity_type,
                "action": log.action,
                "performed_by": log.performed_by,
                "timestamp": log.created_at.isoformat(),
                "details": log.details,
            }
            for log in logs
        ],
    }


@router.get("/audit-logs/entity/{entity_type}/{entity_id}")
async def entity_audit_trail(
    entity_type: str,
    entity_id: str,
    current_user: User = Depends(get_current_user),
    audit_repo=Depends(get_audit_repo),
):
    """Get complete audit trail for a specific entity."""
    query = {
        "tenant_id": str(current_user.tenant_id),
        "entity_type": entity_type,
        "entity_id": entity_id,
    }
    
    logs = await audit_repo.find(query, limit=1000)
    
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "history": [
            {
                "timestamp": log.created_at.isoformat(),
                "action": log.action,
                "performed_by": log.performed_by,
                "changes": log.details,
            }
            for log in logs
        ],
    }
