"""
Learning Database Models
"""
import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, Integer, DateTime, Date, ForeignKey, Enum, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class PathStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ModuleStatus(str, enum.Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ContentType(str, enum.Enum):
    THEORY = "theory"
    PRACTICE = "practice"
    PROJECT = "project"
    QUIZ = "quiz"
    VIDEO = "video"
    INTERACTIVE = "interactive"


class Difficulty(str, enum.Enum):
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class LearningPath(Base):
    """Learning path/curriculum model"""
    __tablename__ = "learning_paths"
    
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
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Progress
    status: Mapped[PathStatus] = mapped_column(Enum(PathStatus), default=PathStatus.ACTIVE)
    progress_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    
    # XP tracking
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    earned_xp: Mapped[int] = mapped_column(Integer, default=0)
    
    # Duration
    estimated_duration_hours: Mapped[int] = mapped_column(Integer, nullable=True)
    target_completion_date: Mapped[date] = mapped_column(Date, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="learning_paths")
    modules: Mapped[list["Module"]] = relationship(
        "Module", 
        back_populates="learning_path",
        cascade="all, delete-orphan",
        order_by="Module.order_index"
    )

    def __repr__(self):
        return f"<LearningPath {self.title}>"


class Module(Base):
    """Learning module within a path"""
    __tablename__ = "modules"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    path_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("learning_paths.id", ondelete="CASCADE"),
        index=True
    )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Module type and difficulty
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType), default=ContentType.THEORY)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), default=Difficulty.MEDIUM)
    
    # Ordering and progress
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ModuleStatus] = mapped_column(Enum(ModuleStatus), default=ModuleStatus.LOCKED)
    
    # Rewards and duration
    xp_reward: Mapped[int] = mapped_column(Integer, default=10)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30)
    
    # Prerequisites
    prerequisites: Mapped[list] = mapped_column(JSON, default=list)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    learning_path: Mapped["LearningPath"] = relationship("LearningPath", back_populates="modules")
    contents: Mapped[list["ModuleContent"]] = relationship(
        "ModuleContent", 
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="ModuleContent.order_index"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", 
        back_populates="module",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Module {self.title}>"


class ModuleContent(Base):
    """Content blocks within a module"""
    __tablename__ = "module_contents"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("modules.id", ondelete="CASCADE"),
        index=True
    )
    
    # Content
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    content_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Ordering
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationship
    module: Mapped["Module"] = relationship("Module", back_populates="contents")

    def __repr__(self):
        return f"<ModuleContent {self.content_type}>"


class Enrollment(Base):
    """Track user enrollments in learning paths"""
    __tablename__ = "enrollments"
    
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
    path_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_paths.id", ondelete="CASCADE"),
        index=True
    )
    
    # Enrollment status
    status: Mapped[str] = mapped_column(String(50), default="enrolled")  # enrolled, in-progress, completed, dropped
    progress_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    
    # Performance
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    modules_completed: Mapped[int] = mapped_column(Integer, default=0)
    average_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0)
    
    # Ratings and feedback
    rating: Mapped[float] = mapped_column(Numeric(2, 1), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Timestamps
    enrolled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_active_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="enrollments")
    learning_path: Mapped["LearningPath"] = relationship("LearningPath")
    
    def __repr__(self):
        return f"<Enrollment {self.user_id} -> {self.path_id}>"


# Import to avoid circular imports
from app.models.user import User
from app.models.task import Task
