"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # user_id
    email: str
    exp: datetime
    iat: datetime
    jti: Optional[str] = None  # JWT ID for refresh token tracking


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    remember_me: bool = False


class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    display_name: Optional[str] = Field(None, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "learner@example.com",
                "password": "securepassword123",
                "display_name": "John Doe"
            }
        }


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordChangeRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class EmailVerifyRequest(BaseModel):
    """Email verification request"""
    token: str


class TwoFactorSetupResponse(BaseModel):
    """2FA setup response"""
    secret: str
    qr_code_url: str
    backup_codes: list[str]


class TwoFactorVerifyRequest(BaseModel):
    """2FA verification request"""
    code: str = Field(..., min_length=6, max_length=6)


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request"""
    code: str
    state: Optional[str] = None
    provider: str


class AuthResponse(BaseModel):
    """Generic auth response"""
    message: str
    success: bool = True
