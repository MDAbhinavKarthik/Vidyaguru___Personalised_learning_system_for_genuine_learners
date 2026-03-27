"""
Learning Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from enum import Enum


class PathStatusEnum(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ModuleStatusEnum(str, Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ContentTypeEnum(str, Enum):
    THEORY = "theory"
    PRACTICE = "practice"
    PROJECT = "project"
    QUIZ = "quiz"
    VIDEO = "video"
    INTERACTIVE = "interactive"


class DifficultyEnum(str, Enum):
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


# Learning Path Schemas
class LearningPathBase(BaseModel):
    """Base learning path schema"""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None


class LearningPathCreate(LearningPathBase):
    """Create learning path schema"""
    estimated_duration_hours: Optional[int] = None
    target_completion_date: Optional[date] = None


class LearningPathUpdate(BaseModel):
    """Update learning path schema"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[PathStatusEnum] = None
    target_completion_date: Optional[date] = None


class LearningPathGenerate(BaseModel):
    """Generate personalized learning path request"""
    topic: str = Field(..., max_length=255)
    target_level: DifficultyEnum = DifficultyEnum.MEDIUM
    weekly_hours: int = Field(5, ge=1, le=40)
    include_projects: bool = True
    focus_areas: Optional[list[str]] = None


# Module Schemas
class ModuleBase(BaseModel):
    """Base module schema"""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    content_type: ContentTypeEnum = ContentTypeEnum.THEORY
    difficulty: DifficultyEnum = DifficultyEnum.MEDIUM


class ModuleCreate(ModuleBase):
    """Create module schema"""
    path_id: UUID
    order_index: int = 0
    estimated_minutes: int = 30
    xp_reward: int = 10
    prerequisites: Optional[list[UUID]] = []


class ModuleUpdate(BaseModel):
    """Update module schema"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    content_type: Optional[ContentTypeEnum] = None
    difficulty: Optional[DifficultyEnum] = None
    status: Optional[ModuleStatusEnum] = None
    order_index: Optional[int] = None


# Module Content Schemas
class ModuleContentBase(BaseModel):
    """Base module content schema"""
    content_type: str = Field(..., max_length=50)
    title: Optional[str] = None
    content_data: dict


class ModuleContentCreate(ModuleContentBase):
    """Create module content schema"""
    module_id: UUID
    order_index: int = 0


class ModuleContentUpdate(BaseModel):
    """Update module content schema"""
    title: Optional[str] = None
    content_data: Optional[dict] = None
    order_index: Optional[int] = None


# Response Schemas
class ModuleContentResponse(ModuleContentBase):
    """Module content response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    module_id: UUID
    order_index: int
    created_at: datetime


class ModuleResponse(ModuleBase):
    """Module response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    path_id: UUID
    order_index: int
    status: ModuleStatusEnum
    xp_reward: int
    estimated_minutes: int
    prerequisites: list[UUID]
    created_at: datetime
    completed_at: Optional[datetime] = None


class ModuleDetailResponse(ModuleResponse):
    """Module detail response with contents"""
    contents: list[ModuleContentResponse] = []


class LearningPathResponse(LearningPathBase):
    """Learning path response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    status: PathStatusEnum
    progress_percentage: float
    total_xp: int
    earned_xp: int
    estimated_duration_hours: Optional[int] = None
    target_completion_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class LearningPathDetailResponse(LearningPathResponse):
    """Learning path detail response with modules"""
    modules: list[ModuleResponse] = []


class LearningPathListResponse(BaseModel):
    """Paginated learning paths response"""
    items: list[LearningPathResponse]
    total: int
    page: int
    size: int
    pages: int


class RecommendationResponse(BaseModel):
    """Learning recommendation response"""
    module_id: UUID
    module_title: str
    reason: str
    priority: int
    estimated_time: int


class KnowledgeGraphNode(BaseModel):
    """Knowledge graph node"""
    id: UUID
    name: str
    type: str
    level: int
    connections: list[UUID]


class KnowledgeGraphResponse(BaseModel):
    """Knowledge graph response"""
    nodes: list[KnowledgeGraphNode]
    total_skills: int
    mastered_skills: int
