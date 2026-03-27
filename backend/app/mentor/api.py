"""
VidyaGuru Mentor API Endpoints
RESTful API for the AI mentor system
"""
import asyncio
from typing import Optional, List
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.database import get_db
from app.dependencies import get_current_user, get_redis
from app.mentor.engine import (
    MentorEngine,
    LLMProvider as EngineLLMProvider,
    MentorPersonality as EnginePersonality,
    LearnerContext as EngineContext
)
from app.mentor.session_manager import SessionManager, PhaseStateMachine
from app.mentor.schemas import (
    # Request schemas
    SessionCreateRequest,
    MessageRequest,
    PhaseTransitionRequest,
    SessionEndRequest,
    TaskSubmission,
    CommunicationSubmission,
    HintRequest,
    # Response schemas
    SessionResponse,
    SessionListResponse,
    SessionSummary,
    SessionEndResponse,
    SessionAnalyticsResponse,
    UserProgressResponse,
    MentorMessageResponse,
    TaskFeedbackResponse,
    CommunicationFeedbackResponse,
    HintResponse,
    IndustryChallengeResponse,
    CommunicationExercise,
    WisdomQuote,
    CheatingAnalysisResponse,
    # Enums
    LearningPhase,
    MentorPersonality,
    LLMProvider
)
from app.mentor.prompts import LearningPhase as PromptPhase, get_wisdom_quote

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mentor", tags=["AI Mentor"])


# =============================================================================
# DEPENDENCIES
# =============================================================================

async def get_mentor_engine(
    provider: LLMProvider = LLMProvider.GEMINI
) -> MentorEngine:
    """Get configured mentor engine"""
    return MentorEngine(provider=EngineLLMProvider.GEMINI)


async def get_session_manager(
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis)
) -> SessionManager:
    """Get session manager instance"""
    return SessionManager(db=db, redis=redis)


# =============================================================================
# SESSION MANAGEMENT ENDPOINTS
# =============================================================================

@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new learning session"
)
async def create_session(
    request: SessionCreateRequest,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Create a new learning session or resume an existing one.
    
    The learning flow follows 8 phases:
    1. Topic Introduction
    2. Concept Explanation
    3. Real-World Examples
    4. Ancient Knowledge Connection
    5. Practical Task
    6. Communication Exercise
    7. Industry Challenge
    8. Reflection
    """
    user_id = str(current_user["id"])
    
    # Build learner context if provided
    learner_context = None
    if request.learner_context:
        learner_context = EngineContext(
            name=current_user.get("name", "Learner"),
            experience_level=request.learner_context.experience_level,
            learning_style=request.learner_context.learning_style,
            interests=request.learner_context.interests,
            current_streak=current_user.get("current_streak", 0),
            total_xp=current_user.get("total_xp", 0),
            strengths=request.learner_context.strengths,
            areas_to_improve=request.learner_context.areas_to_improve,
            preferred_language=request.learner_context.preferred_language
        )
    
    # Map personality
    personality = EnginePersonality(request.personality.value)
    
    # Get or create session
    if request.resume_existing:
        session, is_resumed = await session_manager.resume_or_create_session(
            user_id=user_id,
            topic=request.topic,
            personality=personality,
            learner_context=learner_context
        )
    else:
        session = await session_manager.create_session(
            user_id=user_id,
            topic=request.topic,
            concept=request.concept,
            personality=personality,
            learner_context=learner_context
        )
        is_resumed = False
    
    # Generate initial response for new sessions
    mentor_response = None
    if not is_resumed:
        engine = await get_mentor_engine(request.llm_provider)
        response = await engine.generate_response(
            session=session,
            user_message=f"I want to learn about {request.topic}"
        )
        session = await session_manager.update_session(
            session,
            f"I want to learn about {request.topic}",
            response
        )
        mentor_response = MentorMessageResponse(
            content=response.content,
            phase=LearningPhase(response.phase.value),
            suggestions=response.suggestions,
            xp_awarded=response.xp_awarded,
            phase_complete=response.phase_complete,
            next_phase=LearningPhase(response.next_phase.value) if response.next_phase else None,
            requires_verification=response.requires_verification,
            wisdom_quote=WisdomQuote(**response.wisdom_quote) if response.wisdom_quote else None,
            session_progress=PhaseStateMachine.get_progress_percentage(session)
        )
    
    return SessionResponse(
        session_id=session.session_id,
        topic=session.topic,
        current_phase=LearningPhase(session.current_phase.value),
        phases_completed=list(session.phase_progress.keys()),
        xp_earned=session.xp_earned,
        message_count=len(session.messages),
        started_at=session.started_at,
        last_activity=session.last_activity,
        is_resumed=is_resumed,
        progress_percentage=PhaseStateMachine.get_progress_percentage(session),
        mentor_response=mentor_response
    )


@router.get(
    "/sessions",
    response_model=SessionListResponse,
    summary="Get user's learning sessions"
)
async def list_sessions(
    limit: int = Query(default=10, ge=1, le=50),
    include_active: bool = Query(default=True),
    include_completed: bool = Query(default=True),
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get list of user's learning sessions"""
    user_id = str(current_user["id"])
    
    sessions = await session_manager.get_user_sessions(
        user_id=user_id,
        limit=limit,
        include_active=include_active,
        include_completed=include_completed
    )
    
    return SessionListResponse(
        sessions=[SessionSummary(**s) for s in sessions],
        total=len(sessions)
    )


@router.get(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    summary="Get a specific session"
)
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get details of a specific learning session"""
    user_id = str(current_user["id"])
    
    session = await session_manager.get_session(session_id, user_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return SessionResponse(
        session_id=session.session_id,
        topic=session.topic,
        current_phase=LearningPhase(session.current_phase.value),
        phases_completed=list(session.phase_progress.keys()),
        xp_earned=session.xp_earned,
        message_count=len(session.messages),
        started_at=session.started_at,
        last_activity=session.last_activity,
        is_resumed=True,
        progress_percentage=PhaseStateMachine.get_progress_percentage(session)
    )


@router.delete(
    "/sessions/{session_id}",
    response_model=SessionEndResponse,
    summary="End a learning session"
)
async def end_session(
    session_id: str,
    request: SessionEndRequest = None,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """End a learning session and get summary"""
    user_id = str(current_user["id"])
    
    try:
        result = await session_manager.end_session(
            session_id=session_id,
            user_id=user_id,
            summary=request.summary if request else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    return SessionEndResponse(
        session_id=result["session_id"],
        topic=result["topic"],
        duration_minutes=result["duration_minutes"],
        phases_completed=result["phases_completed"],
        xp_earned=result["xp_earned"],
        message_count=result["message_count"],
        summary=result["summary"],
        achievements_unlocked=[]  # TODO: Check for unlocked achievements
    )


# =============================================================================
# CONVERSATION ENDPOINTS
# =============================================================================

@router.post(
    "/sessions/{session_id}/messages",
    response_model=MentorMessageResponse,
    summary="Send a message to the mentor"
)
async def send_message(
    session_id: str,
    request: MessageRequest,
    provider: LLMProvider = Query(default=LLMProvider.GEMINI),
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Send a message to the AI mentor and receive a response.
    
    The mentor will:
    - Explain concepts using the Socratic method
    - Ask questions to verify understanding
    - Provide guidance without giving direct answers
    - Detect and address potential cheating
    """
    user_id = str(current_user["id"])
    
    session = await session_manager.get_session(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    engine = await get_mentor_engine(provider)
    
    # Handle special requests
    message = request.message
    if request.request_hint:
        message = f"[HINT REQUEST] {message}"
    
    # Generate response
    response = await engine.generate_response(
        session=session,
        user_message=message
    )
    
    # Update session
    session = await session_manager.update_session(session, message, response)
    
    # Handle phase transition if needed
    if request.skip_phase and response.next_phase:
        transition_response = await engine.transition_phase(session, response.next_phase)
        session = await session_manager.update_session(
            session,
            "[PHASE TRANSITION]",
            transition_response
        )
        response = transition_response
    
    return MentorMessageResponse(
        content=response.content,
        phase=LearningPhase(response.phase.value),
        suggestions=response.suggestions,
        xp_awarded=response.xp_awarded,
        phase_complete=response.phase_complete,
        next_phase=LearningPhase(response.next_phase.value) if response.next_phase else None,
        requires_verification=response.requires_verification,
        wisdom_quote=WisdomQuote(**response.wisdom_quote) if response.wisdom_quote else None,
        session_progress=PhaseStateMachine.get_progress_percentage(session)
    )


@router.post(
    "/sessions/{session_id}/messages/stream",
    summary="Stream a message response"
)
async def stream_message(
    session_id: str,
    request: MessageRequest,
    provider: LLMProvider = Query(default=LLMProvider.GEMINI),
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Stream the mentor's response in real-time"""
    user_id = str(current_user["id"])
    
    session = await session_manager.get_session(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    engine = await get_mentor_engine(provider)
    
    async def generate():
        async for chunk in engine.generate_response_stream(
            session=session,
            user_message=request.message
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


# =============================================================================
# PHASE MANAGEMENT ENDPOINTS
# =============================================================================

@router.post(
    "/sessions/{session_id}/transition",
    response_model=MentorMessageResponse,
    summary="Transition to a new learning phase"
)
async def transition_phase(
    session_id: str,
    request: PhaseTransitionRequest,
    provider: LLMProvider = Query(default=LLMProvider.GEMINI),
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Manually transition to a new learning phase"""
    user_id = str(current_user["id"])
    
    session = await session_manager.get_session(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Convert phase enum
    target_phase = PromptPhase(request.target_phase.value)
    
    # Validate transition
    if not request.force:
        can_transition, reason = PhaseStateMachine.can_transition(
            from_phase=session.current_phase,
            to_phase=target_phase,
            session=session
        )
        if not can_transition:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=reason
            )
    
    engine = await get_mentor_engine(provider)
    response = await engine.transition_phase(session, target_phase)
    
    # Update session
    session.current_phase = target_phase
    session = await session_manager.update_session(
        session,
        f"[TRANSITION TO {request.target_phase.value}]",
        response
    )
    
    return MentorMessageResponse(
        content=response.content,
        phase=LearningPhase(response.phase.value),
        suggestions=response.suggestions,
        xp_awarded=response.xp_awarded,
        phase_complete=False,
        next_phase=None,
        wisdom_quote=WisdomQuote(**response.wisdom_quote) if response.wisdom_quote else None,
        session_progress=PhaseStateMachine.get_progress_percentage(session)
    )


# =============================================================================
# TASK AND CHALLENGE ENDPOINTS
# =============================================================================

@router.post(
    "/sessions/{session_id}/submit-task",
    response_model=TaskFeedbackResponse,
    summary="Submit a practical task solution"
)
async def submit_task(
    session_id: str,
    submission: TaskSubmission,
    provider: LLMProvider = Query(default=LLMProvider.GEMINI),
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Submit a solution for the current practical task"""
    user_id = str(current_user["id"])
    
    session = await session_manager.get_session(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Verify we're in task phase
    if session.current_phase not in [
        PromptPhase.PRACTICAL_TASK,
        PromptPhase.INDUSTRY_CHALLENGE
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not in a task phase"
        )
    
    engine = await get_mentor_engine(provider)
    
    # Format submission message
    submission_message = f"""
## Task Submission

**Code ({submission.language}):**
```{submission.language}
{submission.code}
```

**Explanation:**
{submission.explanation}
"""
    if submission.alternative_approaches:
        submission_message += f"\n**Alternative approaches considered:**\n"
        for alt in submission.alternative_approaches:
            submission_message += f"- {alt}\n"
    
    response = await engine.generate_response(session, submission_message)
    
    # Update session
    session = await session_manager.update_session(session, submission_message, response)
    
    # Determine if correct based on response
    is_correct = not response.requires_verification and response.phase_complete
    
    return TaskFeedbackResponse(
        is_correct=is_correct,
        feedback=response.content,
        suggestions=response.suggestions,
        xp_awarded=response.xp_awarded,
        follow_up_questions=[] if is_correct else ["Can you explain your approach?"],
        code_review=None  # TODO: Add code review
    )


@router.get(
    "/sessions/{session_id}/challenge",
    response_model=IndustryChallengeResponse,
    summary="Get current industry challenge"
)
async def get_industry_challenge(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get the current industry challenge for the session"""
    user_id = str(current_user["id"])
    
    session = await session_manager.get_session(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Generate a challenge based on topic
    # In production, this would fetch from a challenge database
    return IndustryChallengeResponse(
        challenge_id=f"challenge_{session.session_id[:8]}",
        title=f"Build a {session.topic} Solution for TechCorp",
        company_context=f"TechCorp is a mid-size startup needing to implement {session.topic} in their platform.",
        requirements=[
            f"Implement core {session.topic} functionality",
            "Handle edge cases gracefully",
            "Write clean, maintainable code"
        ],
        constraints=[
            "Response time < 100ms",
            "Memory usage < 50MB",
            "Must work with existing systems"
        ],
        deliverables=[
            "Working implementation",
            "Explanation of approach",
            "Trade-off analysis"
        ],
        difficulty="intermediate",
        estimated_time_minutes=30,
        xp_reward=75
    )


# =============================================================================
# COMMUNICATION EXERCISE ENDPOINTS
# =============================================================================

@router.get(
    "/sessions/{session_id}/communication-exercise",
    response_model=CommunicationExercise,
    summary="Get a communication exercise"
)
async def get_communication_exercise(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get a communication exercise for the current topic"""
    user_id = str(current_user["id"])
    
    session = await session_manager.get_session(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return CommunicationExercise(
        exercise_id=f"comm_{session.session_id[:8]}",
        type="explain_to_audience",
        scenario=f"Your non-technical manager asks you to explain {session.topic}. They need to present it to stakeholders tomorrow.",
        audience="Non-technical manager",
        constraints={
            "time_limit": "2 minutes",
            "jargon_allowed": False,
            "visual_aids": "Optional"
        },
        evaluation_criteria=[
            "Clarity - Is it understandable?",
            "Accuracy - Is it technically correct?",
            "Engagement - Is it interesting?",
            "Appropriateness - Right level for audience?"
        ]
    )


@router.post(
    "/sessions/{session_id}/submit-communication",
    response_model=CommunicationFeedbackResponse,
    summary="Submit a communication exercise"
)
async def submit_communication(
    session_id: str,
    submission: CommunicationSubmission,
    provider: LLMProvider = Query(default=LLMProvider.GEMINI),
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Submit a communication exercise response"""
    user_id = str(current_user["id"])
    
    session = await session_manager.get_session(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    engine = await get_mentor_engine(provider)
    
    message = f"""
## Communication Exercise Submission

{submission.response}
"""
    
    response = await engine.generate_response(session, message)
    session = await session_manager.update_session(session, message, response)
    
    # Parse scores from response (simplified)
    # In production, use structured output
    return CommunicationFeedbackResponse(
        clarity_score=7,
        accuracy_score=8,
        engagement_score=6,
        audience_appropriateness_score=7,
        overall_score=7,
        strengths=["Good structure", "Clear language"],
        improvements=["Could use more analogies", "Add concrete examples"],
        feedback=response.content,
        xp_awarded=response.xp_awarded
    )


# =============================================================================
# HINT ENDPOINTS
# =============================================================================

@router.post(
    "/sessions/{session_id}/hint",
    response_model=HintResponse,
    summary="Request a hint"
)
async def request_hint(
    session_id: str,
    request: HintRequest,
    provider: LLMProvider = Query(default=LLMProvider.GEMINI),
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Request a hint for the current task"""
    user_id = str(current_user["id"])
    
    session = await session_manager.get_session(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Track hints used
    hints_used = session.metadata.get("hints_used", 0)
    max_hints = 3
    
    if hints_used >= max_hints:
        return HintResponse(
            hint_number=max_hints,
            total_hints=max_hints,
            hint="You've used all available hints. Try working through it yourself!",
            xp_penalty=0,
            next_hint_available=False
        )
    
    engine = await get_mentor_engine(provider)
    
    hint_message = f"[HINT REQUEST {request.hint_level}] {request.context or 'I need a hint'}"
    response = await engine.generate_response(session, hint_message)
    
    # Update hints used
    session.metadata["hints_used"] = hints_used + 1
    session = await session_manager.update_session(session, hint_message, response)
    
    return HintResponse(
        hint_number=hints_used + 1,
        total_hints=max_hints,
        hint=response.content,
        xp_penalty=5 * request.hint_level,
        next_hint_available=hints_used + 1 < max_hints
    )


# =============================================================================
# ANALYTICS ENDPOINTS
# =============================================================================

@router.get(
    "/sessions/{session_id}/analytics",
    response_model=SessionAnalyticsResponse,
    summary="Get session analytics"
)
async def get_session_analytics(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get detailed analytics for a session"""
    user_id = str(current_user["id"])
    
    try:
        analytics = await session_manager.get_session_analytics(session_id, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    return SessionAnalyticsResponse(**analytics)


@router.get(
    "/progress",
    response_model=UserProgressResponse,
    summary="Get user's learning progress"
)
async def get_user_progress(
    days: int = Query(default=30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get aggregated learning progress for the user"""
    user_id = str(current_user["id"])
    
    progress = await session_manager.get_user_learning_progress(user_id, days)
    
    return UserProgressResponse(
        user_id=progress["user_id"],
        period_days=progress["period_days"],
        total_sessions=progress["total_sessions"],
        total_xp_earned=progress["total_xp_earned"],
        total_learning_minutes=progress["total_learning_minutes"],
        topics_covered=progress["topics_covered"],
        phases_distribution=progress["phases_distribution"],
        recent_sessions=[SessionSummary(**s) for s in progress["sessions"]]
    )


# =============================================================================
# WISDOM QUOTES ENDPOINT
# =============================================================================

@router.get(
    "/wisdom",
    response_model=WisdomQuote,
    summary="Get a wisdom quote"
)
async def get_wisdom(
    context: Optional[str] = Query(default=None, description="Context for quote selection")
):
    """Get a random wisdom quote"""
    quote = get_wisdom_quote(context or "general")
    return WisdomQuote(
        text=quote["text"],
        transliteration=quote.get("transliteration"),
        translation=quote["translation"],
        source=quote["source"]
    )
