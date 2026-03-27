"""
Reminder Service
Reminder and notification management
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException, status

from app.models.reminder import Reminder, ReminderType, RepeatPattern
from app.schemas.reminder import (
    ReminderCreate, ReminderUpdate,
    ReminderResponse, ReminderListResponse,
    UpcomingRemindersResponse, SmartReminderSuggestion
)
from app.dependencies import PaginationParams


class ReminderService:
    """Reminder management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_reminders(
        self,
        user_id: UUID,
        pagination: PaginationParams,
        active_only: bool = True
    ) -> ReminderListResponse:
        """Get user's reminders with pagination"""
        query = select(Reminder).where(Reminder.user_id == user_id)
        
        if active_only:
            query = query.where(Reminder.is_active == True)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)
        
        # Get paginated results
        query = query.order_by(Reminder.scheduled_at)
        query = query.offset(pagination.offset).limit(pagination.size)
        
        result = await self.db.execute(query)
        reminders = result.scalars().all()
        
        return ReminderListResponse(
            items=[ReminderResponse.model_validate(r) for r in reminders],
            total=total,
            page=pagination.page,
            size=pagination.size
        )
    
    async def get_reminder(self, reminder_id: UUID, user_id: UUID) -> Reminder:
        """Get reminder by ID"""
        result = await self.db.execute(
            select(Reminder)
            .where(Reminder.id == reminder_id, Reminder.user_id == user_id)
        )
        reminder = result.scalar_one_or_none()
        
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )
        
        return reminder
    
    async def create_reminder(self, user_id: UUID, data: ReminderCreate) -> Reminder:
        """Create a new reminder"""
        reminder = Reminder(
            user_id=user_id,
            title=data.title,
            description=data.description,
            reminder_type=data.reminder_type,
            scheduled_at=data.scheduled_at,
            repeat_pattern=data.repeat_pattern,
            repeat_config=data.repeat_config,
            channels=data.channels,
            related_task_id=data.related_task_id,
            related_module_id=data.related_module_id
        )
        
        self.db.add(reminder)
        await self.db.commit()
        await self.db.refresh(reminder)
        
        return reminder
    
    async def update_reminder(self, reminder_id: UUID, user_id: UUID, data: ReminderUpdate) -> Reminder:
        """Update reminder"""
        reminder = await self.get_reminder(reminder_id, user_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(reminder, field, value)
        
        await self.db.commit()
        await self.db.refresh(reminder)
        
        return reminder
    
    async def delete_reminder(self, reminder_id: UUID, user_id: UUID) -> dict:
        """Delete reminder"""
        reminder = await self.get_reminder(reminder_id, user_id)
        
        await self.db.delete(reminder)
        await self.db.commit()
        
        return {"message": "Reminder deleted successfully"}
    
    async def complete_reminder(self, reminder_id: UUID, user_id: UUID, snooze_until: Optional[datetime] = None) -> Reminder:
        """Complete or snooze a reminder"""
        reminder = await self.get_reminder(reminder_id, user_id)
        
        if snooze_until:
            # Snooze
            reminder.scheduled_at = snooze_until
        else:
            # Complete
            if reminder.repeat_pattern == RepeatPattern.NONE:
                reminder.is_completed = True
                reminder.is_active = False
            else:
                # Schedule next occurrence
                reminder.scheduled_at = self._get_next_occurrence(reminder)
        
        reminder.send_count += 1
        reminder.last_sent = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(reminder)
        
        return reminder
    
    def _get_next_occurrence(self, reminder: Reminder) -> datetime:
        """Calculate next occurrence based on repeat pattern"""
        current = reminder.scheduled_at
        
        if reminder.repeat_pattern == RepeatPattern.DAILY:
            return current + timedelta(days=1)
        elif reminder.repeat_pattern == RepeatPattern.WEEKLY:
            return current + timedelta(weeks=1)
        elif reminder.repeat_pattern == RepeatPattern.MONTHLY:
            return current + timedelta(days=30)
        elif reminder.repeat_pattern == RepeatPattern.CUSTOM:
            # Use repeat_config for custom patterns
            config = reminder.repeat_config or {}
            interval_days = config.get("interval_days", 1)
            return current + timedelta(days=interval_days)
        
        return current
    
    async def get_upcoming(self, user_id: UUID) -> UpcomingRemindersResponse:
        """Get upcoming reminders grouped by time"""
        now = datetime.utcnow()
        today_end = now.replace(hour=23, minute=59, second=59)
        tomorrow_end = today_end + timedelta(days=1)
        week_end = today_end + timedelta(days=7)
        
        # Get all active reminders
        result = await self.db.execute(
            select(Reminder)
            .where(
                Reminder.user_id == user_id,
                Reminder.is_active == True,
                Reminder.is_completed == False
            )
            .order_by(Reminder.scheduled_at)
        )
        reminders = result.scalars().all()
        
        today = []
        tomorrow = []
        this_week = []
        overdue = []
        
        for reminder in reminders:
            r = ReminderResponse.model_validate(reminder)
            
            if reminder.scheduled_at < now:
                overdue.append(r)
            elif reminder.scheduled_at <= today_end:
                today.append(r)
            elif reminder.scheduled_at <= tomorrow_end:
                tomorrow.append(r)
            elif reminder.scheduled_at <= week_end:
                this_week.append(r)
        
        return UpcomingRemindersResponse(
            today=today,
            tomorrow=tomorrow,
            this_week=this_week,
            overdue=overdue
        )
    
    async def get_smart_suggestions(self, user_id: UUID) -> List[SmartReminderSuggestion]:
        """Get AI-powered reminder suggestions"""
        suggestions = []
        now = datetime.utcnow()
        
        # Suggest study reminder if none exists
        study_reminders = await self.db.execute(
            select(Reminder)
            .where(
                Reminder.user_id == user_id,
                Reminder.reminder_type == ReminderType.STUDY,
                Reminder.is_active == True
            )
        )
        if not study_reminders.scalar_one_or_none():
            suggestions.append(SmartReminderSuggestion(
                suggested_title="Daily Study Session",
                suggested_time=now.replace(hour=9, minute=0, second=0) + timedelta(days=1),
                reason="Consistent daily study improves retention by 40%",
                reminder_type=ReminderType.STUDY,
                related_to="Learning Path"
            ))
        
        # Suggest review reminder
        suggestions.append(SmartReminderSuggestion(
            suggested_title="Weekly Review",
            suggested_time=now.replace(hour=18, minute=0, second=0) + timedelta(days=(6 - now.weekday())),
            reason="Spaced repetition is key to long-term memory",
            reminder_type=ReminderType.REVIEW,
            related_to="Recent Modules"
        ))
        
        # Suggest streak reminder if user has active streak
        from app.services.progress_service import ProgressService
        # Would check streak and suggest reminder to maintain it
        
        return suggestions
    
    async def create_study_reminder_series(
        self,
        user_id: UUID,
        start_time: datetime,
        days: List[int],  # 0=Monday, 6=Sunday
        duration_weeks: int = 4
    ) -> List[Reminder]:
        """Create a series of study reminders"""
        reminders = []
        current = start_time
        
        for week in range(duration_weeks):
            for day in days:
                # Calculate the date for this day
                days_ahead = day - current.weekday()
                if days_ahead < 0:
                    days_ahead += 7
                
                reminder_date = current + timedelta(days=days_ahead + (week * 7))
                
                reminder = Reminder(
                    user_id=user_id,
                    title=f"Study Session",
                    description="Time for your scheduled study session",
                    reminder_type=ReminderType.STUDY,
                    scheduled_at=reminder_date,
                    repeat_pattern=RepeatPattern.WEEKLY if week == 0 else RepeatPattern.NONE,
                    channels=["in_app", "push"]
                )
                
                if week == 0:  # Only add first week reminders (they'll repeat)
                    self.db.add(reminder)
                    reminders.append(reminder)
        
        await self.db.commit()
        
        for r in reminders:
            await self.db.refresh(r)
        
        return reminders
