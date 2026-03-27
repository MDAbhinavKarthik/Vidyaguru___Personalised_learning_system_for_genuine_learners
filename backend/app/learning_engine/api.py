"""
VidyaGuru Learning Engine API Endpoints
RESTful API for the learning flow system
"""
from typing import Optional, List
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.learning_engine.engine import (
    learning_engine,
    LearningEngine,
    LearningStage,
    StageStatus,
    STAGE_CONTENT,
    STAGE_REQUIREMENTS,
    StageValidator
)
from app.learning_engine.schemas import (
    # Request schemas
    CreateLearningSessionRequest,
    InteractionRequest,
    SubmissionRequest,
    AdvanceStageRequest,
    VerificationAnswerRequest,
    # Response schemas
    LearningSessionResponse,
    ProgressResponse,
    StageInfoResponse,
    StageContentResponse,
    AdvanceStageResponse,
    InteractionResponse,
    SubmissionResponse,
    VerificationResponse,
    HintResponse,
    CompletionResponse,
    StageRequirementsResponse,
    SessionListResponse,
    # Enums
    LearningStageEnum,
    StageStatusEnum,
    # Errors
    StageLockedError,
    CannotAdvanceError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/learning", tags=["Learning Engine"])


# =============================================================================
# DEPENDENCY
# =============================================================================

def get_engine() -> LearningEngine:
    """Get the learning engine instance"""
    return learning_engine


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

@router.post(
    "/sessions",
    response_model=LearningSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new learning session"
)
async def create_session(
    request: CreateLearningSessionRequest,
    current_user: dict = Depends(get_current_user),
    engine: LearningEngine = Depends(get_engine)
):
    """
    Create a new learning session with the 8-stage flow.
    
    The learning flow includes:
    1. Concept Introduction
    2. Explanation
    3. Real-World Application
    4. Ancient Knowledge Insight
    5. Practical Task
    6. Communication Task
    7. Industry Challenge
    8. Reflection Summary
    
    Users must complete each stage before advancing.
    """
    user_id = str(current_user["id"])
    
    session = engine.create_session(
        user_id=user_id,
        topic=request.topic,
        concept=request.concept,
        difficulty=request.difficulty,
        experience_level=request.experience_level,
        interests=request.interests
    )
    
    logger.info(f"Created learning session {session.session_id} for user {user_id}")
    
    return LearningSessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        topic=session.topic,
        concept=session.concept,
        difficulty=session.difficulty,
        current_stage=LearningStageEnum(session.current_stage.value),
        overall_progress_percent=0,
        total_xp=session.total_xp,
        max_xp=sum(c.xp_reward for c in STAGE_CONTENT.values()),
        is_complete=session.is_complete,
        is_paused=session.is_paused,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


@router.get(
    "/sessions",
    response_model=SessionListResponse,
    summary="List user's learning sessions"
)
async def list_sessions(
    limit: int = Query(default=10, ge=1, le=50),
    include_completed: bool = Query(default=True),
    current_user: dict = Depends(get_current_user),
    engine: LearningEngine = Depends(get_engine)
):
    """Get list of user's learning sessions"""
    user_id = str(current_user["id"])
    
    # Filter sessions for this user
    user_sessions = [
        s for s in engine.sessions.values()
        if s.user_id == user_id and (include_completed or not s.is_complete)
    ]
    
    # Sort by updated_at descending
    user_sessions.sort(key=lambda x: x.updated_at, reverse=True)
    user_sessions = user_sessions[:limit]
    
    sessions = [
        LearningSessionResponse(
            session_id=s.session_id,
            user_id=s.user_id,
            topic=s.topic,
            concept=s.concept,
            difficulty=s.difficulty,
            current_stage=LearningStageEnum(s.current_stage.value),
            overall_progress_percent=engine.get_session_progress(s)["overall_progress_percent"],
            total_xp=s.total_xp,
            max_xp=sum(c.xp_reward for c in STAGE_CONTENT.values()),
            is_complete=s.is_complete,
            is_paused=s.is_paused,
            created_at=s.created_at,
            updated_at=s.updated_at,
            completed_at=s.completed_at
        )
        for s in user_sessions
    ]
    
    return SessionListResponse(sessions=sessions, total=len(sessions))


@router.get(
    "/sessions/{session_id}",
    response_model=LearningSessionResponse,
    summary="Get a learning session"
)
async def get_session(
    session_id: str = Path(..., description="Session ID"),
    current_user: dict = Depends(get_current_user),
    engine: LearningEngine = Depends(get_engine)
):
    """Get details of a specific learning session"""
    session = engine.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )
    
    progress = engine.get_session_progress(session)
    
    return LearningSessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        topic=session.topic,
        concept=session.concept,
        difficulty=session.difficulty,
        current_stage=LearningStageEnum(session.current_stage.value),
        overall_progress_percent=progress["overall_progress_percent"],
        total_xp=session.total_xp,
        max_xp=progress["max_xp"],
        is_complete=session.is_complete,
        is_paused=session.is_paused,
        created_at=session.created_at,
        updated_at=session.updated_at,
        completed_at=session.completed_at
    )


# =============================================================================
# PROGRESS TRACKING
# =============================================================================

@router.get(
    "/sessions/{session_id}/progress",
    response_model=ProgressResponse,
    summary="Get detailed progress for a session"
)
async def get_progress(
    session_id: str = Path(..., description="Session ID"),
    current_user: dict = Depends(get_current_user),
    engine: LearningEngine = Depends(get_engine)
):
    """
    Get detailed progress information including all stages.
    Shows which stages are locked, available, in-progress, or completed.
    """
    session = engine.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    progress_data = engine.get_session_progress(session)
    
    stages = [
        StageInfoResponse(
            stage=LearningStageEnum(s["stage"]),
            title=s["title"],
            description=STAGE_CONTENT[LearningStage(s["stage"])].description,
            status=StageStatusEnum(s["status"]),
            is_current=s["is_current"],
            xp_reward=s["xp_reward"],
            xp_earned=s["xp_earned"],
            interactions=s["interactions"],
            min_interactions=s["min_interactions"],
            time_spent_seconds=s["time_spent_seconds"],
            min_time_seconds=s["min_time_seconds"],
            can_advance=s.get("can_advance"),
            unmet_requirements=s.get("unmet_requirements")
        )
        for s in progress_data["stages"]
    ]
    
    return ProgressResponse(
        session_id=progress_data["session_id"],
        topic=progress_data["topic"],
        current_stage=LearningStageEnum(progress_data["current_stage"]),
        overall_progress_percent=progress_data["overall_progress_percent"],
        total_xp=progress_data["total_xp"],
        max_xp=progress_data["max_xp"],
        stages=stages,
        is_complete=progress_data["is_complete"]
    )


@router.get(
    "/sessions/{session_id}/current-stage",
    response_model=StageContentResponse,
    summary="Get current stage content"
)
async def get_current_stage(
    session_id: str = Path(..., description="Session ID"),
    current_user: dict = Depends(get_current_user),
    engine: LearningEngine = Depends(get_engine)
):
    """Get content and instructions for the current stage"""
    session = engine.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    content = engine.get_current_stage_content(session)
    prompt = engine.get_stage_prompt(session)
    
    return StageContentResponse(
        stage=LearningStageEnum(session.current_stage.value),
        title=content.title,
        description=content.description,
        objectives=content.objectives,
        completion_criteria=content.completion_criteria,
        xp_reward=content.xp_reward,
        mentor_prompt=prompt
    )


@router.get(
    "/sessions/{session_id}/stages/{stage}/requirements",
    response_model=StageRequirementsResponse,
    summary="Get requirements for a stage"
)
async def get_stage_requirements(
    session_id: str = Path(..., description="Session ID"),
    stage: LearningStageEnum = Path(..., description="Stage to check"),
    current_user: dict = Depends(get_current_user),
    engine: LearningEngine = Depends(get_engine)
):
    """Get the requirements needed to complete a specific stage"""
    session = engine.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    requirements = STAGE_REQUIREMENTS[LearningStage(stage.value)]
    
    return StageRequirementsResponse(
        stage=stage,
        min_interactions=requirements.min_interactions,
        min_time_seconds=requirements.min_time_seconds,
        requires_submission=requirements.requires_submission,
        requires_explanation=requirements.requires_explanation,
        requires_verification=requirements.requires_verification,
        min_word_count=requirements.min_word_count
    )


# =============================================================================
# INTERACTION RECORDING
# =============================================================================

@router.post(
    "/sessions/{session_id}/interact",
    response_model=InteractionResponse,
    summary="Record an interaction"
)
async def record_interaction(
    session_id: str = Path(..., description="Session ID"),
    request: InteractionRequest = ...,
    current_user: dict = Depends(get_current_user),
    engine: LearningEngine = Depends(get_engine)
):
    """
    Record a user interaction (message) in the current stage.
    This tracks progress toward stage completion.
    """
    session = engine.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    if session.is_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is already complete"
        )
    
    # Record the interaction
    progress = engine.record_interaction(
        session,
        user_message=request.message,
        mentor_response=""  # Mentor response tracked separately
    )
    
    # Check if can advance
    can_advance, unmet = engine.can_advance_stage(session)
    
    return InteractionResponse(
        success=True,
        stage=LearningStageEnum(session.current_stage.value),
        interactions_count=progress.interactions,
        total_words=progress.total_words,
        can_advance=can_advance,
        unmet_requirements=unmet
    )


# =============================================================================
# SUBMISSIONS
# =============================================================================

@router.post(
    "/sessions/{session_id}/submit",
    response_model=SubmissionResponse,
    summary="Submit a task solution"
)
async def submit_solution(
    session_id: str = Path(..., description="Session ID"),
    request: SubmissionRequest = ...,
    current_user: dict = Depends(get_current_user),
    engine: LearningEngine = Depends(get_engine)
):
    """
    Submit a solution for task stages (Practical Task, Communication Task, Industry Challenge).
    Requires both code (where applicable) and explanation.
    """
    session = engine.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Check if current stage accepts submissions
    requirements = STAGE_REQUIREMENTS[session.current_stage]
    if not requirements.requires_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stage {session.current_stage.value} does not require submissions"
        )
    
    # Record submission
    submission_data = {
        "code": request.code,
        "explanation": request.explanation,
        "language": request.language,
        "alternative_approaches": request.alternative_approaches,
        "metadata": request.metadata
    }
    
    progress = engine.record_submission(session, submission_data)
    
    # Check explanation acceptance
    explanation_accepted = len(request.explanation) >= 50
    
    # Check if verification is needed
    verification_required = (
        requirements.requires_verification and 
        not progress.verification_passed
    )
    
    # Check if can advance
    can_advance, unmet = engine.can_advance_stage(session)
    
    return SubmissionResponse(
        success=True,
        submission_id=len(progress.submissions),
        stage=LearningStageEnum(session.current_stage.value),
        explanation_accepted=explanation_accepted,
        verification_required=verification_required,
        feedback="Submission received. Please answer verification questions." if verification_required else None,
        can_advance=can_advance,
        unmet_requirements=unmet
    )


# =============================================================================
# VERIFICATION
# =============================================================================

@router.post(
    "/sessions/{session_id}/verify",
    response_model=VerificationResponse,
    summary="Verify understanding"
)
async def verify_understanding(
    session_id: str = Path(..., description="Session ID"),
    request: VerificationAnswerRequest = ...,
    current_user: dict = Depends(get_current_user),
    engine: LearningEngine = Depends(get_engine)
):
    """
    Submit answers to verification questions.
    Required for stages that need understanding verification.
    """
    session = engine.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Validate answers (simplified - in production, use LLM to evaluate)
    # For now, check if answers are substantial enough
    passed = True
    feedback_parts = []
    
    for q_id, answer in request.answers.items():
        if len(answer) < 20:
            passed = False
            feedback_parts.append(f"Answer to {q_id} needs more detail")
        else:
            feedback_parts.append(f"Answer to {q_id} accepted")
    
    if passed:
        engine.mark_verification_passed(session)
    
    can_advance, _ = engine.can_advance_stage(session)
    
    return VerificationResponse(
        success=True,
        passed=passed,
        feedback="; ".join(feedback_parts),
        can_advance=can_advance
    )


# =============================================================================
# STAGE ADVANCEMENT
# =============================================================================

@router.post(
    "/sessions/{session_id}/advance",
    response_model=AdvanceStageResponse,
    summary="Advance to next stage"
)
async def advance_stage(
    session_id: str = Path(..., description="Session ID"),
    request: AdvanceStageRequest = AdvanceStageRequest(),
    current_user: dict = Depends(get_current_user),
    engine: LearningEngine = Depends(get_engine)
):
    """
    Advance to the next learning stage.
    
    Requirements must be met unless `force=true` (admin only, with 50% XP penalty).
    
    Stages cannot be easily skipped to ensure genuine learning.
    """
    session = engine.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    if session.is_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is already complete"
        )
    
    # Check if forcing requires admin privileges
    if request.force:
        # In production, check for admin role
        is_admin = current_user.get("role") == "admin"
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required to force stage advancement"
            )
    
    # Try to advance
    success, message, new_stage = engine.advance_to_next_stage(session, force=request.force)
    
    if not success:
        # Get unmet requirements for error response
        _, unmet = engine.can_advance_stage(session)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "cannot_advance",
                "message": message,
                "current_stage": session.current_stage.value,
                "unmet_requirements": unmet
            }
        )
    
    # Get new stage content
    stage_content = None
    xp_earned = 0
    
    if new_stage:
        content = STAGE_CONTENT[new_stage]
        prompt = engine.get_stage_prompt(session, new_stage)
        
        # XP from previous stage
        prev_idx = engine.STAGE_ORDER.index(new_stage) - 1
        if prev_idx >= 0:
            prev_stage = engine.STAGE_ORDER[prev_idx]
            xp_earned = session.stage_progress[prev_stage.value].xp_earned
        
        stage_content = StageContentResponse(
            stage=LearningStageEnum(new_stage.value),
            title=content.title,
            description=content.description,
            objectives=content.objectives,
            completion_criteria=content.completion_criteria,
            xp_reward=content.xp_reward,
            mentor_prompt=prompt
        )
    
    return AdvanceStageResponse(
        success=True,
        message=message,
        new_stage=LearningStageEnum(new_stage.value) if new_stage else None,
        xp_earned=xp_earned,
        stage_content=stage_content
    )


# =============================================================================
# HINTS
# =============================================================================

@router.post(
    "/sessions/{session_id}/hint",
    response_model=HintResponse,
    summary="Request a hint"
)
async def request_hint(
    session_id: str = Path(..., description="Session ID"),
    current_user: dict = Depends(get_current_user),
    engine: LearningEngine = Depends(get_engine)
):
    """
    Request a hint for the current stage.
    Hints come with an XP penalty for task stages.
    Maximum 3 hints per stage.
    """
    session = engine.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    progress = session.stage_progress[session.current_stage.value]
    
    success, message = engine.use_hint(session)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Generate hint (simplified - in production, use LLM)
    hint_number = progress.hints_used
    hints = [
        f"Think about the core concept of {session.topic}",
        f"Consider how {session.concept or session.topic} is typically implemented",
        f"Try breaking down the problem into smaller steps"
    ]
    hint_text = hints[hint_number - 1] if hint_number <= len(hints) else hints[-1]
    
    xp_penalty = 5 * hint_number if session.current_stage in [
        LearningStage.PRACTICAL_TASK,
        LearningStage.INDUSTRY_CHALLENGE
    ] else 0
    
    return HintResponse(
        success=True,
        hint_number=hint_number,
        total_hints=3,
        hint=hint_text,
        xp_penalty=xp_penalty,
        hints_remaining=3 - hint_number
    )


# =============================================================================
# SESSION COMPLETION
# =============================================================================

@router.post(
    "/sessions/{session_id}/complete",
    response_model=CompletionResponse,
    summary="Complete the learning session"
)
async def complete_session(
    session_id: str = Path(..., description="Session ID"),
    current_user: dict = Depends(get_current_user),
    engine: LearningEngine = Depends(get_engine)
):
    """
    Complete the learning session.
    All stages must be completed (or skipped by admin) before completion.
    """
    session = engine.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.user_id != str(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    result = engine.complete_session(session)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return CompletionResponse(
        success=True,
        message=result["message"],
        summary=result.get("summary")
    )


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.get(
    "/stages",
    response_model=List[StageContentResponse],
    summary="List all learning stages"
)
async def list_stages():
    """Get information about all 8 learning stages"""
    stages = []
    
    for stage in LearningEngine.STAGE_ORDER:
        content = STAGE_CONTENT[stage]
        stages.append(StageContentResponse(
            stage=LearningStageEnum(stage.value),
            title=content.title,
            description=content.description,
            objectives=content.objectives,
            completion_criteria=content.completion_criteria,
            xp_reward=content.xp_reward,
            mentor_prompt=""  # Don't expose mentor prompts here
        ))
    
    return stages


@router.get(
    "/stages/{stage}/requirements",
    response_model=StageRequirementsResponse,
    summary="Get generic stage requirements"
)
async def get_generic_stage_requirements(
    stage: LearningStageEnum = Path(..., description="Stage to check")
):
    """Get the requirements for a specific stage (without session context)"""
    requirements = STAGE_REQUIREMENTS[LearningStage(stage.value)]
    
    return StageRequirementsResponse(
        stage=stage,
        min_interactions=requirements.min_interactions,
        min_time_seconds=requirements.min_time_seconds,
        requires_submission=requirements.requires_submission,
        requires_explanation=requirements.requires_explanation,
        requires_verification=requirements.requires_verification,
        min_word_count=requirements.min_word_count
    )
