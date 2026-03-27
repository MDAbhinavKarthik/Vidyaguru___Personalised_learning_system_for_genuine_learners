"""
VidyaGuru AI Mentor Package
A comprehensive AI-powered learning mentor system

"विद्या ददाति विनयम्" - Knowledge gives humility
"""

from app.mentor.prompts import (
    LearningPhase,
    MentorPersonality,
    LearnerContext,
    build_system_prompt,
    build_phase_prompt,
    get_wisdom_quote,
    get_motivation_message,
    WISDOM_QUOTES,
    PHASE_PROMPTS,
    ANTI_CHEATING_PROMPTS,
)

from app.mentor.engine import (
    MentorEngine,
    LLMProvider,
    MessageRole,
    Message,
    LearningSession,
    MentorResponse,
    CheatingIndicator,
)

from app.mentor.session_manager import (
    SessionManager,
    PhaseStateMachine,
)

from app.mentor.cheating_detection import (
    CheatingDetector,
    CheatingAnalysis,
    SuspicionLevel,
    VerificationStrategy,
    cheating_detector,
)

from app.mentor.api import router as mentor_router

__all__ = [
    # Prompts
    "LearningPhase",
    "MentorPersonality", 
    "LearnerContext",
    "build_system_prompt",
    "build_phase_prompt",
    "get_wisdom_quote",
    "get_motivation_message",
    "WISDOM_QUOTES",
    "PHASE_PROMPTS",
    "ANTI_CHEATING_PROMPTS",
    
    # Engine
    "MentorEngine",
    "LLMProvider",
    "MessageRole",
    "Message",
    "LearningSession",
    "MentorResponse",
    "CheatingIndicator",
    
    # Session Management
    "SessionManager",
    "PhaseStateMachine",
    
    # Cheating Detection
    "CheatingDetector",
    "CheatingAnalysis",
    "SuspicionLevel",
    "VerificationStrategy",
    "cheating_detector",
    
    # API
    "mentor_router",
]

__version__ = "1.0.0"
