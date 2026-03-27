"""
AI Mentor Endpoints
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.mentor_service import MentorService
from app.schemas.mentor import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    ConceptExplanationRequest,
    ConceptExplanationResponse,
    CodeReviewRequest,
    CodeReviewResponse,
    QuizGenerateRequest,
    QuizResponse,
    MentorSuggestion
)
from app.dependencies import get_current_active_user, PaginationParams
from app.models.user import User


router = APIRouter(prefix="/mentor", tags=["AI Mentor"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with AI mentor"
)
async def chat(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Send a message to the AI mentor.
    
    The AI uses the Socratic method to encourage genuine understanding.
    """
    service = MentorService(db)
    return await service.chat(current_user.id, data)


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    summary="Get conversations"
)
async def get_conversations(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all mentor conversations.
    """
    service = MentorService(db)
    return await service.get_conversations(current_user.id, pagination)


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    summary="Get conversation"
)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific conversation with all messages.
    """
    service = MentorService(db)
    return await service.get_conversation_detail(conversation_id, current_user.id)


@router.delete(
    "/conversations/{conversation_id}",
    response_model=dict,
    summary="Delete conversation"
)
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Archive a conversation.
    """
    service = MentorService(db)
    return await service.delete_conversation(conversation_id, current_user.id)


@router.post(
    "/explain",
    response_model=ConceptExplanationResponse,
    summary="Get concept explanation"
)
async def explain_concept(
    data: ConceptExplanationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a detailed explanation of a concept.
    """
    service = MentorService(db)
    return await service.explain_concept(current_user.id, data)


@router.post(
    "/review-code",
    response_model=CodeReviewResponse,
    summary="Review code"
)
async def review_code(
    data: CodeReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI review of code.
    """
    service = MentorService(db)
    return await service.review_code(current_user.id, data)


@router.post(
    "/generate-quiz",
    response_model=QuizResponse,
    summary="Generate quiz"
)
async def generate_quiz(
    data: QuizGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a quiz on a topic.
    """
    service = MentorService(db)
    return await service.generate_quiz(current_user.id, data)


@router.get(
    "/suggestions",
    response_model=list[MentorSuggestion],
    summary="Get suggestions"
)
async def get_suggestions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get personalized mentor suggestions.
    """
    service = MentorService(db)
    return await service.get_suggestions(current_user.id)


@router.post(
    "/messages/{message_id}/rate",
    response_model=dict,
    summary="Rate message"
)
async def rate_message(
    message_id: UUID,
    rating: int = Query(..., ge=1, le=5, description="Rating 1-5"),
    feedback: Optional[str] = Query(None, description="Optional feedback"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Rate a mentor message.
    """
    service = MentorService(db)
    return await service.rate_message(message_id, current_user.id, rating, feedback)
