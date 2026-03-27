"""
Journal Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class EntryTypeEnum(str, Enum):
    IDEA = "idea"
    NOTE = "note"
    CONNECTION = "connection"
    QUESTION = "question"
    ACHIEVEMENT = "achievement"
    BUG_LOG = "bug_log"
    GOAL = "goal"
    REFLECTION = "reflection"


class MoodEnum(str, Enum):
    EXCITED = "excited"
    HAPPY = "happy"
    NEUTRAL = "neutral"
    CONFUSED = "confused"
    FRUSTRATED = "frustrated"
    DETERMINED = "determined"


# Tag Schemas
class TagBase(BaseModel):
    """Base tag schema"""
    name: str = Field(..., max_length=50)
    color: str = Field("#6366f1", pattern=r"^#[0-9A-Fa-f]{6}$")


class TagCreate(TagBase):
    """Create tag schema"""
    pass


class TagResponse(TagBase):
    """Tag response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime


# Journal Entry Schemas
class JournalEntryBase(BaseModel):
    """Base journal entry schema"""
    title: Optional[str] = Field(None, max_length=255)
    content: str = Field(..., min_length=1)
    entry_type: EntryTypeEnum = EntryTypeEnum.NOTE
    mood: Optional[MoodEnum] = None


class JournalEntryCreate(JournalEntryBase):
    """Create journal entry schema"""
    rich_content: Optional[dict] = None
    tag_ids: Optional[list[UUID]] = []
    linked_entry_ids: Optional[list[UUID]] = []
    related_module_id: Optional[UUID] = None
    related_task_id: Optional[UUID] = None


class JournalEntryUpdate(BaseModel):
    """Update journal entry schema"""
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    entry_type: Optional[EntryTypeEnum] = None
    mood: Optional[MoodEnum] = None
    rich_content: Optional[dict] = None
    tag_ids: Optional[list[UUID]] = None
    linked_entry_ids: Optional[list[UUID]] = None


class JournalEntryResponse(JournalEntryBase):
    """Journal entry response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    rich_content: Optional[dict] = None
    ai_insights: Optional[dict] = None
    linked_entry_ids: list[UUID] = []
    related_module_id: Optional[UUID] = None
    related_task_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = []


class JournalEntryListResponse(BaseModel):
    """Paginated journal entries response"""
    items: list[JournalEntryResponse]
    total: int
    page: int
    size: int
    pages: int


class JournalReflectionRequest(BaseModel):
    """Request AI reflection on entry"""
    entry_id: UUID
    reflection_type: str = "general"  # general, actionable, connections


class JournalReflectionResponse(BaseModel):
    """AI reflection response"""
    entry_id: UUID
    reflection: str
    suggested_connections: list[UUID]
    action_items: list[str]
    insights: dict


class JournalInsightsResponse(BaseModel):
    """Journal insights summary"""
    total_entries: int
    entries_by_type: dict[str, int]
    mood_distribution: dict[str, int]
    top_tags: list[TagResponse]
    weekly_activity: list[dict]
    ai_summary: Optional[str] = None
    patterns_detected: list[str]


class JournalSearchRequest(BaseModel):
    """Journal search request"""
    query: str = Field(..., min_length=1)
    entry_types: Optional[list[EntryTypeEnum]] = None
    tag_ids: Optional[list[UUID]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    mood: Optional[MoodEnum] = None
