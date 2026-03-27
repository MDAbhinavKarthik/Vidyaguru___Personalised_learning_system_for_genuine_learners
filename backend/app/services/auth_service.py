"""
Authentication Service
Handles user registration, login, and token management
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User, UserProfile
from app.schemas.auth import (
    LoginRequest, 
    RegisterRequest, 
    TokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest
)
from app.core.security import (
    get_password_hash, 
    verify_password, 
    create_tokens,
    verify_token,
    create_email_verification_token,
    verify_email_token,
    create_password_reset_token,
    verify_password_reset_token,
    validate_password_strength,
    REFRESH_TOKEN,
    SecurityError
)


class AuthService:
    """Authentication service for user management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(self, data: RegisterRequest) -> dict:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self._get_user_by_email(data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password strength
        is_valid, issues = validate_password_strength(data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Password does not meet requirements", "issues": issues}
            )
        
        # Create user
        user = User(
            email=data.email,
            password_hash=get_password_hash(data.password)
        )
        self.db.add(user)
        await self.db.flush()
        
        # Create profile
        profile = UserProfile(
            user_id=user.id,
            display_name=data.display_name
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(user)
        
        # Generate tokens
        tokens = create_tokens(user.id, user.email)
        
        # Create verification token
        verification_token = create_email_verification_token(user.email)
        
        return {
            **tokens,
            "user_id": str(user.id),
            "verification_token": verification_token,
            "message": "Registration successful. Please verify your email."
        }
    
    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate user and return tokens"""
        user = await self._get_user_by_email(data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please use OAuth to login"
            )
        
        if not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        # Generate tokens
        tokens = create_tokens(user.id, user.email)
        
        return TokenResponse(**tokens)
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        try:
            payload = verify_token(refresh_token, REFRESH_TOKEN)
            user_id = payload.get("sub")
            email = payload.get("email")
            
            # Verify user still exists and is active
            user = await self._get_user_by_id(UUID(user_id))
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Generate new tokens
            tokens = create_tokens(user.id, user.email)
            return TokenResponse(**tokens)
            
        except SecurityError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
    
    async def verify_email(self, token: str) -> dict:
        """Verify user email"""
        try:
            email = verify_email_token(token)
            user = await self._get_user_by_email(email)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user.email_verified = True
            await self.db.commit()
            
            return {"message": "Email verified successfully"}
            
        except SecurityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
    
    async def request_password_reset(self, data: PasswordResetRequest) -> dict:
        """Request password reset"""
        user = await self._get_user_by_email(data.email)
        
        # Always return success to prevent email enumeration
        if not user:
            return {"message": "If the email exists, a reset link has been sent"}
        
        reset_token = create_password_reset_token(user.email)
        
        # TODO: Send email with reset token
        # For now, return the token (in production, send via email)
        
        return {
            "message": "If the email exists, a reset link has been sent",
            "reset_token": reset_token  # Remove in production
        }
    
    async def reset_password(self, data: PasswordResetConfirm) -> dict:
        """Reset password using token"""
        try:
            email = verify_password_reset_token(data.token)
            user = await self._get_user_by_email(email)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Validate new password
            is_valid, issues = validate_password_strength(data.new_password)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"message": "Password does not meet requirements", "issues": issues}
                )
            
            user.password_hash = get_password_hash(data.new_password)
            await self.db.commit()
            
            return {"message": "Password reset successfully"}
            
        except SecurityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
    
    async def change_password(self, user_id: UUID, data: PasswordChangeRequest) -> dict:
        """Change password for authenticated user"""
        user = await self._get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not verify_password(data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        is_valid, issues = validate_password_strength(data.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Password does not meet requirements", "issues": issues}
            )
        
        user.password_hash = get_password_hash(data.new_password)
        await self.db.commit()
        
        return {"message": "Password changed successfully"}
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def _get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
