"""
VidyaGuru Mentor API Schemas
Request/Response models for the mentor API
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class LearningPhase(str, Enum):
    TOPIC_INTRODUCTION = "topic_introduction"
    CONCEPT_EXPLANATION = "concept_explanation"
    REAL_WORLD_EXAMPLES = "real_world_examples"
    ANCIENT_KNOWLEDGE = "ancient_knowledge"
    PRACTICAL_TASK = "practical_task"
    COMMUNICATION_EXERCISE = "communication_exercise"
    INDUSTRY_CHALLENGE = "industry_challenge"
    REFLECTION = "reflection"


class MentorPersonality(str, Enum):
    SOCRATIC = "socratic"
    ENCOURAGING = "encouraging"
    CHALLENGING = "challenging"
    ANALYTICAL = "analytical"
    STORYTELLER = "storyteller"


class LLMProvider(str, Enum):
    GEMINI = "gemini"


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class LearnerContextCreate(BaseModel):
    """Learner context for personalization"""
    experience_level: str = Field(
        default="intermediate",
        description="beginner, intermediate, advanced, expert"
    )
    learning_style: str = Field(
        default="mixed",
        description="visual, auditory, reading_writing, kinesthetic, mixed"
    )
    interests: List[str] = Field(
        default_factory=lambda: ["technology"],
        description="List of learner interests"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Known strengths"
    )
    areas_to_improve: List[str] = Field(
        default_factory=list,
        description="Areas needing improvement"
    )
    preferred_language: str = Field(
        default="en",
        description="Preferred language code"
    )


class SessionCreateRequest(BaseModel):
    """Request to create a new learning session"""
    topic: str = Field(..., min_length=1, max_length=200, description="Topic to learn")
    concept: Optional[str] = Field(None, description="Specific concept within topic")
    personality: MentorPersonality = Field(
        default=MentorPersonality.SOCRATIC,
        description="Mentor personality style"
    )
    learner_context: Optional[LearnerContextCreate] = Field(
        None,
        description="Optional learner context for personalization"
    )
    resume_existing: bool = Field(
        default=True,
        description="Resume existing session if available"
    )
    llm_provider: LLMProvider = Field(
        default=LLMProvider.GEMINI,
        description="LLM provider to use"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Decorators",
                "concept": "Function decorators with arguments",
                "personality": "socratic",
                "learner_context": {
                    "experience_level": "intermediate",
                    "learning_style": "visual",
                    "interests": ["web development", "data science"]
                },
                "resume_existing": True
            }
        }


class MessageRequest(BaseModel):
    """Request to send a message to the mentor"""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    request_hint: bool = Field(default=False, description="Request a hint")
    skip_phase: bool = Field(default=False, description="Skip to next phase")
    stream: bool = Field(default=False, description="Stream the response")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "I think decorators are like wrappers that modify function behavior, right?",
                "request_hint": False,
                "stream": False
            }
        }


class PhaseTransitionRequest(BaseModel):
    """Request to manually transition to a phase"""
    target_phase: LearningPhase = Field(..., description="Phase to transition to")
    force: bool = Field(default=False, description="Force transition even if requirements not met")


class SessionEndRequest(BaseModel):
    """Request to end a session"""
    summary: Optional[str] = Field(None, description="Optional custom summary")


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class WisdomQuote(BaseModel):
    """A wisdom quote"""
    text: str
    transliteration: Optional[str] = None
    translation: str
    source: str


class MentorMessageResponse(BaseModel):
    """Response from the mentor"""
    content: str = Field(..., description="Mentor's response")
    phase: LearningPhase = Field(..., description="Current learning phase")
    suggestions: List[str] = Field(default_factory=list, description="Suggested responses")
    xp_awarded: int = Field(default=0, description="XP awarded for this interaction")
    phase_complete: bool = Field(default=False, description="Whether current phase is complete")
    next_phase: Optional[LearningPhase] = Field(None, description="Next phase if transitioning")
    requires_verification: bool = Field(default=False, description="Whether verification is needed")
    wisdom_quote: Optional[WisdomQuote] = Field(None, description="Optional wisdom quote")
    session_progress: int = Field(default=0, description="Overall session progress percentage")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Excellent question! Before I explain, tell me - what do you think happens when you put @ above a function?",
                "phase": "concept_explanation",
                "suggestions": [
                    "I think it modifies the function",
                    "It's like wrapping the function",
                    "I'm not sure, can you explain?"
                ],
                "xp_awarded": 10,
                "phase_complete": False,
                "session_progress": 25
            }
        }


class SessionResponse(BaseModel):
    """Response with session information"""
    session_id: str = Field(..., description="Unique session identifier")
    topic: str = Field(..., description="Learning topic")
    current_phase: LearningPhase = Field(..., description="Current learning phase")
    phases_completed: List[str] = Field(default_factory=list, description="Completed phases")
    xp_earned: int = Field(default=0, description="Total XP earned")
    message_count: int = Field(default=0, description="Total messages in session")
    started_at: datetime = Field(..., description="Session start time")
    last_activity: datetime = Field(..., description="Last activity time")
    is_resumed: bool = Field(default=False, description="Whether session was resumed")
    progress_percentage: int = Field(default=0, description="Overall progress")
    mentor_response: Optional[MentorMessageResponse] = Field(
        None,
        description="Initial mentor response (for new sessions)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "topic": "Python Decorators",
                "current_phase": "topic_introduction",
                "phases_completed": [],
                "xp_earned": 0,
                "message_count": 2,
                "started_at": "2024-01-15T10:30:00Z",
                "last_activity": "2024-01-15T10:30:00Z",
                "is_resumed": False,
                "progress_percentage": 12
            }
        }


class SessionSummary(BaseModel):
    """Summary of a session"""
    session_id: str
    topic: str
    current_phase: str
    phases_completed: List[str]
    xp_earned: int
    message_count: int
    duration_minutes: int
    started_at: str
    last_activity: str
    is_active: bool


class SessionListResponse(BaseModel):
    """Response with list of sessions"""
    sessions: List[SessionSummary]
    total: int


class SessionEndResponse(BaseModel):
    """Response when ending a session"""
    session_id: str
    topic: str
    duration_minutes: int
    phases_completed: int
    xp_earned: int
    message_count: int
    summary: str
    achievements_unlocked: List[str] = Field(default_factory=list)


class SessionAnalyticsResponse(BaseModel):
    """Detailed session analytics"""
    session_id: str
    topic: str
    current_phase: str
    phases_completed: List[str]
    stats: Dict[str, Any]
    message_analysis: Dict[str, Any]
    phase_timestamps: Dict[str, str]
    engagement_score: float


class UserProgressResponse(BaseModel):
    """User's learning progress"""
    user_id: str
    period_days: int
    total_sessions: int
    total_xp_earned: int
    total_learning_minutes: int
    topics_covered: List[str]
    phases_distribution: Dict[str, int]
    recent_sessions: List[SessionSummary]


# =============================================================================
# TASK AND CHALLENGE SCHEMAS
# =============================================================================

class TaskSubmission(BaseModel):
    """Submission for a practical task"""
    code: str = Field(..., description="Code solution")
    explanation: str = Field(..., min_length=50, description="Explanation of approach")
    language: str = Field(default="python", description="Programming language")
    alternative_approaches: Optional[List[str]] = Field(
        None,
        description="Alternative approaches considered"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "code": "def my_decorator(func):\n    def wrapper(*args):\n        print('Before')\n        result = func(*args)\n        print('After')\n        return result\n    return wrapper",
                "explanation": "I created a decorator that prints 'Before' and 'After' around the function execution. The wrapper function uses *args to accept any arguments.",
                "language": "python"
            }
        }


class TaskFeedbackResponse(BaseModel):
    """Feedback on a task submission"""
    is_correct: bool
    feedback: str
    suggestions: List[str]
    xp_awarded: int
    follow_up_questions: List[str]
    code_review: Optional[Dict[str, Any]] = None


class IndustryChallengeResponse(BaseModel):
    """An industry challenge"""
    challenge_id: str
    title: str
    company_context: str
    requirements: List[str]
    constraints: List[str]
    deliverables: List[str]
    difficulty: str
    estimated_time_minutes: int
    xp_reward: int


# =============================================================================
# COMMUNICATION EXERCISE SCHEMAS
# =============================================================================

class CommunicationExercise(BaseModel):
    """A communication exercise"""
    exercise_id: str
    type: str  # explain_to_audience, interview, teaching, debate
    scenario: str
    audience: str
    constraints: Dict[str, Any]
    evaluation_criteria: List[str]


class CommunicationSubmission(BaseModel):
    """Submission for communication exercise"""
    response: str = Field(..., min_length=100, description="Communication response")
    format: str = Field(default="text", description="Format: text, bullet_points, structured")


class CommunicationFeedbackResponse(BaseModel):
    """Feedback on communication exercise"""
    clarity_score: int = Field(..., ge=1, le=10)
    accuracy_score: int = Field(..., ge=1, le=10)
    engagement_score: int = Field(..., ge=1, le=10)
    audience_appropriateness_score: int = Field(..., ge=1, le=10)
    overall_score: int = Field(..., ge=1, le=10)
    strengths: List[str]
    improvements: List[str]
    feedback: str
    xp_awarded: int


# =============================================================================
# HINT AND HELP SCHEMAS
# =============================================================================

class HintRequest(BaseModel):
    """Request for a hint"""
    context: Optional[str] = Field(None, description="Additional context for the hint")
    hint_level: int = Field(default=1, ge=1, le=3, description="Hint level 1-3")


class HintResponse(BaseModel):
    """A hint from the mentor"""
    hint_number: int
    total_hints: int
    hint: str
    xp_penalty: int = Field(default=5, description="XP penalty for using hint")
    next_hint_available: bool


# =============================================================================
# CHEATING DETECTION SCHEMAS
# =============================================================================

class CheatingAnalysisResponse(BaseModel):
    """Results of cheating analysis"""
    suspicion_level: float = Field(..., ge=0, le=1)
    indicators: List[str]
    recommended_action: str
    verification_questions: List[str]
