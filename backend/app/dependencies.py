"""
Application Dependencies
Reusable dependencies for FastAPI routes
"""
from typing import Optional, Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.core.security import verify_token, SecurityError, ACCESS_TOKEN
from app.models.user import User

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Dependency to get current authenticated user
    Validates JWT token and retrieves user from database
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = verify_token(token, ACCESS_TOKEN)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except SecurityError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to ensure user is active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to ensure user has verified email
    """
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to ensure user is an admin
    """
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_optional_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(HTTPBearer(auto_error=False))],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Optional[User]:
    """
    Dependency to optionally get current user (for public endpoints that behave differently for authenticated users)
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token, ACCESS_TOKEN)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
            
        result = await db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        return result.scalar_one_or_none()
        
    except (SecurityError, Exception):
        return None


class RateLimiter:
    """
    Rate limiting dependency
    In production, use Redis for distributed rate limiting
    """
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds
        self._cache: dict = {}
    
    async def __call__(
        self,
        request: Request,
        user: Annotated[Optional[User], Depends(get_optional_user)]
    ) -> bool:
        """Check rate limit by user when available, otherwise by client IP."""
        # Simplified in-memory rate limiting
        # In production, use Redis
        from datetime import datetime, timedelta
        
        if user is not None:
            user_key = f"user:{user.id}"
        else:
            client_ip = request.client.host if request.client else "anonymous"
            user_key = f"ip:{client_ip}"
        now = datetime.utcnow()
        
        if user_key not in self._cache:
            self._cache[user_key] = {"count": 1, "window_start": now}
            return True
        
        user_data = self._cache[user_key]
        window_start = user_data["window_start"]
        
        if now - window_start > timedelta(seconds=self.seconds):
            # Reset window
            self._cache[user_key] = {"count": 1, "window_start": now}
            return True
        
        if user_data["count"] >= self.times:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        user_data["count"] += 1
        return True


# Common rate limiters
rate_limit_standard = RateLimiter(times=60, seconds=60)
rate_limit_ai = RateLimiter(times=20, seconds=60)


# Redis dependency (optional)
_redis_client = None

async def get_redis():
    """
    Get Redis client (optional dependency).
    Returns None if Redis is not available.
    """
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    try:
        from redis.asyncio import Redis
        from app.config import settings
        
        _redis_client = Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        # Test connection
        await _redis_client.ping()
        return _redis_client
    except Exception:
        # Redis not available, return None
        return None


# Pagination dependency
class PaginationParams:
    """Pagination parameters"""
    def __init__(
        self,
        page: int = 1,
        size: int = 20,
        max_size: int = 100
    ):
        self.page = max(1, page)
        self.size = min(max(1, size), max_size)
        self.offset = (self.page - 1) * self.size


def get_pagination(page: int = 1, size: int = 20) -> PaginationParams:
    """Get pagination parameters"""
    return PaginationParams(page=page, size=size)
