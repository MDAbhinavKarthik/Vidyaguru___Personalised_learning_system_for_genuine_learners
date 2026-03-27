"""
VidyaGuru Learning Engine API Schemas
Request/Response models for the learning flow API
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class LearningStageEnum(str, Enum):
    """Learning stages enum for API"""
    CONCEPT_INTRODUCTION = "concept_introduction"
    EXPLANATION = "explanation"
    REAL_WORLD_APPLICATION = "real_world_application"
    ANCIENT_KNOWLEDGE = "ancient_knowledge"
    PRACTICAL_TASK = "practical_task"
    COMMUNICATION_TASK = "communication_task"
    INDUSTRY_CHALLENGE = "industry_challenge"
    REFLECTION_SUMMARY = "reflection_summary"


class StageStatusEnum(str, Enum):
    """Stage status enum for API"""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class CreateLearningSessionRequest(BaseModel):
    """Request to create a new learning session"""
    topic: str = Field(..., min_length=1, max_length=200, description="Topic to learn")
    concept: Optional[str] = Field(None, max_length=200, description="Specific concept")
    difficulty: str = Field(
        default="intermediate",
        pattern="^(beginner|intermediate|advanced|expert)$",
        description="Difficulty level"
    )
    experience_level: str = Field(
        default="intermediate",
        pattern="^(beginner|intermediate|advanced|expert)$",
        description="Learner's experience level"
    )
    interests: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Learner's interests for personalization"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Decorators",
                "concept": "Function decorators with arguments",
                "difficulty": "intermediate",
                "experience_level": "intermediate",
                "interests": ["web development", "data science"]
            }
        }


class InteractionRequest(BaseModel):
    """Request to record an interaction"""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "I think decorators wrap functions to add extra behavior"
            }
        }


class SubmissionRequest(BaseModel):
    """Request to submit a task solution"""
    code: Optional[str] = Field(None, max_length=50000, description="Code solution")
    explanation: str = Field(..., min_length=20, max_length=10000, description="Explanation")
    language: str = Field(default="python", description="Programming language")
    alternative_approaches: Optional[List[str]] = Field(
        None,
        max_length=5,
        description="Alternative approaches considered"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "code": "def my_decorator(func):\n    def wrapper(*args):\n        print('Before')\n        result = func(*args)\n        print('After')\n        return result\n    return wrapper",
                "explanation": "I created a decorator that prints 'Before' and 'After' around the function call. The wrapper function captures any arguments using *args and passes them to the original function.",
                "language": "python",
                "alternative_approaches": ["Could use functools.wraps for better metadata preservation"]
            }
        }


class AdvanceStageRequest(BaseModel):
    """Request to advance to next stage"""
    force: bool = Field(
        default=False,
        description="Force advancement (admin only, 50% XP penalty)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "force": False
            }
        }


class VerificationAnswerRequest(BaseModel):
    """Request to answer verification questions"""
    answers: Dict[str, str] = Field(
        ...,
        description="Map of question IDs to answers"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "answers": {
                    "q1": "The decorator wraps the function to add logging",
                    "q2": "We could use classes instead of nested functions"
                }
            }
        }


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class StageInfoResponse(BaseModel):
    """Information about a single stage"""
    stage: LearningStageEnum
    title: str
    description: str
    status: StageStatusEnum
    is_current: bool
    xp_reward: int
    xp_earned: int
    interactions: int
    min_interactions: int
    time_spent_seconds: float
    min_time_seconds: int
    can_advance: Optional[bool] = None
    unmet_requirements: Optional[List[str]] = None


class StageContentResponse(BaseModel):
    """Content for a learning stage"""
    stage: LearningStageEnum
    title: str
    description: str
    objectives: List[str]
    completion_criteria: str
    xp_reward: int
    mentor_prompt: str  # The contextual prompt for the mentor


class LearningSessionResponse(BaseModel):
    """Response with learning session details"""
    session_id: str
    user_id: str
    topic: str
    concept: Optional[str]
    difficulty: str
    current_stage: LearningStageEnum
    overall_progress_percent: int
    total_xp: int
    max_xp: int
    is_complete: bool
    is_paused: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-123",
                "topic": "Python Decorators",
                "concept": "Function decorators",
                "difficulty": "intermediate",
                "current_stage": "explanation",
                "overall_progress_percent": 25,
                "total_xp": 35,
                "max_xp": 235,
                "is_complete": False,
                "is_paused": False,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T11:00:00Z"
            }
        }


class ProgressResponse(BaseModel):
    """Complete progress report for a session"""
    session_id: str
    topic: str
    current_stage: LearningStageEnum
    overall_progress_percent: int
    total_xp: int
    max_xp: int
    stages: List[StageInfoResponse]
    is_complete: bool


class AdvanceStageResponse(BaseModel):
    """Response when advancing to next stage"""
    success: bool
    message: str
    new_stage: Optional[LearningStageEnum] = None
    xp_earned: int = 0
    stage_content: Optional[StageContentResponse] = None


class InteractionResponse(BaseModel):
    """Response after recording an interaction"""
    success: bool
    stage: LearningStageEnum
    interactions_count: int
    total_words: int
    can_advance: bool
    unmet_requirements: List[str]


class SubmissionResponse(BaseModel):
    """Response after submitting a solution"""
    success: bool
    submission_id: int  # Position in submissions list
    stage: LearningStageEnum
    explanation_accepted: bool
    verification_required: bool
    feedback: Optional[str] = None
    can_advance: bool
    unmet_requirements: List[str]


class VerificationResponse(BaseModel):
    """Response after verification"""
    success: bool
    passed: bool
    feedback: str
    can_advance: bool


class HintResponse(BaseModel):
    """Response when requesting a hint"""
    success: bool
    hint_number: int
    total_hints: int
    hint: str
    xp_penalty: int
    hints_remaining: int


class CompletionResponse(BaseModel):
    """Response when completing a session"""
    success: bool
    message: str
    summary: Optional[Dict[str, Any]] = None


class StageRequirementsResponse(BaseModel):
    """Requirements for a stage"""
    stage: LearningStageEnum
    min_interactions: int
    min_time_seconds: int
    requires_submission: bool
    requires_explanation: bool
    requires_verification: bool
    min_word_count: int


class SessionListResponse(BaseModel):
    """List of learning sessions"""
    sessions: List[LearningSessionResponse]
    total: int


# =============================================================================
# ERROR RESPONSES
# =============================================================================

class StageLockedError(BaseModel):
    """Error when trying to access a locked stage"""
    error: str = "stage_locked"
    message: str
    current_stage: LearningStageEnum
    requested_stage: LearningStageEnum
    requirements_to_unlock: List[str]


class CannotAdvanceError(BaseModel):
    """Error when trying to advance without meeting requirements"""
    error: str = "cannot_advance"
    message: str
    current_stage: LearningStageEnum
    unmet_requirements: List[str]
