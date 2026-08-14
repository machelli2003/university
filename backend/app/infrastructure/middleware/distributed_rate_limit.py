"""
Distributed Rate Limiting Middleware
Item 75: Redis-backed rate limiting for production deployments

Replaces in-memory rate limiting with Redis for:
- Horizontal scaling (shared across servers)
- Automatic cleanup (TTL-based expiration)
- Per-user, per-IP, per-endpoint limits
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import get_settings
import redis
import logging

logger = logging.getLogger(__name__)

# Rate limit configurations
RATE_LIMIT_CONFIG = {
    # Auth endpoints - prevent brute force
    "/api/v1/auth/login": {"max_requests": 5, "window_seconds": 300},  # 5 attempts per 5 min
    "/api/v1/auth/register": {"max_requests": 3, "window_seconds": 3600},  # 3 per hour
    
    # Payment endpoints
    "/api/v1/apply/": {"max_requests": 20, "window_seconds": 3600},  # 20 per hour
    "/api/v1/finance/payments/initiate": {"max_requests": 10, "window_seconds": 3600},
    
    # API endpoints - general
    "default": {"max_requests": 100, "window_seconds": 3600},  # 100 per hour
}


class DistributedRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-backed rate limiting middleware.
    
    Supports:
    - Per-user rate limiting (prevent abuse)
    - Per-IP rate limiting (prevent DDoS)
    - Per-endpoint rate limiting
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(self.settings.REDIS_URL)
            self.redis_client.ping()
            logger.info("✅ Distributed rate limiting initialized")
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable for rate limiting: {str(e)}")
            self.redis_client = None
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request."""
        
        # Skip health checks
        if request.url.path in ["/health", "/api/v1/health"]:
            return await call_next(request)
        
        # Skip if Redis unavailable
        if not self.redis_client:
            return await call_next(request)
        
        # Determine rate limit for this endpoint
        limit_config = self._get_rate_limit_config(request.url.path)
        max_requests = limit_config["max_requests"]
        window_seconds = limit_config["window_seconds"]
        
        # Get identifier (user_id or IP)
        identifier = self._get_identifier(request)
        
        # Check rate limit
        allowed, remaining = self._check_rate_limit(
            identifier,
            request.url.path,
            max_requests,
            window_seconds,
        )
        
        if not allowed:
            logger.warning(f"⚠️ Rate limit exceeded for {identifier} on {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {window_seconds} seconds.",
                headers={"Retry-After": str(window_seconds)},
            )
        
        # Add rate limit info to response headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.
        
        Priority:
        1. User ID (if authenticated)
        2. IP address (fallback)
        """
        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fallback to IP address
        if request.client:
            return f"ip:{request.client.host}"
        
        return "unknown"
    
    def _get_rate_limit_config(self, path: str) -> dict:
        """Get rate limit config for endpoint."""
        # Check for exact match
        if path in RATE_LIMIT_CONFIG:
            return RATE_LIMIT_CONFIG[path]
        
        # Check for prefix match (e.g., /api/v1/apply/*)
        for config_path, config in RATE_LIMIT_CONFIG.items():
            if config_path.endswith("/") and path.startswith(config_path):
                return config
        
        # Default config
        return RATE_LIMIT_CONFIG.get("default", {
            "max_requests": 100,
            "window_seconds": 3600,
        })
    
    def _check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple:
        """
        Check if request is within rate limit.
        
        Returns: (allowed: bool, remaining: int)
        """
        try:
            rate_key = f"ratelimit:{identifier}:{endpoint}"
            
            # Get current count
            current_count = self.redis_client.get(rate_key)
            
            if current_count is None:
                # First request in window
                self.redis_client.setex(rate_key, window_seconds, 1)
                return True, max_requests - 1
            
            current_count = int(current_count)
            
            if current_count >= max_requests:
                # Rate limit exceeded
                return False, 0
            
            # Increment and get remaining
            new_count = self.redis_client.incr(rate_key)
            remaining = max(0, max_requests - new_count)
            
            return True, remaining
        
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            # Allow on error to avoid breaking service
            return True, max_requests


class SessionCleanupMiddleware(BaseHTTPMiddleware):
    """
    Session cleanup middleware.
    
    Automatically cleans up expired sessions from Redis.
    Runs on startup and periodically.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.cleanup_interval = 3600  # Run every hour
        self.last_cleanup = 0
    
    async def dispatch(self, request: Request, call_next):
        """Check if cleanup is due."""
        import time
        
        current_time = time.time()
        
        # If cleanup interval passed, trigger cleanup
        if current_time - self.last_cleanup > self.cleanup_interval:
            self.last_cleanup = current_time
            # Trigger async cleanup (non-blocking)
            try:
                from app.infrastructure.security.token_rotation import RedisSessionStore
                # This runs in background
                import asyncio
                asyncio.create_task(RedisSessionStore.cleanup_expired_sessions())
            except Exception as e:
                logger.warning(f"Session cleanup failed: {str(e)}")
        
        return await call_next(request)
