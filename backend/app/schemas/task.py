"""
Task Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class TaskTypeEnum(str, Enum):
    LEARNING = "learning"
    PRACTICE = "practice"
    PROJECT = "project"
    DAILY = "daily"
    CHALLENGE = "challenge"
    QUIZ = "quiz"


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    SKIPPED = "skipped"


class TaskDifficultyEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class VerificationStatusEnum(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FLAGGED = "flagged"
    REQUIRES_REVIEW = "requires_review"


# Task Schemas
class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    task_type: TaskTypeEnum = TaskTypeEnum.PRACTICE
    difficulty: TaskDifficultyEnum = TaskDifficultyEnum.MEDIUM


class TaskCreate(TaskBase):
    """Create task schema"""
    module_id: Optional[UUID] = None
    deadline: Optional[datetime] = None
    max_attempts: int = 3
    xp_reward: int = 5
    hints: Optional[list[str]] = []
    template_code: Optional[dict] = None
    test_cases: Optional[dict] = None


class TaskUpdate(BaseModel):
    """Update task schema"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    task_type: Optional[TaskTypeEnum] = None
    difficulty: Optional[TaskDifficultyEnum] = None
    status: Optional[TaskStatusEnum] = None
    deadline: Optional[datetime] = None


class TaskStartRequest(BaseModel):
    """Start task request"""
    task_id: UUID


# Submission Schemas
class SubmissionCreate(BaseModel):
    """Create submission schema"""
    task_id: UUID
    content: str = Field(..., min_length=1)
    language: Optional[str] = None
    time_spent_seconds: Optional[int] = None
    typing_pattern_data: Optional[dict] = None


class SubmissionResponse(BaseModel):
    """Submission response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    task_id: UUID
    user_id: UUID
    content: str
    language: Optional[str] = None
    score: Optional[float] = None
    max_score: float
    feedback: Optional[dict] = None
    ai_feedback: Optional[str] = None
    time_spent_seconds: Optional[int] = None
    verification_status: VerificationStatusEnum
    attempt_number: int
    tests_passed: Optional[int] = None
    tests_total: Optional[int] = None
    submitted_at: datetime
    evaluated_at: Optional[datetime] = None


class HintRequest(BaseModel):
    """Request hint for task"""
    task_id: UUID
    hint_index: Optional[int] = None  # Request specific hint or next available


class HintResponse(BaseModel):
    """Hint response"""
    hint: str
    hint_index: int
    total_hints: int
    xp_penalty: int


# Response Schemas
class TaskResponse(TaskBase):
    """Task response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    module_id: Optional[UUID] = None
    status: TaskStatusEnum
    deadline: Optional[datetime] = None
    max_attempts: int
    current_attempts: int
    xp_reward: int
    hints_used: int
    template_code: Optional[dict] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskDetailResponse(TaskResponse):
    """Task detail response with submissions"""
    hints: list[str] = []
    test_cases: Optional[dict] = None
    submissions: list[SubmissionResponse] = []


class TaskListResponse(BaseModel):
    """Paginated tasks response"""
    items: list[TaskResponse]
    total: int
    page: int
    size: int
    pages: int


class DailyTasksResponse(BaseModel):
    """Daily tasks response"""
    date: datetime
    tasks: list[TaskResponse]
    completed_count: int
    total_count: int
    xp_available: int


class TaskEvaluationResult(BaseModel):
    """Task evaluation result"""
    task_id: UUID
    submission_id: UUID
    score: float
    max_score: float
    passed: bool
    feedback: dict
    ai_feedback: str
    verification_status: VerificationStatusEnum
    xp_earned: int
    tests_passed: Optional[int] = None
    tests_total: Optional[int] = None
