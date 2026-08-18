"""
Audit Middleware
Item 62: Audit Logging - Comprehensive request/action logging for compliance

This middleware logs all API requests/responses for audit trail purposes.
Captures:
- Tenant context
- User performing action
- Resource accessed/modified
- Request/response details
- IP address & request ID
- Timestamps
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from datetime import datetime
import json
import logging
import uuid
from typing import Optional
from app.infrastructure.database.repositories.audit_repository import AuditRepository

logger = logging.getLogger(__name__)

# Methods that should be fully audited
AUDIT_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

# Paths to exclude from detailed audit logging (health checks, etc.)
EXCLUDED_PATHS = {
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}

# Sensitive fields to redact from audit logs
SENSITIVE_FIELDS = {
    "password",
    "pin",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "credit_card",
    "ssn",
}


def redact_sensitive_data(data: dict) -> dict:
    """Redact sensitive fields from dictionary recursively."""
    if not isinstance(data, dict):
        return data
    
    redacted = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS):
            redacted[key] = "***REDACTED***"
        elif isinstance(value, dict):
            redacted[key] = redact_sensitive_data(value)
        elif isinstance(value, list):
            redacted[key] = [
                redact_sensitive_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            redacted[key] = value
    
    return redacted


class AuditMiddleware(BaseHTTPMiddleware):
    """Log all API operations for audit trail."""
    
    def __init__(self, app, audit_repo: Optional[AuditRepository] = None):
        super().__init__(app)
        self.audit_repo = audit_repo
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Skip excluded paths
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)
        
        # Extract request context
        tenant_id = request.headers.get("X-Tenant-ID", "unknown")
        user_id = getattr(request.state, "user_id", None)  # Set by auth middleware
        ip_address = request.client.host if request.client else "unknown"
        
        request_data = None
        if request.method in AUDIT_METHODS:
            try:
                body = await request.body()
                if body:
                    request_data = json.loads(body)
                    # Redact sensitive data
                    request_data = redact_sensitive_data(request_data)
            except:
                request_data = None
        
        # Call next middleware/route
        start_time = datetime.utcnow()
        response = await call_next(request)
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Prepare audit log
        if request.method in AUDIT_METHODS or response.status_code >= 400:
            audit_entry = {
                "tenant_id": tenant_id,
                "request_id": request_id,
                "timestamp": start_time.isoformat(),
                "http_method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "user_id": user_id,
                "ip_address": ip_address,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "request_body": request_data,
                "user_agent": request.headers.get("User-Agent", "unknown"),
            }
            
            # Log to file
            log_level = "INFO" if 200 <= response.status_code < 300 else "WARNING"
            getattr(logger, log_level.lower())(
                f"API Request: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"User: {user_id} "
                f"Duration: {duration_ms:.2f}ms"
            )
            
            # Log to database if repository available or instantiate lazily
            try:
                repo = self.audit_repo or AuditRepository()
                path_parts = request.url.path.strip("/").split("/")
                entity_type = path_parts[0] if path_parts else "unknown"
                
                await repo.create({
                    "tenant_id": tenant_id,
                    "event_type": "api_request",
                    "entity_type": entity_type,
                    "action": f"{request.method} {request.url.path}",
                    "performed_by": user_id,
                    "details": audit_entry,
                    "request_id": request_id,
                })
            except Exception as e:
                logger.error(f"Failed to create audit log: {str(e)}")
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
