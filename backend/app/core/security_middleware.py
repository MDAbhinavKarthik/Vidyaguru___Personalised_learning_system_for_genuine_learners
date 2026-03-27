"""
API Security Middleware

Provides:
- Rate limiting
- Request validation
- Security headers
- IP blocking
- Request logging
"""

import time
import hashlib
from typing import Callable, Optional, Dict
from datetime import datetime, timedelta
from collections import defaultdict

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


class RateLimitExceeded(HTTPException):
    """Custom exception for rate limit exceeded"""
    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please slow down.",
                "retry_after": retry_after
            },
            headers={"Retry-After": str(retry_after)}
        )


class InMemoryRateLimiter:
    """
    Simple in-memory rate limiter using sliding window algorithm.
    For production, use Redis-based rate limiting.
    """
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.blocked_ips: Dict[str, datetime] = {}
    
    def _cleanup_old_requests(self, key: str, window_seconds: int):
        """Remove requests outside the current window"""
        cutoff = time.time() - window_seconds
        self.requests[key] = [ts for ts in self.requests[key] if ts > cutoff]
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is temporarily blocked"""
        if ip in self.blocked_ips:
            if datetime.utcnow() < self.blocked_ips[ip]:
                return True
            else:
                del self.blocked_ips[ip]
        return False
    
    def block_ip(self, ip: str, duration_minutes: int = 15):
        """Temporarily block an IP"""
        self.blocked_ips[ip] = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 60
    ) -> tuple[bool, int]:
        """
        Check if request is within rate limit.
        Returns (is_allowed, requests_remaining)
        """
        self._cleanup_old_requests(key, window_seconds)
        
        current_count = len(self.requests[key])
        
        if current_count >= max_requests:
            return False, 0
        
        self.requests[key].append(time.time())
        return True, max_requests - current_count - 1
    
    def get_retry_after(self, key: str, window_seconds: int = 60) -> int:
        """Get seconds until rate limit resets"""
        if not self.requests[key]:
            return 0
        
        oldest_request = min(self.requests[key])
        retry_after = int(oldest_request + window_seconds - time.time())
        return max(retry_after, 1)


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware that adds:
    - Security headers
    - Request ID tracking
    - Basic rate limiting
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = hashlib.md5(
            f"{time.time()}{request.client.host}".encode()
        ).hexdigest()[:12]
        
        # Add request ID to state
        request.state.request_id = request_id
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if rate_limiter.is_blocked(client_ip):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Your IP has been temporarily blocked due to suspicious activity.",
                    "request_id": request_id
                }
            )
        
        # Process request
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            self._log_request(request, 500, process_time, request_id)
            raise
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add security headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Add CSP header for API responses
        if request.url.path.startswith("/api"):
            response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        
        # Log request
        self._log_request(request, response.status_code, process_time, request_id)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP considering proxies"""
        # Check X-Forwarded-For header (set by nginx/proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        return request.client.host if request.client else "unknown"
    
    def _log_request(
        self,
        request: Request,
        status_code: int,
        process_time: float,
        request_id: str
    ):
        """Log request details"""
        client_ip = self._get_client_ip(request)
        
        # In production, use proper logging
        if settings.ENVIRONMENT == "development":
            log_level = "INFO" if status_code < 400 else "WARNING" if status_code < 500 else "ERROR"
            print(
                f"[{log_level}] {request_id} | {client_ip} | "
                f"{request.method} {request.url.path} | "
                f"{status_code} | {process_time:.3f}s"
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with different limits for different endpoints.
    """
    
    # Rate limit configurations (requests per minute)
    RATE_LIMITS = {
        "/api/v1/auth/login": (5, 60),      # 5 per minute
        "/api/v1/auth/register": (3, 60),   # 3 per minute
        "/api/v1/learning/generate": (10, 60),  # 10 per minute (AI calls)
        "/api/v1/challenges/generate": (5, 60),  # 5 per minute (AI calls)
        "default": (60, 60)  # 60 per minute for general endpoints
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier
        client_ip = self._get_client_ip(request)
        
        # Get rate limit for this endpoint
        max_requests, window = self._get_rate_limit(request.url.path)
        
        # Create rate limit key
        rate_key = f"{client_ip}:{request.url.path}"
        
        # Check rate limit
        is_allowed, remaining = rate_limiter.check_rate_limit(
            rate_key, max_requests, window
        )
        
        if not is_allowed:
            retry_after = rate_limiter.get_retry_after(rate_key, window)
            
            # If consistently hitting limits, consider blocking
            abuse_key = f"abuse:{client_ip}"
            rate_limiter.check_rate_limit(abuse_key, 10, 300)  # 10 violations in 5 min
            abuse_count = len(rate_limiter.requests.get(abuse_key, []))
            
            if abuse_count >= 10:
                rate_limiter.block_ip(client_ip, 15)  # Block for 15 minutes
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please slow down.",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP considering proxies"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _get_rate_limit(self, path: str) -> tuple[int, int]:
        """Get rate limit configuration for path"""
        # Check exact match first
        if path in self.RATE_LIMITS:
            return self.RATE_LIMITS[path]
        
        # Check prefix matches
        for route, limit in self.RATE_LIMITS.items():
            if route != "default" and path.startswith(route):
                return limit
        
        return self.RATE_LIMITS["default"]


class TrustedHostMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate Host header and prevent host header attacks.
    """
    
    def __init__(self, app, allowed_hosts: list[str] = None):
        super().__init__(app)
        self.allowed_hosts = allowed_hosts or ["*"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if "*" in self.allowed_hosts:
            return await call_next(request)
        
        host = request.headers.get("host", "").split(":")[0]
        
        if host not in self.allowed_hosts:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid host header"}
            )
        
        return await call_next(request)


def setup_security_middleware(app):
    """Setup all security middleware for the application"""
    from fastapi.middleware.trustedhost import TrustedHostMiddleware as FastAPITrustedHost
    
    # Add middleware in reverse order (last added = first executed)
    
    # Rate limiting
    app.add_middleware(RateLimitMiddleware)
    
    # Security headers and logging
    app.add_middleware(SecurityMiddleware)
    
    # Trusted hosts (in production)
    if settings.ENVIRONMENT == "production":
        allowed_hosts = ["yourdomain.com", "www.yourdomain.com", "api.yourdomain.com"]
        app.add_middleware(FastAPITrustedHost, allowed_hosts=allowed_hosts)
