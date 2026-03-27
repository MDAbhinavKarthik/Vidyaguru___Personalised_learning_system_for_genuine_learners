"""
User Service
User profile and preferences management
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.user import User, UserProfile
from app.schemas.user import (
    UserProfileUpdate,
    OnboardingData,
    UserResponse,
    UserProfileResponse,
    CurrentUserResponse
)


class UserService:
    """User management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user(self, user_id: UUID) -> User:
        """Get user by ID with profile"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.profile))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    
    async def get_current_user_response(self, user: User) -> CurrentUserResponse:
        """Get current user response with stats"""
        # Load profile explicitly to avoid async lazy-load issues.
        await self.db.refresh(user, ["profile"])
        
        # Calculate stats (simplified, would aggregate from progress records)
        total_xp = 0
        current_streak = 0
        
        # Get XP from progress records
        from app.models.progress import DailyProgress
        from sqlalchemy import func
        
        xp_result = await self.db.execute(
            select(func.sum(DailyProgress.xp_earned))
            .where(DailyProgress.user_id == user.id)
        )
        total_xp = xp_result.scalar() or 0
        
        # Get current streak
        streak_result = await self.db.execute(
            select(DailyProgress.current_streak)
            .where(DailyProgress.user_id == user.id)
            .order_by(DailyProgress.date.desc())
            .limit(1)
        )
        current_streak = streak_result.scalar() or 0
        
        return CurrentUserResponse(
            id=user.id,
            email=user.email,
            email_verified=user.email_verified,
            is_active=user.is_active,
            two_factor_enabled=user.two_factor_enabled,
            created_at=user.created_at,
            last_login=user.last_login,
            profile=UserProfileResponse.model_validate(user.profile) if user.profile else None,
            total_xp=total_xp,
            current_streak=current_streak
        )
    
    async def get_profile(self, user_id: UUID) -> UserProfile:
        """Get user profile"""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return profile
    
    async def update_profile(self, user_id: UUID, data: UserProfileUpdate) -> UserProfile:
        """Update user profile"""
        profile = await self.get_profile(user_id)
        
        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        await self.db.commit()
        await self.db.refresh(profile)
        
        return profile
    
    async def complete_onboarding(self, user_id: UUID, data: OnboardingData) -> UserProfile:
        """Complete user onboarding"""
        profile = await self.get_profile(user_id)
        
        profile.learning_style = data.learning_style
        profile.experience_level = data.experience_level
        profile.weekly_time_commitment = data.weekly_time_commitment
        profile.primary_goal = data.primary_goal
        profile.interests = data.interests
        profile.timezone = data.timezone
        profile.onboarding_completed = True
        
        await self.db.commit()
        await self.db.refresh(profile)
        
        return profile
    
    async def update_preferences(self, user_id: UUID, preferences: dict) -> UserProfile:
        """Update notification and other preferences"""
        profile = await self.get_profile(user_id)
        
        # Merge with existing preferences
        existing = profile.notification_preferences or {}
        existing.update(preferences.get("notification_preferences", {}))
        profile.notification_preferences = existing
        
        if "timezone" in preferences:
            profile.timezone = preferences["timezone"]
        
        await self.db.commit()
        await self.db.refresh(profile)
        
        return profile
    
    async def delete_user(self, user_id: UUID) -> dict:
        """Soft delete user account"""
        user = await self.get_user(user_id)
        
        from app.models.user import AccountStatus
        user.is_active = False
        user.account_status = AccountStatus.DELETED
        
        await self.db.commit()
        
        return {"message": "Account deleted successfully"}
    
    async def get_learning_style(self, user_id: UUID) -> dict:
        """Get user's learning style assessment"""
        profile = await self.get_profile(user_id)
        
        return {
            "learning_style": profile.learning_style,
            "experience_level": profile.experience_level,
            "weekly_time_commitment": profile.weekly_time_commitment,
            "primary_goal": profile.primary_goal,
            "interests": profile.interests
        }
