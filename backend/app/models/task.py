"""
Task Database Models
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Enum, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class TaskType(str, enum.Enum):
    LEARNING = "learning"
    PRACTICE = "practice"
    PROJECT = "project"
    DAILY = "daily"
    CHALLENGE = "challenge"
    QUIZ = "quiz"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    SKIPPED = "skipped"


class TaskDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FLAGGED = "flagged"
    REQUIRES_REVIEW = "requires_review"


class Task(Base):
    """Task/assignment model"""
    __tablename__ = "tasks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("modules.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Task details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Type and difficulty
    task_type: Mapped[TaskType] = mapped_column(Enum(TaskType), default=TaskType.PRACTICE)
    difficulty: Mapped[TaskDifficulty] = mapped_column(Enum(TaskDifficulty), default=TaskDifficulty.MEDIUM)
    
    # Status and progress
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING)
    
    # Deadline and attempts
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    current_attempts: Mapped[int] = mapped_column(Integer, default=0)
    
    # Rewards
    xp_reward: Mapped[int] = mapped_column(Integer, default=5)
    
    # Hints
    hints: Mapped[list] = mapped_column(JSON, default=list)
    hints_used: Mapped[int] = mapped_column(Integer, default=0)
    
    # Template/starter code
    template_code: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Test cases for code tasks
    test_cases: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    module: Mapped["Module"] = relationship("Module", back_populates="tasks")
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission", 
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="Submission.submitted_at.desc()"
    )

    def __repr__(self):
        return f"<Task {self.title}>"


class Submission(Base):
    """Task submission model"""
    __tablename__ = "submissions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("tasks.id", ondelete="CASCADE"),
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    # Submission content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=True)  # Programming language
    
    # Scoring
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    max_score: Mapped[float] = mapped_column(Numeric(5, 2), default=100)
    
    # Feedback
    feedback: Mapped[dict] = mapped_column(JSON, nullable=True)
    ai_feedback: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Time tracking
    time_spent_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Anti-cheat data
    typing_pattern_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    plagiarism_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus), 
        default=VerificationStatus.PENDING
    )
    
    # Attempt tracking
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    
    # Test results
    test_results: Mapped[dict] = mapped_column(JSON, nullable=True)
    tests_passed: Mapped[int] = mapped_column(Integer, nullable=True)
    tests_total: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Timestamps
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Relationship
    task: Mapped["Task"] = relationship("Task", back_populates="submissions")

    def __repr__(self):
        return f"<Submission task={self.task_id} attempt={self.attempt_number}>"


# Import to avoid circular imports
from app.models.user import User
from app.models.learning import Module
