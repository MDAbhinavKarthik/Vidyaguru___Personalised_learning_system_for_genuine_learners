"""
Reminder Database Models
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class ReminderType(str, enum.Enum):
    STUDY = "study"
    REVIEW = "review"
    DEADLINE = "deadline"
    STREAK = "streak"
    CUSTOM = "custom"
    REFLECTION = "reflection"


class RepeatPattern(str, enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class NotificationChannel(str, enum.Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class Reminder(Base):
    """User reminder model"""
    __tablename__ = "reminders"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    # Reminder details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    reminder_type: Mapped[ReminderType] = mapped_column(
        Enum(ReminderType), 
        default=ReminderType.CUSTOM
    )
    
    # Scheduling
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    repeat_pattern: Mapped[RepeatPattern] = mapped_column(
        Enum(RepeatPattern), 
        default=RepeatPattern.NONE
    )
    repeat_config: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Notification settings
    channels: Mapped[list] = mapped_column(JSON, default=["in_app"])
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Tracking
    last_sent: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    send_count: Mapped[int] = mapped_column(default=0)
    
    # Related entities
    related_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        nullable=True
    )
    related_module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder {self.title} at {self.scheduled_at}>"


# Import to avoid circular imports
from app.models.user import User
