"""
Reminder Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class ReminderTypeEnum(str, Enum):
    STUDY = "study"
    REVIEW = "review"
    DEADLINE = "deadline"
    STREAK = "streak"
    CUSTOM = "custom"
    REFLECTION = "reflection"


class RepeatPatternEnum(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class NotificationChannelEnum(str, Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


# Reminder Schemas
class ReminderBase(BaseModel):
    """Base reminder schema"""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    reminder_type: ReminderTypeEnum = ReminderTypeEnum.CUSTOM


class ReminderCreate(ReminderBase):
    """Create reminder schema"""
    scheduled_at: datetime
    repeat_pattern: RepeatPatternEnum = RepeatPatternEnum.NONE
    repeat_config: Optional[dict] = None
    channels: list[str] = ["in_app"]
    related_task_id: Optional[UUID] = None
    related_module_id: Optional[UUID] = None


class ReminderUpdate(BaseModel):
    """Update reminder schema"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    reminder_type: Optional[ReminderTypeEnum] = None
    scheduled_at: Optional[datetime] = None
    repeat_pattern: Optional[RepeatPatternEnum] = None
    repeat_config: Optional[dict] = None
    channels: Optional[list[str]] = None
    is_active: Optional[bool] = None


class ReminderResponse(ReminderBase):
    """Reminder response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    scheduled_at: datetime
    repeat_pattern: RepeatPatternEnum
    repeat_config: Optional[dict] = None
    channels: list[str]
    is_active: bool
    is_completed: bool
    last_sent: Optional[datetime] = None
    send_count: int
    related_task_id: Optional[UUID] = None
    related_module_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class ReminderListResponse(BaseModel):
    """Paginated reminders response"""
    items: list[ReminderResponse]
    total: int
    page: int
    size: int


class UpcomingRemindersResponse(BaseModel):
    """Upcoming reminders response"""
    today: list[ReminderResponse]
    tomorrow: list[ReminderResponse]
    this_week: list[ReminderResponse]
    overdue: list[ReminderResponse]


class ReminderCompleteRequest(BaseModel):
    """Complete/dismiss reminder request"""
    reminder_id: UUID
    snoozed_until: Optional[datetime] = None  # If snoozing instead of completing


class SmartReminderSuggestion(BaseModel):
    """AI-suggested reminder"""
    suggested_title: str
    suggested_time: datetime
    reason: str
    reminder_type: ReminderTypeEnum
    related_to: Optional[str] = None
