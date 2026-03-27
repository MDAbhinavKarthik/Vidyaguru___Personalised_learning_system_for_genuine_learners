"""
Industry Challenges API Endpoints

REST API for:
- Generating and listing challenges
- Submitting and evaluating solutions
- Managing resume highlights
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.challenges.models import ChallengeCategory, ChallengeDifficulty
from app.challenges.schemas import (
    ChallengeGenerateRequest,
    ChallengeResponse,
    ChallengeListResponse,
    SolutionSubmitRequest,
    SolutionDraftRequest,
    SolutionResponse,
    SolutionEvaluationResponse,
    ResumeHighlightResponse,
    UserResumeHighlightsResponse,
    UserChallengeStatsResponse,
)
from app.challenges.service import (
    challenge_service,
    evaluation_service,
    resume_service,
)

router = APIRouter(prefix="/challenges", tags=["Industry Challenges"])


# ============================================================================
# CHALLENGE ENDPOINTS
# ============================================================================

@router.post("/generate", response_model=ChallengeResponse)
async def generate_challenge(
    request: ChallengeGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a new industry challenge using AI.
    
    Categories:
    - system_design: Design distributed systems
    - scalability: Solve scaling problems
    - algorithm_optimization: Optimize algorithms
    - software_architecture: Design software architecture
    """
    try:
        challenge = await challenge_service.generate_challenge(db, request)
        return challenge
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate challenge: {str(e)}")


@router.get("/", response_model=ChallengeListResponse)
async def list_challenges(
    category: Optional[ChallengeCategory] = None,
    difficulty: Optional[ChallengeDifficulty] = None,
    industry: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List available challenges with optional filters.
    """
    challenges, total = await challenge_service.list_challenges(
        db,
        category=category,
        difficulty=difficulty,
        industry=industry,
        page=page,
        page_size=page_size,
    )
    
    return ChallengeListResponse(
        challenges=challenges,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/random", response_model=ChallengeResponse)
async def get_random_challenge(
    category: Optional[ChallengeCategory] = None,
    difficulty: Optional[ChallengeDifficulty] = None,
    exclude_attempted: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a random challenge, optionally excluding ones the user has attempted.
    """
    user_id = current_user.id if exclude_attempted else None
    
    challenge = await challenge_service.get_random_challenge(
        db,
        category=category,
        difficulty=difficulty,
        user_id=user_id,
    )
    
    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="No matching challenges available. Try generating a new one!"
        )
    
    return challenge


@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific challenge by ID."""
    challenge = await challenge_service.get_challenge(db, challenge_id)
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    return challenge


# ============================================================================
# SOLUTION ENDPOINTS
# ============================================================================

@router.post("/solutions/submit", response_model=SolutionResponse)
async def submit_solution(
    request: SolutionSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a solution for a challenge.
    
    The solution will be queued for AI evaluation.
    """
    try:
        solution = await evaluation_service.submit_solution(
            db,
            user_id=current_user.id,
            request=request,
        )
        return solution
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/solutions/draft", response_model=SolutionResponse)
async def save_draft(
    request: SolutionDraftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Save a draft solution without submitting for evaluation.
    """
    from app.challenges.models import ChallengeSolution, SolutionStatus
    
    # Check for existing draft
    existing = db.query(ChallengeSolution).filter(
        ChallengeSolution.user_id == current_user.id,
        ChallengeSolution.challenge_id == request.challenge_id,
    ).first()
    
    if existing and existing.status in [SolutionStatus.EVALUATED, SolutionStatus.RESUME_WORTHY]:
        raise HTTPException(
            status_code=400,
            detail="You have already submitted and evaluated a solution for this challenge"
        )
    
    if existing:
        existing.solution_text = request.solution_text
        existing.architecture_diagram = request.architecture_diagram
        existing.trade_offs_discussed = request.trade_offs_discussed
        existing.technologies_proposed = request.technologies_proposed
        solution = existing
    else:
        solution = ChallengeSolution(
            user_id=current_user.id,
            challenge_id=request.challenge_id,
            solution_text=request.solution_text,
            architecture_diagram=request.architecture_diagram,
            trade_offs_discussed=request.trade_offs_discussed,
            technologies_proposed=request.technologies_proposed,
            status=SolutionStatus.DRAFT,
        )
        db.add(solution)
    
    db.commit()
    db.refresh(solution)
    
    return solution


@router.post("/solutions/{solution_id}/evaluate", response_model=SolutionEvaluationResponse)
async def evaluate_solution(
    solution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger AI evaluation of a submitted solution.
    
    Returns detailed feedback including:
    - Innovation, practicality, and completeness scores
    - Strengths and areas for improvement
    - Resume recommendation if the solution is outstanding
    """
    from app.challenges.models import ChallengeSolution
    
    # Verify ownership
    solution = db.query(ChallengeSolution).filter(
        ChallengeSolution.id == solution_id,
        ChallengeSolution.user_id == current_user.id,
    ).first()
    
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    try:
        evaluation = await evaluation_service.evaluate_solution(db, solution_id)
        return evaluation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/solutions/my", response_model=List[SolutionResponse])
async def get_my_solutions(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all solutions submitted by the current user."""
    from app.challenges.models import ChallengeSolution, SolutionStatus
    
    query = db.query(ChallengeSolution).filter(
        ChallengeSolution.user_id == current_user.id
    )
    
    if status:
        try:
            status_enum = SolutionStatus(status)
            query = query.filter(ChallengeSolution.status == status_enum)
        except ValueError:
            pass
    
    solutions = query.order_by(ChallengeSolution.created_at.desc()).all()
    return solutions


@router.get("/solutions/{solution_id}", response_model=SolutionResponse)  
async def get_solution(
    solution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific solution by ID."""
    from app.challenges.models import ChallengeSolution
    
    solution = db.query(ChallengeSolution).filter(
        ChallengeSolution.id == solution_id,
        ChallengeSolution.user_id == current_user.id,
    ).first()
    
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    return solution


# ============================================================================
# HINT ENDPOINT
# ============================================================================

@router.post("/{challenge_id}/hint")
async def get_hint(
    challenge_id: int,
    current_attempt: str = Query(..., description="What you've tried so far"),
    struggle_area: str = Query(..., description="Specific area you're stuck on"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a Socratic hint for a challenge without revealing the answer.
    
    The AI will ask guiding questions to help you discover the solution yourself.
    """
    try:
        hint = await evaluation_service.get_hint(
            db,
            challenge_id=challenge_id,
            current_attempt=current_attempt,
            struggle_area=struggle_area,
        )
        return hint
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# RESUME HIGHLIGHT ENDPOINTS
# ============================================================================

@router.get("/resume/highlights", response_model=UserResumeHighlightsResponse)
async def get_resume_highlights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all resume-worthy achievements from completed challenges.
    """
    from app.challenges.models import ChallengeSolution, SolutionStatus
    
    highlights = await resume_service.get_user_highlights(db, current_user.id)
    
    # Get stats
    total_completed = db.query(ChallengeSolution).filter(
        ChallengeSolution.user_id == current_user.id,
        ChallengeSolution.status == SolutionStatus.EVALUATED,
    ).count()
    
    resume_worthy = db.query(ChallengeSolution).filter(
        ChallengeSolution.user_id == current_user.id,
        ChallengeSolution.is_resume_worthy == True,
    ).count()
    
    return UserResumeHighlightsResponse(
        highlights=highlights,
        total_challenges_completed=total_completed,
        resume_worthy_solutions=resume_worthy,
    )


@router.post("/resume/highlights/{highlight_id}/add")
async def mark_added_to_resume(
    highlight_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a highlight as added to your resume."""
    try:
        highlight = await resume_service.mark_added_to_resume(
            db, highlight_id, current_user.id
        )
        return {"message": "Highlight marked as added to resume", "highlight_id": highlight.id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/resume/export")
async def export_resume_highlights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export all resume highlights as formatted text.
    
    Returns Markdown-formatted text ready to copy into your resume.
    """
    export_text = await resume_service.export_highlights(db, current_user.id)
    return {"content": export_text}


# ============================================================================
# STATISTICS ENDPOINT
# ============================================================================

@router.get("/stats/me", response_model=UserChallengeStatsResponse)
async def get_my_challenge_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get your challenge statistics."""
    from app.challenges.models import ChallengeSolution, SolutionStatus, IndustryChallenge
    from sqlalchemy import func
    
    # Basic stats
    total_attempted = db.query(ChallengeSolution).filter(
        ChallengeSolution.user_id == current_user.id
    ).count()
    
    total_completed = db.query(ChallengeSolution).filter(
        ChallengeSolution.user_id == current_user.id,
        ChallengeSolution.status.in_([SolutionStatus.EVALUATED, SolutionStatus.RESUME_WORTHY]),
    ).count()
    
    total_resume_worthy = db.query(ChallengeSolution).filter(
        ChallengeSolution.user_id == current_user.id,
        ChallengeSolution.is_resume_worthy == True,
    ).count()
    
    # Average score
    avg_result = db.query(func.avg(ChallengeSolution.overall_score)).filter(
        ChallengeSolution.user_id == current_user.id,
        ChallengeSolution.overall_score.isnot(None),
    ).scalar()
    average_score = float(avg_result) if avg_result else 0.0
    
    # Total XP
    xp_result = db.query(func.sum(ChallengeSolution.xp_earned)).filter(
        ChallengeSolution.user_id == current_user.id,
    ).scalar()
    total_xp = int(xp_result) if xp_result else 0
    
    # Challenges by category
    category_counts = db.query(
        IndustryChallenge.category,
        func.count(ChallengeSolution.id)
    ).join(
        ChallengeSolution,
        ChallengeSolution.challenge_id == IndustryChallenge.id
    ).filter(
        ChallengeSolution.user_id == current_user.id
    ).group_by(
        IndustryChallenge.category
    ).all()
    
    challenges_by_category = {cat.value: count for cat, count in category_counts}
    
    # Strongest category (highest average score)
    strongest = None
    if challenges_by_category:
        category_scores = db.query(
            IndustryChallenge.category,
            func.avg(ChallengeSolution.overall_score)
        ).join(
            ChallengeSolution,
            ChallengeSolution.challenge_id == IndustryChallenge.id
        ).filter(
            ChallengeSolution.user_id == current_user.id,
            ChallengeSolution.overall_score.isnot(None),
        ).group_by(
            IndustryChallenge.category
        ).all()
        
        if category_scores:
            strongest = max(category_scores, key=lambda x: x[1] or 0)[0].value
    
    return UserChallengeStatsResponse(
        total_attempted=total_attempted,
        total_completed=total_completed,
        total_resume_worthy=total_resume_worthy,
        average_score=round(average_score, 1),
        total_xp_earned=total_xp,
        challenges_by_category=challenges_by_category,
        strongest_category=strongest,
    )
