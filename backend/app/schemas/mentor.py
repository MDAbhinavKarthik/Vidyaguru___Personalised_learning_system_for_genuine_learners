"""
AI Mentor Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, AsyncGenerator
from datetime import datetime
from uuid import UUID
from enum import Enum


class MessageRoleEnum(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationContextEnum(str, Enum):
    GENERAL = "general"
    MODULE_LEARNING = "module_learning"
    TASK_HELP = "task_help"
    CODE_REVIEW = "code_review"
    CONCEPT_EXPLANATION = "concept_explanation"
    QUIZ = "quiz"
    INTERVIEW_PREP = "interview_prep"


# Chat Message Schemas
class ChatMessageBase(BaseModel):
    """Base chat message schema"""
    content: str = Field(..., min_length=1)


class ChatMessageCreate(ChatMessageBase):
    """Create chat message schema"""
    conversation_id: Optional[UUID] = None
    context_type: Optional[ConversationContextEnum] = ConversationContextEnum.GENERAL
    related_module_id: Optional[UUID] = None
    related_task_id: Optional[UUID] = None
    attachments: Optional[dict] = None  # For code snippets, images


class ChatMessageResponse(ChatMessageBase):
    """Chat message response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    conversation_id: UUID
    role: MessageRoleEnum
    tokens_used: Optional[int] = None
    metadata: Optional[dict] = None
    attachments: Optional[dict] = None
    user_rating: Optional[int] = None
    created_at: datetime


# Conversation Schemas
class ConversationBase(BaseModel):
    """Base conversation schema"""
    title: Optional[str] = None
    context_type: ConversationContextEnum = ConversationContextEnum.GENERAL


class ConversationCreate(ConversationBase):
    """Create conversation schema"""
    related_module_id: Optional[UUID] = None
    related_task_id: Optional[UUID] = None


class ConversationUpdate(BaseModel):
    """Update conversation schema"""
    title: Optional[str] = None
    is_archived: Optional[bool] = None


class ConversationResponse(ConversationBase):
    """Conversation response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    related_module_id: Optional[UUID] = None
    related_task_id: Optional[UUID] = None
    total_tokens_used: int
    summary: Optional[str] = None
    model_used: str
    is_archived: bool
    created_at: datetime
    last_message_at: datetime


class ConversationDetailResponse(ConversationResponse):
    """Conversation detail with messages"""
    messages: list[ChatMessageResponse] = []


class ConversationListResponse(BaseModel):
    """Paginated conversations response"""
    items: list[ConversationResponse]
    total: int
    page: int
    size: int


# Chat Request/Response
class ChatRequest(BaseModel):
    """Chat request to AI mentor"""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[UUID] = None
    context_type: ConversationContextEnum = ConversationContextEnum.GENERAL
    related_module_id: Optional[UUID] = None
    related_task_id: Optional[UUID] = None
    include_wisdom: bool = True  # Include ancient wisdom quotes
    code_context: Optional[str] = None  # For code-related queries


class ChatResponse(BaseModel):
    """Chat response from AI mentor"""
    conversation_id: UUID
    message: ChatMessageResponse
    suggestions: list[str] = []
    related_resources: list[dict] = []
    wisdom_quote: Optional[dict] = None
    follow_up_questions: list[str] = []


class StreamChatRequest(ChatRequest):
    """Streaming chat request"""
    pass


# Specialized Mentor Features
class ConceptExplanationRequest(BaseModel):
    """Request concept explanation"""
    concept: str = Field(..., min_length=1)
    current_understanding: Optional[str] = None
    preferred_style: Optional[str] = None  # visual, analogy, step-by-step
    difficulty_level: Optional[str] = "beginner"


class ConceptExplanationResponse(BaseModel):
    """Concept explanation response"""
    concept: str
    explanation: str
    examples: list[str]
    analogies: list[str]
    related_concepts: list[str]
    quiz_questions: list[dict]
    wisdom_connection: Optional[str] = None


class CodeReviewRequest(BaseModel):
    """Code review request"""
    code: str = Field(..., min_length=1)
    language: str
    context: Optional[str] = None
    focus_areas: Optional[list[str]] = None  # performance, readability, security


class CodeReviewResponse(BaseModel):
    """Code review response"""
    overall_rating: float
    summary: str
    issues: list[dict]
    suggestions: list[dict]
    improved_code: Optional[str] = None
    learning_points: list[str]


class QuizGenerateRequest(BaseModel):
    """Generate quiz request"""
    topic: str
    difficulty: str = "medium"
    num_questions: int = Field(5, ge=1, le=20)
    question_types: list[str] = ["multiple_choice", "true_false", "short_answer"]


class QuizQuestion(BaseModel):
    """Quiz question"""
    id: UUID
    question: str
    question_type: str
    options: Optional[list[str]] = None
    correct_answer: Optional[str] = None  # Hidden until answered
    explanation: Optional[str] = None
    difficulty: str
    topic: str


class QuizResponse(BaseModel):
    """Quiz response"""
    quiz_id: UUID
    topic: str
    questions: list[QuizQuestion]
    time_limit_minutes: Optional[int] = None


class QuizSubmitRequest(BaseModel):
    """Submit quiz answers"""
    quiz_id: UUID
    answers: dict  # question_id -> answer


class QuizResultResponse(BaseModel):
    """Quiz result response"""
    quiz_id: UUID
    score: float
    total_questions: int
    correct_answers: int
    time_taken_seconds: int
    detailed_results: list[dict]
    recommendations: list[str]
    xp_earned: int


class MentorSuggestion(BaseModel):
    """Mentor suggestion for next steps"""
    suggestion_type: str
    title: str
    description: str
    action_url: Optional[str] = None
    priority: int


class VoiceChatRequest(BaseModel):
    """Voice chat request"""
    audio_base64: str
    conversation_id: Optional[UUID] = None


class VoiceChatResponse(BaseModel):
    """Voice chat response"""
    conversation_id: UUID
    transcript: str
    response_text: str
    response_audio_url: Optional[str] = None
    message: ChatMessageResponse


class MessageRatingRequest(BaseModel):
    """Rate a message"""
    message_id: UUID
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None
