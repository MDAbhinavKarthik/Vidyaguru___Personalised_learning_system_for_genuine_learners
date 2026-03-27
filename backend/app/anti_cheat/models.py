"""
VidyaGuru Anti-Cheating System - Database Models
=================================================

Models for tracking submissions and detecting suspicious behavior.
"""

import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4, UUID

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    ForeignKey, DateTime, Enum, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class SuspicionLevel(str, enum.Enum):
    """Level of suspicion for detected behavior"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SuspicionType(str, enum.Enum):
    """Types of suspicious behavior"""
    LARGE_PASTE = "large_paste"
    RAPID_SUBMISSION = "rapid_submission"
    IDENTICAL_ANSWER = "identical_answer"
    COPY_PASTE_PATTERN = "copy_paste_pattern"
    INCONSISTENT_SKILL = "inconsistent_skill"
    EXTERNAL_SOURCE_MATCH = "external_source_match"
    TIME_ANOMALY = "time_anomaly"
    TYPING_PATTERN_ANOMALY = "typing_pattern_anomaly"


class VerificationType(str, enum.Enum):
    """Types of verification challenges"""
    FOLLOW_UP_QUESTION = "follow_up_question"
    CODE_MODIFICATION = "code_modification"
    EXPLAIN_IN_OWN_WORDS = "explain_in_own_words"
    CONCEPT_QUESTION = "concept_question"
    DEBUG_CHALLENGE = "debug_challenge"


class VerificationStatus(str, enum.Enum):
    """Status of verification challenge"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    EXPIRED = "expired"
    SKIPPED = "skipped"


class SubmissionAnalysis(Base):
    """
    Records analysis of each task submission.
    Tracks typing patterns, timing, and similarity scores.
    """
    __tablename__ = "submission_analyses"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    
    # Link to task assignment
    task_assignment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("task_assignments.id", ondelete="CASCADE"),
        nullable=False
    )
    
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Submission metrics
    submission_text: Mapped[str] = mapped_column(Text, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Typing pattern analysis
    typing_events_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_typing_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # chars per minute
    paste_events: Mapped[int] = mapped_column(Integer, default=0)
    largest_paste_size: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing analysis
    time_to_submit_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    expected_time_range_min: Mapped[int] = mapped_column(Integer, nullable=True)
    expected_time_range_max: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Similarity analysis
    similarity_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 of normalized content
    similarity_scores: Mapped[dict] = mapped_column(JSON, default=dict)  # Scores against known sources
    highest_similarity_score: Mapped[float] = mapped_column(Float, default=0.0)
    similar_submission_ids: Mapped[list] = mapped_column(JSON, default=list)
    
    # Suspicion indicators
    suspicion_level: Mapped[SuspicionLevel] = mapped_column(
        Enum(SuspicionLevel),
        default=SuspicionLevel.NONE
    )
    suspicion_types: Mapped[list] = mapped_column(JSON, default=list)
    suspicion_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 to 1.0
    suspicion_details: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Flags
    requires_verification: Mapped[bool] = mapped_column(Boolean, default=False)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed_by_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    task_assignment = relationship("TaskAssignment", back_populates="submission_analysis")
    verifications = relationship("VerificationChallenge", back_populates="submission_analysis")
    
    __table_args__ = (
        Index("idx_submission_analysis_user", "user_id"),
        Index("idx_submission_analysis_suspicion", "suspicion_level", "is_flagged"),
        Index("idx_submission_analysis_hash", "similarity_hash"),
    )


class VerificationChallenge(Base):
    """
    Verification challenges issued when cheating is suspected.
    Stores follow-up questions, code modification tasks, etc.
    """
    __tablename__ = "verification_challenges"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    
    # Links
    submission_analysis_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("submission_analyses.id", ondelete="CASCADE"),
        nullable=False
    )
    
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Challenge details
    verification_type: Mapped[VerificationType] = mapped_column(
        Enum(VerificationType),
        nullable=False
    )
    
    challenge_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    challenge_context: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # For code modification challenges
    original_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_modification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    modification_hints: Mapped[list] = mapped_column(JSON, default=list)
    
    # Expected answer patterns (for validation)
    expected_keywords: Mapped[list] = mapped_column(JSON, default=list)
    min_response_length: Mapped[int] = mapped_column(Integer, default=50)
    
    # Response
    user_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_analysis: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Evaluation
    status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus),
        default=VerificationStatus.PENDING
    )
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.0 to 1.0
    passed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # AI evaluation
    ai_evaluation: Mapped[dict] = mapped_column(JSON, default=dict)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Feedback
    feedback_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Attempt tracking
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    max_attempts: Mapped[int] = mapped_column(Integer, default=2)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    submission_analysis = relationship("SubmissionAnalysis", back_populates="verifications")
    
    __table_args__ = (
        Index("idx_verification_user", "user_id"),
        Index("idx_verification_status", "status"),
        Index("idx_verification_expires", "expires_at"),
    )


class UserIntegrityProfile(Base):
    """
    Tracks user's overall integrity metrics and history.
    Used to determine trust level and response to suspicious behavior.
    """
    __tablename__ = "user_integrity_profiles"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    
    # Trust metrics
    trust_score: Mapped[float] = mapped_column(Float, default=1.0)  # 0.0 to 1.0
    integrity_level: Mapped[str] = mapped_column(String(20), default="trusted")  # trusted, monitored, restricted
    
    # Statistics
    total_submissions: Mapped[int] = mapped_column(Integer, default=0)
    flagged_submissions: Mapped[int] = mapped_column(Integer, default=0)
    verifications_issued: Mapped[int] = mapped_column(Integer, default=0)
    verifications_passed: Mapped[int] = mapped_column(Integer, default=0)
    verifications_failed: Mapped[int] = mapped_column(Integer, default=0)
    
    # Typing patterns (baseline established over time)
    avg_typing_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    typing_speed_std_dev: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    typical_submission_time_factor: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Warning history
    warnings_issued: Mapped[int] = mapped_column(Integer, default=0)
    last_warning_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Restrictions
    requires_verification_always: Mapped[bool] = mapped_column(Boolean, default=False)
    is_restricted: Mapped[bool] = mapped_column(Boolean, default=False)
    restriction_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    restricted_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    __table_args__ = (
        Index("idx_integrity_trust", "trust_score"),
        Index("idx_integrity_level", "integrity_level"),
    )


class SuspiciousActivityLog(Base):
    """
    Log of all detected suspicious activities.
    Used for analysis and pattern detection.
    """
    __tablename__ = "suspicious_activity_logs"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    submission_analysis_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("submission_analyses.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Activity details
    suspicion_type: Mapped[SuspicionType] = mapped_column(
        Enum(SuspicionType),
        nullable=False
    )
    severity: Mapped[SuspicionLevel] = mapped_column(
        Enum(SuspicionLevel),
        nullable=False
    )
    
    # Evidence
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Context
    task_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    task_difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Resolution
    action_taken: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamp
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    __table_args__ = (
        Index("idx_suspicious_activity_user", "user_id"),
        Index("idx_suspicious_activity_type", "suspicion_type"),
        Index("idx_suspicious_activity_severity", "severity"),
        Index("idx_suspicious_activity_date", "detected_at"),
    )


class SubmissionFingerprint(Base):
    """
    Stores fingerprints of submissions for similarity detection.
    Uses multiple hashing techniques for robust matching.
    """
    __tablename__ = "submission_fingerprints"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    
    submission_analysis_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("submission_analyses.id", ondelete="CASCADE"),
        nullable=False
    )
    
    task_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Multiple fingerprint types
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 of normalized content
    structure_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # Hash of code structure
    simhash: Mapped[str] = mapped_column(String(64), nullable=False)  # Simhash for similarity detection
    
    # N-gram fingerprints for partial matching
    ngram_hashes: Mapped[list] = mapped_column(JSON, default=list)
    
    # Metadata
    language: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # For code submissions
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    __table_args__ = (
        Index("idx_fingerprint_content", "content_hash"),
        Index("idx_fingerprint_structure", "structure_hash"),
        Index("idx_fingerprint_simhash", "simhash"),
        Index("idx_fingerprint_task", "task_id"),
    )
