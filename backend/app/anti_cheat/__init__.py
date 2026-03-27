"""
VidyaGuru Anti-Cheating System
==============================

A comprehensive integrity verification system designed for genuine learners.

Philosophy:
    This system is built on the principle that learning happens through genuine
    effort and understanding. Rather than being punitive, it gently guides users
    towards authentic learning practices.

Detection Methods:
    - Large paste detection (sudden appearance of content)
    - Identical/similar answer matching
    - Typing pattern analysis
    - Submission timing anomalies
    - Skill consistency checking

Verification Methods:
    - Follow-up explanation questions
    - Code modification challenges
    - Explain-in-own-words prompts
    - Concept understanding questions

Usage:
    from app.anti_cheat import (
        SubmissionAnalyzer,
        VerificationService,
        IntegrityService,
        router
    )
    
    # Analyze a submission
    analyzer = SubmissionAnalyzer(db)
    result = await analyzer.analyze_submission(submission, task_id)
    
    # Create verification challenge
    verification_service = VerificationService(db)
    challenge = await verification_service.create_challenge(...)
"""

from app.anti_cheat.models import (
    # Enums
    SuspicionLevel,
    SuspicionType,
    VerificationType,
    VerificationStatus,
    
    # Models
    SubmissionAnalysis,
    VerificationChallenge,
    UserIntegrityProfile,
    SuspiciousActivityLog,
    SubmissionFingerprint
)

from app.anti_cheat.schemas import (
    # Enums
    SuspicionLevelEnum,
    SuspicionTypeEnum,
    VerificationTypeEnum,
    VerificationStatusEnum,
    IntegrityLevelEnum,
    
    # Input schemas
    TypingEvent,
    SubmissionMetrics,
    SubmissionWithMetrics,
    VerificationSubmitRequest,
    
    # Analysis schemas
    SuspicionIndicator,
    SubmissionAnalysisResult,
    SubmissionAnalysisResponse,
    
    # Verification schemas
    FollowUpQuestionChallenge,
    CodeModificationChallenge,
    ExplainInOwnWordsChallenge,
    VerificationChallengeResponse,
    VerificationResultResponse,
    
    # Profile schemas
    IntegrityProfileResponse,
    IntegrityStatsResponse,
    VerificationHistoryItem,
    
    # Activity schemas
    SuspiciousActivityResponse,
    ActivityAlertResponse,
    
    # Reminder messages
    GenuineLearnerReminder,
    REMINDER_MESSAGES,
    
    # Admin schemas
    IntegrityAnalyticsSummary,
    FlaggedSubmissionResponse
)

from app.anti_cheat.service import (
    # Configuration
    DetectionConfig,
    
    # Utility functions
    normalize_text,
    normalize_code,
    compute_hash,
    compute_simhash,
    compute_ngram_hashes,
    hamming_distance,
    calculate_similarity_from_hamming,
    
    # Detectors
    PasteDetector,
    TimingAnalyzer,
    TypingPatternAnalyzer,
    SimilarityDetector,
    SkillConsistencyChecker,
    
    # Services
    SubmissionAnalyzer,
    VerificationService,
    IntegrityService
)

from app.anti_cheat.api import router

__all__ = [
    # Model Enums
    "SuspicionLevel",
    "SuspicionType",
    "VerificationType",
    "VerificationStatus",
    
    # Schema Enums
    "SuspicionLevelEnum",
    "SuspicionTypeEnum",
    "VerificationTypeEnum",
    "VerificationStatusEnum",
    "IntegrityLevelEnum",
    
    # Models
    "SubmissionAnalysis",
    "VerificationChallenge",
    "UserIntegrityProfile",
    "SuspiciousActivityLog",
    "SubmissionFingerprint",
    
    # Input Schemas
    "TypingEvent",
    "SubmissionMetrics",
    "SubmissionWithMetrics",
    "VerificationSubmitRequest",
    
    # Analysis Schemas
    "SuspicionIndicator",
    "SubmissionAnalysisResult",
    "SubmissionAnalysisResponse",
    
    # Verification Schemas
    "FollowUpQuestionChallenge",
    "CodeModificationChallenge",
    "ExplainInOwnWordsChallenge",
    "VerificationChallengeResponse",
    "VerificationResultResponse",
    
    # Profile Schemas
    "IntegrityProfileResponse",
    "IntegrityStatsResponse",
    "VerificationHistoryItem",
    
    # Activity Schemas
    "SuspiciousActivityResponse",
    "ActivityAlertResponse",
    
    # Reminder Messages
    "GenuineLearnerReminder",
    "REMINDER_MESSAGES",
    
    # Admin Schemas
    "IntegrityAnalyticsSummary",
    "FlaggedSubmissionResponse",
    
    # Configuration
    "DetectionConfig",
    
    # Utility Functions
    "normalize_text",
    "normalize_code",
    "compute_hash",
    "compute_simhash",
    "compute_ngram_hashes",
    "hamming_distance",
    "calculate_similarity_from_hamming",
    
    # Detectors
    "PasteDetector",
    "TimingAnalyzer",
    "TypingPatternAnalyzer",
    "SimilarityDetector",
    "SkillConsistencyChecker",
    
    # Services
    "SubmissionAnalyzer",
    "VerificationService",
    "IntegrityService",
    
    # Router
    "router"
]
