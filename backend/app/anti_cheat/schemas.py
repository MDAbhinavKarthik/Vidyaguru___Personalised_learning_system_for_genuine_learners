"""
VidyaGuru Anti-Cheating System - Pydantic Schemas
==================================================

Request/Response schemas for integrity verification.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Enums
# ============================================================================

class SuspicionLevelEnum(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SuspicionTypeEnum(str, Enum):
    LARGE_PASTE = "large_paste"
    RAPID_SUBMISSION = "rapid_submission"
    IDENTICAL_ANSWER = "identical_answer"
    COPY_PASTE_PATTERN = "copy_paste_pattern"
    INCONSISTENT_SKILL = "inconsistent_skill"
    EXTERNAL_SOURCE_MATCH = "external_source_match"
    TIME_ANOMALY = "time_anomaly"
    TYPING_PATTERN_ANOMALY = "typing_pattern_anomaly"


class VerificationTypeEnum(str, Enum):
    FOLLOW_UP_QUESTION = "follow_up_question"
    CODE_MODIFICATION = "code_modification"
    EXPLAIN_IN_OWN_WORDS = "explain_in_own_words"
    CONCEPT_QUESTION = "concept_question"
    DEBUG_CHALLENGE = "debug_challenge"


class VerificationStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    EXPIRED = "expired"
    SKIPPED = "skipped"


class IntegrityLevelEnum(str, Enum):
    TRUSTED = "trusted"
    MONITORED = "monitored"
    RESTRICTED = "restricted"


# ============================================================================
# Typing Pattern Tracking (sent from frontend)
# ============================================================================

class TypingEvent(BaseModel):
    """Single typing event from frontend"""
    event_type: str = Field(..., description="Type: keystroke, paste, delete, cut")
    timestamp: int = Field(..., description="Unix timestamp in milliseconds")
    char_count: int = Field(default=1, description="Number of characters affected")
    content_length: int = Field(..., description="Total content length after event")


class SubmissionMetrics(BaseModel):
    """Metrics collected during task completion"""
    typing_events: List[TypingEvent] = Field(default_factory=list)
    total_keystrokes: int = Field(default=0)
    paste_events: int = Field(default=0)
    largest_paste_size: int = Field(default=0)
    start_time: datetime = Field(...)
    end_time: datetime = Field(...)
    focus_time_seconds: int = Field(default=0, description="Time with window in focus")
    tab_switches: int = Field(default=0)
    
    @field_validator('typing_events', mode='before')
    @classmethod
    def validate_events(cls, v):
        if v is None:
            return []
        return v


class SubmissionWithMetrics(BaseModel):
    """Submission content with typing metrics for analysis"""
    content: str = Field(..., min_length=1)
    task_assignment_id: UUID
    metrics: SubmissionMetrics
    
    @field_validator('content')
    @classmethod
    def normalize_content(cls, v):
        return v.strip()


# ============================================================================
# Submission Analysis
# ============================================================================

class SuspicionIndicator(BaseModel):
    """Individual suspicion indicator with evidence"""
    type: SuspicionTypeEnum
    severity: SuspicionLevelEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    description: str


class SubmissionAnalysisResult(BaseModel):
    """Result of analyzing a submission"""
    submission_analysis_id: UUID
    task_assignment_id: UUID
    
    # Overall assessment
    suspicion_level: SuspicionLevelEnum
    suspicion_score: float = Field(..., ge=0.0, le=1.0)
    requires_verification: bool
    
    # Individual indicators
    indicators: List[SuspicionIndicator] = Field(default_factory=list)
    
    # Recommendations
    recommended_verification_type: Optional[VerificationTypeEnum] = None
    
    # Summary
    summary: str
    

class SubmissionAnalysisResponse(BaseModel):
    """Full response after submission analysis"""
    analysis: SubmissionAnalysisResult
    verification_challenge: Optional["VerificationChallengeResponse"] = None
    user_message: Optional[str] = None  # Polite reminder if needed
    
    class Config:
        from_attributes = True


# ============================================================================
# Verification Challenges
# ============================================================================

class FollowUpQuestionChallenge(BaseModel):
    """Follow-up question to verify understanding"""
    question: str
    context: str = Field(..., description="Relevant context from submission")
    expected_concepts: List[str] = Field(default_factory=list)


class CodeModificationChallenge(BaseModel):
    """Challenge to modify code in a specific way"""
    original_code: str
    modification_request: str
    hints: List[str] = Field(default_factory=list)
    expected_changes: List[str] = Field(default_factory=list, description="What should change")


class ExplainInOwnWordsChallenge(BaseModel):
    """Challenge to explain concept without copying"""
    concept: str
    context: str
    forbidden_phrases: List[str] = Field(default_factory=list, description="Phrases that indicate copying")
    expected_keywords: List[str] = Field(default_factory=list)


class VerificationChallengeCreate(BaseModel):
    """Request to create a verification challenge"""
    submission_analysis_id: UUID
    verification_type: VerificationTypeEnum
    custom_prompt: Optional[str] = None


class VerificationChallengeResponse(BaseModel):
    """Verification challenge sent to user"""
    id: UUID
    verification_type: VerificationTypeEnum
    prompt: str
    context: Optional[Dict[str, Any]] = None
    
    # For code modification
    original_code: Optional[str] = None
    
    # Constraints
    min_response_length: int = 50
    expires_at: datetime
    attempt_number: int
    max_attempts: int
    
    # Encouragement
    encouragement_message: str = Field(
        default="Take your time to think through your response. "
        "We believe in your ability to demonstrate your understanding! 🌟"
    )
    
    class Config:
        from_attributes = True


class VerificationSubmitRequest(BaseModel):
    """User's response to verification challenge"""
    challenge_id: UUID
    response: str = Field(..., min_length=10)
    typing_metrics: Optional[SubmissionMetrics] = None
    
    @field_validator('response')
    @classmethod
    def validate_response(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Response must be at least 10 characters")
        return v.strip()


class VerificationResultResponse(BaseModel):
    """Result of verification challenge evaluation"""
    challenge_id: UUID
    status: VerificationStatusEnum
    passed: bool
    score: float = Field(..., ge=0.0, le=1.0)
    
    # Feedback
    feedback: str
    areas_for_improvement: List[str] = Field(default_factory=list)
    
    # Next steps
    can_retry: bool
    remaining_attempts: int
    next_challenge: Optional[VerificationChallengeResponse] = None
    
    # Encouragement (always positive and supportive)
    message: str
    
    class Config:
        from_attributes = True


# ============================================================================
# User Integrity Profile
# ============================================================================

class IntegrityProfileResponse(BaseModel):
    """User's integrity profile summary"""
    user_id: UUID
    trust_score: float = Field(..., ge=0.0, le=1.0)
    integrity_level: IntegrityLevelEnum
    
    # Statistics
    total_submissions: int
    flagged_submissions: int
    verification_pass_rate: float = Field(..., ge=0.0, le=1.0)
    
    # Status
    is_restricted: bool
    restriction_reason: Optional[str] = None
    restricted_until: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class IntegrityStatsResponse(BaseModel):
    """Detailed integrity statistics for user"""
    profile: IntegrityProfileResponse
    
    # Verification history
    recent_verifications: List["VerificationHistoryItem"] = Field(default_factory=list)
    
    # Patterns (shown to user for transparency)
    avg_submission_time: Optional[float] = None
    typical_response_length: Optional[int] = None
    
    # Positive reinforcement
    streak_days_without_flags: int = 0
    improvements_noted: List[str] = Field(default_factory=list)


class VerificationHistoryItem(BaseModel):
    """Single item in verification history"""
    id: UUID
    verification_type: VerificationTypeEnum
    status: VerificationStatusEnum
    passed: Optional[bool]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Suspicious Activity
# ============================================================================

class SuspiciousActivityResponse(BaseModel):
    """Single suspicious activity record"""
    id: UUID
    suspicion_type: SuspicionTypeEnum
    severity: SuspicionLevelEnum
    description: str
    detected_at: datetime
    resolved: bool
    
    class Config:
        from_attributes = True


class ActivityAlertResponse(BaseModel):
    """Alert shown to user about detected activity"""
    alert_type: str
    severity: SuspicionLevelEnum
    
    # Always polite and educational
    title: str
    message: str
    
    # What user should do
    suggested_action: Optional[str] = None
    
    # Link to verification if needed
    verification_required: bool = False
    verification_id: Optional[UUID] = None


# ============================================================================
# Polite Reminder Messages
# ============================================================================

class GenuineLearnerReminder(BaseModel):
    """
    Polite reminder about genuine learning.
    These messages are designed to be supportive, not accusatory.
    """
    title: str = "A Gentle Reminder 🌱"
    message: str
    encouragement: str
    tips: List[str] = Field(default_factory=list)
    support_offered: str = Field(
        default="If you're struggling with this topic, we're here to help! "
        "Try breaking down the problem into smaller parts, or revisit the fundamentals."
    )


# Pre-defined reminder messages
REMINDER_MESSAGES = {
    "large_paste": GenuineLearnerReminder(
        title="Taking Shortcuts? 🤔",
        message=(
            "We noticed your response was entered very quickly. "
            "VidyaGuru is designed to help you truly understand concepts, "
            "not just find answers."
        ),
        encouragement=(
            "Real learning takes time, and every moment you spend thinking "
            "through a problem strengthens your understanding. "
            "The journey matters as much as the destination!"
        ),
        tips=[
            "Try solving problems step by step",
            "Use the hint system if you're stuck",
            "Write out your thought process",
            "It's okay to take longer - quality over speed!"
        ]
    ),
    "identical_answer": GenuineLearnerReminder(
        title="Let's Try Something Different 📝",
        message=(
            "Your answer looks very similar to existing solutions. "
            "While it's great to learn from examples, VidyaGuru helps you "
            "develop your own problem-solving skills."
        ),
        encouragement=(
            "The best way to learn is by tackling problems in your own way. "
            "Even if your solution isn't perfect, the thought process you develop "
            "is invaluable for your growth as a learner!"
        ),
        tips=[
            "Try explaining the solution in your own words",
            "Add comments explaining WHY each step works",
            "Think about alternative approaches",
            "Ask yourself: Could I solve a similar problem without help?"
        ]
    ),
    "verification_request": GenuineLearnerReminder(
        title="Quick Check-In 🎯",
        message=(
            "To help us understand your learning progress better, "
            "we'd like to ask a quick follow-up question. "
            "This helps ensure you're getting the most out of your learning experience."
        ),
        encouragement=(
            "Think of this as a friendly conversation about what you've learned. "
            "There's no pressure - we just want to support your learning journey!"
        ),
        tips=[
            "Take your time to think through your response",
            "Use your own words to explain your understanding",
            "It's okay if you're not 100% sure - that's how we identify areas to strengthen!"
        ]
    ),
    "failed_verification": GenuineLearnerReminder(
        title="Let's Learn Together 🌟",
        message=(
            "It seems like this topic might need a bit more practice. "
            "That's completely normal - learning is a journey, not a race!"
        ),
        encouragement=(
            "Every expert was once a beginner. The fact that you're here, "
            "putting in effort to learn, already puts you ahead. "
            "Let's work together to strengthen your understanding!"
        ),
        tips=[
            "Review the fundamental concepts again",
            "Try the practice exercises with hints enabled",
            "Break complex problems into smaller parts",
            "Reach out to your AI mentor for personalized guidance"
        ],
        support_offered=(
            "We're here to help you succeed! Consider revisiting this topic "
            "through our guided learning path, or chat with your AI mentor "
            "for personalized explanations."
        )
    ),
    "general_integrity": GenuineLearnerReminder(
        title="About Genuine Learning 📚",
        message=(
            "VidyaGuru is built for learners who want to truly understand, "
            "not just complete tasks. Our learning approach is designed to "
            "build real, lasting knowledge."
        ),
        encouragement=(
            "विद्या ददाति विनयम् - Knowledge gives humility. "
            "The skills you develop through genuine effort will serve you "
            "throughout your life and career!"
        ),
        tips=[
            "Focus on understanding WHY, not just WHAT",
            "Embrace mistakes as learning opportunities",
            "Take time to reflect on what you've learned",
            "Build connections between different concepts"
        ]
    )
}


# ============================================================================
# Admin/Analytics Schemas
# ============================================================================

class IntegrityAnalyticsSummary(BaseModel):
    """Platform-wide integrity analytics"""
    period_start: datetime
    period_end: datetime
    
    # Submission stats
    total_submissions: int
    flagged_submissions: int
    flag_rate: float
    
    # Verification stats
    verifications_issued: int
    verifications_passed: int
    verifications_failed: int
    pass_rate: float
    
    # Top issues
    top_suspicion_types: List[Dict[str, Any]]
    
    # User stats
    users_with_flags: int
    users_restricted: int


class FlaggedSubmissionResponse(BaseModel):
    """Admin view of flagged submission"""
    id: UUID
    user_id: UUID
    task_assignment_id: UUID
    
    suspicion_level: SuspicionLevelEnum
    suspicion_types: List[str]
    suspicion_score: float
    suspicion_details: Dict[str, Any]
    
    reviewed: bool
    admin_notes: Optional[str]
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# Forward references
SubmissionAnalysisResponse.model_rebuild()
IntegrityStatsResponse.model_rebuild()
