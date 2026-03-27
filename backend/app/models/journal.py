"""
Journal Database Models
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class EntryType(str, enum.Enum):
    IDEA = "idea"
    NOTE = "note"
    CONNECTION = "connection"
    QUESTION = "question"
    ACHIEVEMENT = "achievement"
    BUG_LOG = "bug_log"
    GOAL = "goal"
    REFLECTION = "reflection"


class Mood(str, enum.Enum):
    EXCITED = "excited"
    HAPPY = "happy"
    NEUTRAL = "neutral"
    CONFUSED = "confused"
    FRUSTRATED = "frustrated"
    DETERMINED = "determined"


class JournalEntry(Base):
    """Idea/Learning journal entry model"""
    __tablename__ = "journal_entries"
    
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
    
    # Entry content
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Type and mood
    entry_type: Mapped[EntryType] = mapped_column(Enum(EntryType), default=EntryType.NOTE)
    mood: Mapped[Mood] = mapped_column(Enum(Mood), nullable=True)
    
    # Rich content (code snippets, attachments)
    rich_content: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # AI-generated insights
    ai_insights: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Related entries (for connections)
    linked_entry_ids: Mapped[list] = mapped_column(JSON, default=list)
    
    # Related learning context
    related_module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        nullable=True
    )
    related_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="journal_entries")
    entry_tags: Mapped[list["EntryTag"]] = relationship(
        "EntryTag",
        back_populates="entry",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<JournalEntry {self.entry_type}: {self.title}>"


class Tag(Base):
    """Tag for categorizing journal entries"""
    __tablename__ = "tags"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")  # Hex color
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship
    entry_tags: Mapped[list["EntryTag"]] = relationship(
        "EntryTag",
        back_populates="tag",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Tag {self.name}>"


class EntryTag(Base):
    """Many-to-many relationship between entries and tags"""
    __tablename__ = "entry_tags"
    
    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("journal_entries.id", ondelete="CASCADE"),
        primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    # Relationships
    entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="entry_tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="entry_tags")


# Import to avoid circular imports
from app.models.user import User
