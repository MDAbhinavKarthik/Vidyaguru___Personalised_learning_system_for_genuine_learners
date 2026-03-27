"""
User Schemas
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class LearningStyleEnum(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"


class ExperienceLevelEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class AccountStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# Base schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr


class UserProfileBase(BaseModel):
    """Base user profile schema"""
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    learning_style: Optional[LearningStyleEnum] = None
    experience_level: Optional[ExperienceLevelEnum] = ExperienceLevelEnum.BEGINNER
    weekly_time_commitment: Optional[int] = Field(5, ge=1, le=168)
    primary_goal: Optional[str] = Field(None, max_length=255)
    interests: Optional[list[str]] = []
    timezone: Optional[str] = "UTC"


# Create schemas
class UserCreate(UserBase):
    """Create user schema"""
    password: str = Field(..., min_length=8, max_length=128)
    display_name: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    """Create user profile schema"""
    pass


# Update schemas
class UserUpdate(BaseModel):
    """Update user schema"""
    email: Optional[EmailStr] = None


class UserProfileUpdate(BaseModel):
    """Update user profile schema"""
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    learning_style: Optional[LearningStyleEnum] = None
    experience_level: Optional[ExperienceLevelEnum] = None
    weekly_time_commitment: Optional[int] = Field(None, ge=1, le=168)
    primary_goal: Optional[str] = Field(None, max_length=255)
    interests: Optional[list[str]] = None
    timezone: Optional[str] = None
    notification_preferences: Optional[dict] = None


class OnboardingData(BaseModel):
    """Onboarding completion data"""
    learning_style: LearningStyleEnum
    experience_level: ExperienceLevelEnum
    weekly_time_commitment: int = Field(..., ge=1, le=168)
    primary_goal: str = Field(..., max_length=255)
    interests: list[str] = Field(..., min_length=1)
    timezone: Optional[str] = "UTC"


# Response schemas
class UserProfileResponse(UserProfileBase):
    """User profile response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    onboarding_completed: bool
    notification_preferences: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class UserResponse(UserBase):
    """User response without sensitive data"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email_verified: bool
    is_active: bool
    account_status: AccountStatusEnum
    two_factor_enabled: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    profile: Optional[UserProfileResponse] = None


class UserMinimal(BaseModel):
    """Minimal user info for references"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: EmailStr
    display_name: Optional[str] = None


class CurrentUserResponse(BaseModel):
    """Current authenticated user response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: EmailStr
    email_verified: bool
    is_active: bool
    two_factor_enabled: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    profile: Optional[UserProfileResponse] = None
    
    # Stats
    total_xp: Optional[int] = 0
    current_streak: Optional[int] = 0


class PreferencesUpdate(BaseModel):
    """User preferences update"""
    notification_preferences: Optional[dict] = None
    timezone: Optional[str] = None
    theme: Optional[str] = None
    language: Optional[str] = None
