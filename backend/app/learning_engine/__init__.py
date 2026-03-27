"""
VidyaGuru Learning Engine Module
================================

A comprehensive learning flow engine that controls educational content delivery
through 8 sequential stages with strict progression requirements.

The 8 Learning Stages:
1. Concept Introduction (10 XP) - Initial exposure to the topic
2. Detailed Explanation (25 XP) - Deep dive with verification
3. Real-World Application (15 XP) - Practical context and examples
4. Ancient Knowledge (10 XP) - Historical and cultural insights
5. Practical Task (50 XP) - Hands-on coding/implementation
6. Communication Task (30 XP) - Explain to validate understanding
7. Industry Challenge (75 XP) - Real-world problem solving
8. Reflection Summary (20 XP) - Consolidate and reflect

Key Features:
- Stage progression requires meeting specific interaction/time/submission requirements
- Anti-skip mechanism prevents rushing through content
- XP rewards encourage genuine engagement
- Verification questions ensure comprehension
- Admin override with 50% XP penalty for forced advancement

Usage:
    from app.learning_engine import (
        learning_engine,
        learning_service,
        LearningStage,
        router
    )
    
    # Create a session
    session = learning_engine.create_session(
        user_id="user123",
        topic="Machine Learning",
        concept="Neural Networks"
    )
    
    # Check if user can advance
    can_advance, unmet = learning_engine.can_advance_stage(session)
"""

from app.learning_engine.engine import (
    # Enums
    LearningStage,
    StageStatus,
    
    # Data classes
    StageRequirement,
    StageContent,
    StageProgress,
    
    # Models
    LearningSessionState,
    
    # Constants
    STAGE_REQUIREMENTS,
    STAGE_CONTENT,
    
    # Main classes
    LearningEngine,
    StageValidator,
    
    # Singleton
    learning_engine
)

from app.learning_engine.schemas import (
    # Enums
    LearningStageEnum,
    StageStatusEnum,
    
    # Request schemas
    CreateLearningSessionRequest,
    InteractionRequest,
    SubmissionRequest,
    AdvanceStageRequest,
    VerificationAnswerRequest,
    
    # Response schemas
    StageInfoResponse,
    StageProgressResponse,
    StageContentResponse,
    LearningSessionResponse,
    SessionListResponse,
    ProgressResponse,
    AdvanceStageResponse,
    InteractionResponse,
    SubmissionResponse,
    HintResponse,
    CompletionResponse,
    
    # Error schemas
    StageLockedError,
    CannotAdvanceError,
    SessionNotFoundError,
    ValidationError
)

from app.learning_engine.service import (
    LearningEngineService,
    learning_service
)

from app.learning_engine.api import router

__all__ = [
    # Enums
    "LearningStage",
    "StageStatus",
    "LearningStageEnum",
    "StageStatusEnum",
    
    # Data classes
    "StageRequirement",
    "StageContent",
    "StageProgress",
    
    # Models
    "LearningSessionState",
    
    # Constants
    "STAGE_REQUIREMENTS",
    "STAGE_CONTENT",
    
    # Classes
    "LearningEngine",
    "LearningEngineService",
    "StageValidator",
    
    # Singletons
    "learning_engine",
    "learning_service",
    
    # Request schemas
    "CreateLearningSessionRequest",
    "InteractionRequest",
    "SubmissionRequest",
    "AdvanceStageRequest",
    "VerificationAnswerRequest",
    
    # Response schemas
    "StageInfoResponse",
    "StageProgressResponse",
    "StageContentResponse",
    "LearningSessionResponse",
    "SessionListResponse",
    "ProgressResponse",
    "AdvanceStageResponse",
    "InteractionResponse",
    "SubmissionResponse",
    "HintResponse",
    "CompletionResponse",
    
    # Error schemas
    "StageLockedError",
    "CannotAdvanceError",
    "SessionNotFoundError",
    "ValidationError",
    
    # Router
    "router"
]
