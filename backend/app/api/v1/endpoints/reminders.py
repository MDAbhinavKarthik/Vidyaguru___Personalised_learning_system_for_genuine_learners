"""
Reminder Endpoints
"""
from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.reminder_service import ReminderService
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse,
    UpcomingRemindersResponse,
    SmartReminderSuggestion
)
from app.dependencies import get_current_active_user, PaginationParams
from app.models.user import User


router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.get(
    "",
    response_model=ReminderListResponse,
    summary="Get reminders"
)
async def get_reminders(
    active_only: bool = Query(True, description="Show only active reminders"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all reminders for the current user.
    """
    service = ReminderService(db)
    return await service.get_reminders(current_user.id, pagination, active_only)


@router.get(
    "/upcoming",
    response_model=UpcomingRemindersResponse,
    summary="Get upcoming reminders"
)
async def get_upcoming(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get upcoming reminders grouped by time (today, tomorrow, this week).
    """
    service = ReminderService(db)
    return await service.get_upcoming(current_user.id)


@router.get(
    "/suggestions",
    response_model=list[SmartReminderSuggestion],
    summary="Get smart suggestions"
)
async def get_suggestions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-powered reminder suggestions.
    """
    service = ReminderService(db)
    return await service.get_smart_suggestions(current_user.id)


@router.get(
    "/{reminder_id}",
    response_model=ReminderResponse,
    summary="Get reminder"
)
async def get_reminder(
    reminder_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific reminder.
    """
    service = ReminderService(db)
    reminder = await service.get_reminder(reminder_id, current_user.id)
    return ReminderResponse.model_validate(reminder)


@router.post(
    "",
    response_model=ReminderResponse,
    status_code=201,
    summary="Create reminder"
)
async def create_reminder(
    data: ReminderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new reminder.
    """
    service = ReminderService(db)
    reminder = await service.create_reminder(current_user.id, data)
    return ReminderResponse.model_validate(reminder)


@router.patch(
    "/{reminder_id}",
    response_model=ReminderResponse,
    summary="Update reminder"
)
async def update_reminder(
    reminder_id: UUID,
    data: ReminderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a reminder.
    """
    service = ReminderService(db)
    reminder = await service.update_reminder(reminder_id, current_user.id, data)
    return ReminderResponse.model_validate(reminder)


@router.delete(
    "/{reminder_id}",
    response_model=dict,
    summary="Delete reminder"
)
async def delete_reminder(
    reminder_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a reminder.
    """
    service = ReminderService(db)
    return await service.delete_reminder(reminder_id, current_user.id)


@router.post(
    "/{reminder_id}/complete",
    response_model=ReminderResponse,
    summary="Complete reminder"
)
async def complete_reminder(
    reminder_id: UUID,
    snooze_until: Optional[datetime] = Query(None, description="Snooze until this time"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Complete or snooze a reminder.
    """
    service = ReminderService(db)
    reminder = await service.complete_reminder(reminder_id, current_user.id, snooze_until)
    return ReminderResponse.model_validate(reminder)
