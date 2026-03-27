"""
Progress Endpoints
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.progress_service import ProgressService
from app.schemas.progress import (
    ProgressOverviewResponse,
    DailyProgressResponse,
    SkillRadarResponse,
    AchievementListResponse,
    StreakResponse,
    TimelineResponse,
    ProgressAnalyticsResponse
)
from app.dependencies import get_current_active_user, PaginationParams
from app.models.user import User


router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get(
    "/overview",
    response_model=ProgressOverviewResponse,
    summary="Get progress overview"
)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get overall progress overview including XP, level, and streaks.
    """
    service = ProgressService(db)
    return await service.get_overview(current_user.id)


@router.get(
    "/skills",
    response_model=SkillRadarResponse,
    summary="Get skill levels"
)
async def get_skills(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get skill levels and radar chart data.
    """
    service = ProgressService(db)
    return await service.get_skills(current_user.id)


@router.get(
    "/achievements",
    response_model=AchievementListResponse,
    summary="Get achievements"
)
async def get_achievements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get earned and available achievements.
    """
    service = ProgressService(db)
    return await service.get_achievements(current_user.id)


@router.get(
    "/streak",
    response_model=StreakResponse,
    summary="Get streak info"
)
async def get_streak(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed streak information.
    """
    service = ProgressService(db)
    return await service.get_streak(current_user.id)


@router.get(
    "/timeline",
    response_model=TimelineResponse,
    summary="Get activity timeline"
)
async def get_timeline(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get activity timeline/history.
    """
    service = ProgressService(db)
    return await service.get_timeline(current_user.id, page, size)


@router.get(
    "/analytics",
    response_model=ProgressAnalyticsResponse,
    summary="Get analytics"
)
async def get_analytics(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed progress analytics.
    """
    service = ProgressService(db)
    return await service.get_analytics(current_user.id, days)


@router.post(
    "/record",
    response_model=DailyProgressResponse,
    summary="Record progress"
)
async def record_progress(
    xp_earned: int = 0,
    time_spent_minutes: int = 0,
    modules_completed: int = 0,
    tasks_completed: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Record daily progress (usually called automatically by other services).
    """
    service = ProgressService(db)
    progress = await service.record_progress(
        current_user.id,
        xp_earned=xp_earned,
        time_spent_minutes=time_spent_minutes,
        modules_completed=modules_completed,
        tasks_completed=tasks_completed
    )
    return DailyProgressResponse.model_validate(progress)
