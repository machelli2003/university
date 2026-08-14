from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
from typing import Dict, List

# Simple in-memory rate limiter for demonstration. Use Redis for production.
_requests: Dict[str, List[float]] = {}

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds

    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else "unknown"
        now = time.time()
        hits = _requests.get(client, [])
        # drop old timestamps
        hits = [t for t in hits if t > now - self.window]
        hits.append(now)
        _requests[client] = hits

        if len(hits) > self.max_requests:
            return Response(status_code=429, content="Too Many Requests")

        return await call_next(request)
