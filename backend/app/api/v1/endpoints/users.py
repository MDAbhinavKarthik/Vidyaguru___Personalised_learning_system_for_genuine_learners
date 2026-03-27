"""
User Endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.user_service import UserService
from app.schemas.user import (
    UserProfileUpdate,
    OnboardingData,
    UserProfileResponse,
    CurrentUserResponse
)
from app.dependencies import get_current_user, get_current_active_user
from app.models.user import User


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Get current user"
)
async def get_current_user_info(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information.
    """
    service = UserService(db)
    return await service.get_current_user_response(current_user)


@router.get(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Get user profile"
)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's profile.
    """
    service = UserService(db)
    profile = await service.get_profile(current_user.id)
    return UserProfileResponse.model_validate(profile)


@router.patch(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Update user profile"
)
async def update_profile(
    data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user's profile.
    """
    service = UserService(db)
    profile = await service.update_profile(current_user.id, data)
    return UserProfileResponse.model_validate(profile)


@router.post(
    "/me/onboarding",
    response_model=UserProfileResponse,
    summary="Complete onboarding"
)
async def complete_onboarding(
    data: OnboardingData,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Complete the onboarding process with learning preferences.
    """
    service = UserService(db)
    profile = await service.complete_onboarding(current_user.id, data)
    return UserProfileResponse.model_validate(profile)


@router.patch(
    "/me/preferences",
    response_model=UserProfileResponse,
    summary="Update preferences"
)
async def update_preferences(
    preferences: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update user preferences (notifications, timezone, etc.).
    """
    service = UserService(db)
    profile = await service.update_preferences(current_user.id, preferences)
    return UserProfileResponse.model_validate(profile)


@router.get(
    "/me/learning-style",
    response_model=dict,
    summary="Get learning style"
)
async def get_learning_style(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's learning style assessment results.
    """
    service = UserService(db)
    return await service.get_learning_style(current_user.id)


@router.delete(
    "/me",
    response_model=dict,
    summary="Delete account"
)
async def delete_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete (soft delete) current user's account.
    """
    service = UserService(db)
    return await service.delete_user(current_user.id)
