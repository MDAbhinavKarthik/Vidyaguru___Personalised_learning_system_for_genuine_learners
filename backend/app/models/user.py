"""
User Database Models
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class LearningStyle(str, enum.Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"


class ExperienceLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # OAuth fields
    oauth_provider: Mapped[str] = mapped_column(String(50), nullable=True)
    oauth_id: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Account status
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    account_status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus), 
        default=AccountStatus.ACTIVE
    )
    
    # Two-factor auth
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_secret: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile", 
        back_populates="user", 
        uselist=False,
        cascade="all, delete-orphan"
    )
    learning_paths: Mapped[list["LearningPath"]] = relationship(
        "LearningPath", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    journal_entries: Mapped[list["JournalEntry"]] = relationship(
        "JournalEntry", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    progress_records: Mapped[list["DailyProgress"]] = relationship(
        "DailyProgress",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    skill_levels: Mapped[list["SkillLevel"]] = relationship(
        "SkillLevel",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"


class UserProfile(Base):
    """User profile with preferences and settings"""
    __tablename__ = "user_profiles"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True
    )
    
    # Profile info
    display_name: Mapped[str] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Learning preferences
    learning_style: Mapped[LearningStyle] = mapped_column(
        Enum(LearningStyle), 
        nullable=True
    )
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        Enum(ExperienceLevel), 
        default=ExperienceLevel.BEGINNER
    )
    weekly_time_commitment: Mapped[int] = mapped_column(default=5)  # hours
    
    # Goals and interests
    primary_goal: Mapped[str] = mapped_column(String(255), nullable=True)
    interests: Mapped[list] = mapped_column(JSON, default=list)
    
    # Settings
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    notification_preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Onboarding
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile {self.display_name}>"


# Import these at the bottom to avoid circular imports
from app.models.learning import LearningPath, Enrollment
from app.models.task import Task
from app.models.journal import JournalEntry
from app.models.reminder import Reminder
from app.models.conversation import Conversation
from app.models.progress import DailyProgress, SkillLevel, UserAchievement
