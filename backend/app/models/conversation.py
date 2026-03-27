"""
AI Mentor Conversation Database Models
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationContext(str, enum.Enum):
    GENERAL = "general"
    MODULE_LEARNING = "module_learning"
    TASK_HELP = "task_help"
    CODE_REVIEW = "code_review"
    CONCEPT_EXPLANATION = "concept_explanation"
    QUIZ = "quiz"
    INTERVIEW_PREP = "interview_prep"


class Conversation(Base):
    """AI Mentor conversation session"""
    __tablename__ = "conversations"
    
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
    
    # Conversation details
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    context_type: Mapped[ConversationContext] = mapped_column(
        Enum(ConversationContext), 
        default=ConversationContext.GENERAL
    )
    
    # Related entities
    related_module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        nullable=True
    )
    related_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        nullable=True
    )
    
    # Token tracking
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    
    # Summary for context
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Settings for this conversation
    temperature: Mapped[float] = mapped_column(default=0.7)
    model_used: Mapped[str] = mapped_column(String(50), default="gpt-4o")
    
    # Status
    is_archived: Mapped[bool] = mapped_column(default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_message_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __repr__(self):
        return f"<Conversation {self.id} - {self.context_type}>"


class Message(Base):
    """Individual message in a conversation"""
    __tablename__ = "messages"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True
    )
    
    # Message content
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Token usage
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Metadata
    message_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # For code blocks or special content
    attachments: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Feedback
    user_rating: Mapped[int] = mapped_column(Integer, nullable=True)  # 1-5
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.role}: {self.content[:50]}...>"


# Import to avoid circular imports
from app.models.user import User
