"""
VidyaGuru Task Management & Skill Tracking - Database Models
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum
import uuid

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, 
    ForeignKey, Enum, JSON, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base



# =============================================================================
# ENUMS
# =============================================================================

class TaskType(str, PyEnum):
    """Types of learning tasks"""
    CODING_EXERCISE = "coding_exercise"
    CONCEPT_EXPLANATION = "concept_explanation"
    COMMUNICATION_TASK = "communication_task"
    RESEARCH_TASK = "research_task"
    INDUSTRY_PROBLEM = "industry_problem"


class TaskStatus(str, PyEnum):
    """Task completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskDifficulty(str, PyEnum):
    """Task difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillCategory(str, PyEnum):
    """Categories of skills to track"""
    CONCEPT_UNDERSTANDING = "concept_understanding"
    PRACTICAL_SKILLS = "practical_skills"
    COMMUNICATION_ABILITY = "communication_ability"
    PROBLEM_SOLVING = "problem_solving"


class SkillLevel(str, PyEnum):
    """Skill proficiency levels"""
    NOVICE = "novice"           # 0-20
    BEGINNER = "beginner"       # 21-40
    INTERMEDIATE = "intermediate"  # 41-60
    ADVANCED = "advanced"       # 61-80
    EXPERT = "expert"           # 81-100


# =============================================================================
# TASK MODELS
# =============================================================================

class SkillTask(Base):
    """
    Skill-based task definition - templates for learning activities.
    Named SkillTask to avoid conflict with app.models.task.Task
    """
    __tablename__ = "skill_tasks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Basic info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Classification
    task_type: Mapped[TaskType] = mapped_column(
        Enum(TaskType), 
        nullable=False,
        index=True
    )
    difficulty: Mapped[TaskDifficulty] = mapped_column(
        Enum(TaskDifficulty),
        default=TaskDifficulty.INTERMEDIATE
    )
    
    # Topic/concept association
    topic: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    concept: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=[])
    
    # Requirements
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30)
    prerequisites: Mapped[Optional[List[str]]] = mapped_column(JSON, default=[])
    
    # Skill impact - which skills this task develops and by how much
    skill_weights: Mapped[dict] = mapped_column(
        JSON,
        default={
            "concept_understanding": 0.0,
            "practical_skills": 0.0,
            "communication_ability": 0.0,
            "problem_solving": 0.0
        }
    )
    
    # XP and rewards
    base_xp: Mapped[int] = mapped_column(Integer, default=10)
    bonus_xp_conditions: Mapped[Optional[dict]] = mapped_column(JSON, default={})
    
    # Task-specific content
    content: Mapped[dict] = mapped_column(JSON, default={})
    # For coding: starter_code, test_cases, expected_output
    # For explanation: key_points, required_depth
    # For communication: audience, format, tone
    # For research: sources_required, citation_format
    # For industry: constraints, real_world_context
    
    # Evaluation criteria
    evaluation_rubric: Mapped[dict] = mapped_column(JSON, default={})
    passing_score: Mapped[float] = mapped_column(Float, default=70.0)
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    assignments = relationship("TaskAssignment", back_populates="skill_task")
    
    __table_args__ = (
        Index("ix_skill_tasks_topic_type", "topic", "task_type"),
        Index("ix_skill_tasks_difficulty_type", "difficulty", "task_type"),
    )


class TaskAssignment(Base):
    """
    User's assignment/attempt at a task
    """
    __tablename__ = "task_assignments"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # References
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    skill_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skill_tasks.id"),
        nullable=False,
        index=True
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )  # Links to learning session
    
    # Status tracking
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        default=TaskStatus.NOT_STARTED,
        index=True
    )
    
    # Progress
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    
    # Submission
    submission: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Contains: code, explanation, response, etc. based on task type
    
    # Evaluation
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    feedback: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Contains: strengths, improvements, detailed_scores, ai_feedback
    
    # Skill gains from this assignment
    skill_gains: Mapped[dict] = mapped_column(
        JSON,
        default={
            "concept_understanding": 0.0,
            "practical_skills": 0.0,
            "communication_ability": 0.0,
            "problem_solving": 0.0
        }
    )
    
    # XP earned
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    bonus_xp: Mapped[int] = mapped_column(Integer, default=0)
    
    # Time tracking
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)
    
    # Hints used (penalty)
    hints_used: Mapped[int] = mapped_column(Integer, default=0)
    hints_content: Mapped[Optional[List[str]]] = mapped_column(JSON, default=[])
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    skill_task = relationship("SkillTask", back_populates="assignments")
    submission_analysis = relationship(
        "SubmissionAnalysis",
        back_populates="task_assignment",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
    Index("ix_task_assignments_user_status", "user_id", "status"),
    Index("ix_task_assignments_user_skill_task", "user_id", "skill_task_id"),
    CheckConstraint(
        "progress_percent >= 0 AND progress_percent <= 100",
        name="ck_task_assignments_progress_percent_range"
    ),
    CheckConstraint(
        "score IS NULL OR (score >= 0 AND score <= 100)",
        name="ck_task_assignments_score_range"
    ),
)


# =============================================================================
# SKILL TRACKING MODELS
# =============================================================================

class UserSkill(Base):
    """
    User's skill levels across different categories
    """
    __tablename__ = "user_skills"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # Skill category
    category: Mapped[SkillCategory] = mapped_column(
        Enum(SkillCategory),
        nullable=False
    )
    
    # Topic-specific or general
    topic: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )  # NULL means general/overall skill
    
    # Current level (0-100)
    level: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Experience points in this skill
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    
    # Statistics
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    average_score: Mapped[float] = mapped_column(Float, default=0.0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, default=0)
    
    # Level thresholds reached
    proficiency: Mapped[SkillLevel] = mapped_column(
        Enum(SkillLevel),
        default=SkillLevel.NOVICE
    )
    
    # Progress to next level
    xp_to_next_level: Mapped[int] = mapped_column(Integer, default=100)
    
    # Timestamps
    last_activity: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
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
    UniqueConstraint(
        "user_id",
        "category",
        "topic",
        name="uq_user_skill_category_topic"
    ),
    Index(
        "ix_user_skills_user_category",
        "user_id",
        "category"
    ),
    CheckConstraint(
        "level >= 0 AND level <= 100",
        name="ck_user_skills_level_range"
    ),
)


class SkillHistory(Base):
    """
    Historical record of skill changes
    """
    __tablename__ = "skill_history"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_skills.id"),
        nullable=False,
        index=True
    )
    
    # What caused the change
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # task_completion, daily_practice, milestone, decay, bonus
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )  # Task assignment ID, etc.
    
    # Change details
    previous_level: Mapped[float] = mapped_column(Float, nullable=False)
    new_level: Mapped[float] = mapped_column(Float, nullable=False)
    change_amount: Mapped[float] = mapped_column(Float, nullable=False)
    
    xp_gained: Mapped[int] = mapped_column(Integer, default=0)
    
    # Context
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    __table_args__ = (
        Index("ix_skill_history_user_date", "user_id", "created_at"),
    )


class SkillAssessment(Base):
    """
    Formal skill assessments/tests
    """
    __tablename__ = "skill_assessments"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # What's being assessed
    category: Mapped[SkillCategory] = mapped_column(
        Enum(SkillCategory),
        nullable=False
    )
    topic: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Assessment type
    assessment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # initial, periodic, challenge, certification
    
    # Questions and answers
    questions: Mapped[List[dict]] = mapped_column(JSON, default=[])
    responses: Mapped[Optional[List[dict]]] = mapped_column(JSON, nullable=True)
    
    # Results
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    passed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Skill level before and after
    level_before: Mapped[float] = mapped_column(Float, nullable=False)
    level_after: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Detailed breakdown
    breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    __table_args__ = (
        Index("ix_skill_assessments_user_category", "user_id", "category"),
    )


# =============================================================================
# ACHIEVEMENT & MILESTONE MODELS
# =============================================================================

class SkillMilestone(Base):
    """
    Milestones/achievements for skill progression
    """
    __tablename__ = "skill_milestones"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Milestone definition
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Requirements
    category: Mapped[Optional[SkillCategory]] = mapped_column(
        Enum(SkillCategory),
        nullable=True
    )  # NULL means any category
    required_level: Mapped[float] = mapped_column(Float, default=0.0)
    required_tasks: Mapped[int] = mapped_column(Integer, default=0)
    required_streak: Mapped[int] = mapped_column(Integer, default=0)
    custom_requirements: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Rewards
    xp_reward: Mapped[int] = mapped_column(Integer, default=0)
    badge_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class UserMilestone(Base):
    """
    User's achieved milestones
    """
    __tablename__ = "user_milestones"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    milestone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skill_milestones.id"),
        nullable=False
    )
    
    # When achieved
    achieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Context
    context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # What triggered this milestone
    
    __table_args__ = (
        UniqueConstraint("user_id", "milestone_id", name="uq_user_milestone"),
    )

print("TASK MODEL LOADED")