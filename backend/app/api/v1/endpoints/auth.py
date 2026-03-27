"""
Authentication Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    EmailVerifyRequest
)
from app.dependencies import get_current_user, RateLimiter
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])

# Rate limiter for auth endpoints
auth_rate_limiter = RateLimiter(times=10, seconds=60)


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(auth_rate_limiter)
):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Strong password (8+ chars, uppercase, lowercase, number, special char)
    - **display_name**: Name to display in the app
    """
    service = AuthService(db)
    result = await service.register(data)
    return result


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login to get access token"
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(auth_rate_limiter)
):
    """
    Authenticate and receive access & refresh tokens.
    
    - Access token expires in 30 minutes
    - Refresh token expires in 7 days
    """
    service = AuthService(db)
    return await service.login(data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token"
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a new access token using refresh token.
    """
    service = AuthService(db)
    return await service.refresh_token(data.refresh_token)


@router.post(
    "/verify-email",
    response_model=dict,
    summary="Verify email address"
)
async def verify_email(
    data: EmailVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify email address using token sent to email.
    """
    service = AuthService(db)
    return await service.verify_email(data.token)


@router.post(
    "/request-password-reset",
    response_model=dict,
    summary="Request password reset"
)
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(auth_rate_limiter)
):
    """
    Request a password reset link to be sent to email.
    """
    service = AuthService(db)
    return await service.request_password_reset(data)


@router.post(
    "/reset-password",
    response_model=dict,
    summary="Reset password"
)
async def reset_password(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using token from email.
    """
    service = AuthService(db)
    return await service.reset_password(data)


@router.post(
    "/change-password",
    response_model=dict,
    summary="Change password"
)
async def change_password(
    data: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change password for authenticated user.
    """
    service = AuthService(db)
    return await service.change_password(current_user.id, data)


@router.post(
    "/logout",
    response_model=dict,
    summary="Logout"
)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user.
    
    Note: In a real implementation, you would invalidate the token.
    For stateless JWT, simply discard the token on the client side.
    """
    return {"message": "Successfully logged out"}
