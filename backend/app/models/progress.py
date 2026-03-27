"""
Progress & Achievement Database Models
"""
import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, Integer, DateTime, Date, ForeignKey, Enum, JSON, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class AchievementRarity(str, enum.Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class AchievementCategory(str, enum.Enum):
    LEARNING = "learning"
    STREAK = "streak"
    CHALLENGE = "challenge"
    SOCIAL = "social"
    MASTERY = "mastery"
    SPECIAL = "special"


class DailyProgress(Base):
    """Daily progress tracking"""
    __tablename__ = "daily_progress"
    
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
    
    # Date
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Activity metrics
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0)
    
    # Completion counts
    modules_completed: Mapped[int] = mapped_column(Integer, default=0)
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    challenges_attempted: Mapped[int] = mapped_column(Integer, default=0)
    
    # Streaks
    streak_maintained: Mapped[bool] = mapped_column(Boolean, default=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    
    # Journal activity
    journal_entries_created: Mapped[int] = mapped_column(Integer, default=0)
    
    # Mentor interactions
    mentor_messages_sent: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="progress_records")
    
    # Unique constraint
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    def __repr__(self):
        return f"<DailyProgress user={self.user_id} date={self.date}>"


class SkillLevel(Base):
    """Skill/competency tracking"""
    __tablename__ = "skill_levels"
    
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
    
    # Skill identification
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    skill_category: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Level metrics (0-100)
    current_level: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), default=50)
    
    # Assessment tracking
    assessments_count: Mapped[int] = mapped_column(Integer, default=0)
    last_assessed: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Historical data
    level_history: Mapped[dict] = mapped_column(JSON, default=list)
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="skill_levels")

    def __repr__(self):
        return f"<SkillLevel {self.skill_name}: {self.current_level}>"


class Achievement(Base):
    """Achievement/badge definitions"""
    __tablename__ = "achievements"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Achievement details
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Category and rarity
    category: Mapped[AchievementCategory] = mapped_column(
        Enum(AchievementCategory), 
        default=AchievementCategory.LEARNING
    )
    rarity: Mapped[AchievementRarity] = mapped_column(
        Enum(AchievementRarity), 
        default=AchievementRarity.COMMON
    )
    
    # Rewards
    xp_reward: Mapped[int] = mapped_column(Integer, default=0)
    
    # Criteria for earning (JSON schema)
    criteria: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Visibility
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Achievement {self.name}>"


class UserAchievement(Base):
    """User's earned achievements"""
    __tablename__ = "user_achievements"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("achievements.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    # When earned
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Progress data at time of earning
    progress_snapshot: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement")

    def __repr__(self):
        return f"<UserAchievement user={self.user_id} achievement={self.achievement_id}>"


# Import to avoid circular imports
from app.models.user import User
