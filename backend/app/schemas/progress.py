"""
Progress Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from enum import Enum


class AchievementRarityEnum(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class AchievementCategoryEnum(str, Enum):
    LEARNING = "learning"
    STREAK = "streak"
    CHALLENGE = "challenge"
    SOCIAL = "social"
    MASTERY = "mastery"
    SPECIAL = "special"


# Daily Progress Schemas
class DailyProgressBase(BaseModel):
    """Base daily progress schema"""
    xp_earned: int = 0
    time_spent_minutes: int = 0
    modules_completed: int = 0
    tasks_completed: int = 0


class DailyProgressResponse(DailyProgressBase):
    """Daily progress response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    date: date
    challenges_attempted: int
    streak_maintained: bool
    current_streak: int
    journal_entries_created: int
    mentor_messages_sent: int


class ProgressOverviewResponse(BaseModel):
    """Overall progress overview"""
    total_xp: int
    current_level: int
    xp_to_next_level: int
    current_streak: int
    longest_streak: int
    total_time_spent_hours: float
    modules_completed: int
    tasks_completed: int
    challenges_completed: int
    achievements_earned: int
    rank_percentile: Optional[float] = None


# Skill Level Schemas
class SkillLevelBase(BaseModel):
    """Base skill level schema"""
    skill_name: str = Field(..., max_length=100)
    skill_category: Optional[str] = None


class SkillLevelCreate(SkillLevelBase):
    """Create skill level schema"""
    current_level: int = Field(0, ge=0, le=100)


class SkillLevelUpdate(BaseModel):
    """Update skill level schema"""
    current_level: Optional[int] = Field(None, ge=0, le=100)
    confidence_score: Optional[float] = Field(None, ge=0, le=100)


class SkillLevelResponse(SkillLevelBase):
    """Skill level response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    current_level: int
    confidence_score: float
    assessments_count: int
    last_assessed: Optional[datetime] = None
    level_history: list[dict] = []


class SkillRadarResponse(BaseModel):
    """Skill radar chart data"""
    skills: list[SkillLevelResponse]
    overall_score: float
    strengths: list[str]
    areas_to_improve: list[str]


# Achievement Schemas
class AchievementBase(BaseModel):
    """Base achievement schema"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    category: AchievementCategoryEnum
    rarity: AchievementRarityEnum


class AchievementResponse(AchievementBase):
    """Achievement response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    icon_url: Optional[str] = None
    xp_reward: int
    criteria: dict
    is_hidden: bool


class UserAchievementResponse(BaseModel):
    """User achievement response"""
    model_config = ConfigDict(from_attributes=True)
    
    achievement: AchievementResponse
    earned_at: datetime
    progress_snapshot: Optional[dict] = None


class AchievementListResponse(BaseModel):
    """Achievements list response"""
    earned: list[UserAchievementResponse]
    available: list[AchievementResponse]
    total_earned: int
    total_available: int


# Streak Schemas
class StreakResponse(BaseModel):
    """Streak information response"""
    current_streak: int
    longest_streak: int
    streak_start_date: Optional[date] = None
    last_activity_date: Optional[date] = None
    at_risk: bool  # True if no activity today
    streak_history: list[dict]


# Timeline/Activity Schemas
class ActivityItem(BaseModel):
    """Activity timeline item"""
    id: UUID
    activity_type: str
    title: str
    description: Optional[str] = None
    xp_earned: int
    timestamp: datetime
    metadata: Optional[dict] = None


class TimelineResponse(BaseModel):
    """Activity timeline response"""
    items: list[ActivityItem]
    total: int
    page: int
    size: int


# Analytics Schemas
class ProgressAnalyticsResponse(BaseModel):
    """Detailed progress analytics"""
    daily_progress: list[DailyProgressResponse]
    weekly_summary: dict
    monthly_summary: dict
    learning_velocity: float  # Modules per week
    consistency_score: float
    peak_learning_hours: list[int]
    skill_growth: list[dict]
    predictions: dict


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    user_id: UUID
    display_name: str
    avatar_url: Optional[str] = None
    xp: int
    level: int
    streak: int


class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    entries: list[LeaderboardEntry]
    user_rank: Optional[int] = None
    total_users: int
    period: str  # weekly, monthly, all-time
