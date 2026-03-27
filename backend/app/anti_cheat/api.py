"""
VidyaGuru Anti-Cheating System - API Endpoints
===============================================

REST API for integrity verification and monitoring.
"""

from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin_user
from app.models.user import User

from app.anti_cheat.models import (
    SubmissionAnalysis,
    VerificationChallenge,
    UserIntegrityProfile,
    SuspiciousActivityLog,
    SuspicionLevel,
    VerificationStatus
)
from app.anti_cheat.schemas import (
    SubmissionWithMetrics,
    SubmissionAnalysisResponse,
    SubmissionAnalysisResult,
    VerificationChallengeResponse,
    VerificationSubmitRequest,
    VerificationResultResponse,
    VerificationTypeEnum,
    IntegrityProfileResponse,
    IntegrityStatsResponse,
    VerificationHistoryItem,
    SuspiciousActivityResponse,
    ActivityAlertResponse,
    GenuineLearnerReminder,
    IntegrityAnalyticsSummary,
    FlaggedSubmissionResponse,
    REMINDER_MESSAGES,
    SuspicionLevelEnum,
    VerificationStatusEnum,
    IntegrityLevelEnum
)
from app.anti_cheat.service import (
    SubmissionAnalyzer,
    VerificationService,
    IntegrityService
)

router = APIRouter(prefix="/integrity", tags=["Integrity & Anti-Cheat"])


# ============================================================================
# Submission Analysis Endpoints
# ============================================================================

@router.post(
    "/analyze",
    response_model=SubmissionAnalysisResponse,
    summary="Analyze a submission for suspicious behavior",
    description="""
    Analyzes a task submission for potential cheating indicators.
    
    Detection methods:
    - Large paste detection
    - Rapid submission timing
    - Similar/identical answer matching
    - Typing pattern anomalies
    - Skill consistency checking
    
    Returns analysis results and may include a verification challenge if needed.
    """
)
async def analyze_submission(
    submission: SubmissionWithMetrics,
    task_id: UUID = Query(..., description="ID of the task being submitted"),
    expected_time_seconds: int = Query(600, description="Expected completion time"),
    task_type: str = Query("general", description="Type of task"),
    task_difficulty: str = Query("intermediate", description="Task difficulty"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze submission and return integrity assessment"""
    analyzer = SubmissionAnalyzer(db)
    
    # Perform analysis
    result = await analyzer.analyze_submission(
        submission=submission,
        task_id=task_id,
        expected_time_seconds=expected_time_seconds,
        task_type=task_type,
        task_difficulty=task_difficulty
    )
    
    # Update user's integrity profile
    integrity_service = IntegrityService(db)
    await integrity_service.update_on_submission(
        user_id=current_user.id,
        was_flagged=result.suspicion_level in [SuspicionLevelEnum.HIGH, SuspicionLevelEnum.CRITICAL],
        suspicion_score=result.suspicion_score
    )
    
    # Generate verification challenge if needed
    verification = None
    user_message = None
    
    if result.requires_verification:
        verification_service = VerificationService(db)
        verification = await verification_service.create_challenge(
            analysis_id=result.submission_analysis_id,
            user_id=current_user.id,
            verification_type=result.recommended_verification_type or VerificationTypeEnum.FOLLOW_UP_QUESTION,
            original_content=submission.content,
            task_context={
                "task_id": str(task_id),
                "task_type": task_type,
                "difficulty": task_difficulty
            }
        )
        
        # Get polite reminder message
        reminder = await integrity_service.get_reminder_message(
            user_id=current_user.id,
            suspicion_type=result.indicators[0].type if result.indicators else None
        )
        user_message = f"{reminder.title}\n\n{reminder.message}\n\n{reminder.encouragement}"
        
        # Log suspicious activity
        if result.indicators:
            for indicator in result.indicators:
                await integrity_service.log_suspicious_activity(
                    user_id=current_user.id,
                    analysis_id=result.submission_analysis_id,
                    suspicion_type=indicator.type,
                    severity=indicator.severity,
                    description=indicator.description,
                    evidence=indicator.evidence
                )
    
    return SubmissionAnalysisResponse(
        analysis=result,
        verification_challenge=verification,
        user_message=user_message
    )


@router.get(
    "/analysis/{analysis_id}",
    response_model=SubmissionAnalysisResult,
    summary="Get submission analysis details"
)
async def get_analysis(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific submission analysis"""
    analysis = await db.get(SubmissionAnalysis, analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Users can only view their own analyses
    if analysis.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return SubmissionAnalysisResult(
        submission_analysis_id=analysis.id,
        task_assignment_id=analysis.task_assignment_id,
        suspicion_level=SuspicionLevelEnum(analysis.suspicion_level.value),
        suspicion_score=analysis.suspicion_score,
        requires_verification=analysis.requires_verification,
        indicators=[],  # Could reconstruct from suspicion_details
        summary=f"Suspicion level: {analysis.suspicion_level.value}"
    )


# ============================================================================
# Verification Challenge Endpoints
# ============================================================================

@router.get(
    "/verification/pending",
    response_model=List[VerificationChallengeResponse],
    summary="Get pending verification challenges"
)
async def get_pending_verifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all pending verification challenges for the current user"""
    result = await db.execute(
        select(VerificationChallenge)
        .where(
            and_(
                VerificationChallenge.user_id == current_user.id,
                VerificationChallenge.status.in_([
                    VerificationStatus.PENDING,
                    VerificationStatus.IN_PROGRESS
                ]),
                VerificationChallenge.expires_at > datetime.now(timezone.utc)
            )
        )
        .order_by(VerificationChallenge.created_at)
    )
    challenges = result.scalars().all()
    
    return [
        VerificationChallengeResponse(
            id=c.id,
            verification_type=VerificationTypeEnum(c.verification_type.value),
            prompt=c.challenge_prompt,
            context=c.challenge_context,
            original_code=c.original_code,
            min_response_length=c.min_response_length,
            expires_at=c.expires_at,
            attempt_number=c.attempt_number,
            max_attempts=c.max_attempts
        )
        for c in challenges
    ]


@router.get(
    "/verification/{challenge_id}",
    response_model=VerificationChallengeResponse,
    summary="Get verification challenge details"
)
async def get_verification_challenge(
    challenge_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific verification challenge"""
    challenge = await db.get(VerificationChallenge, challenge_id)
    
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    if challenge.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check expiry
    if datetime.now(timezone.utc) > challenge.expires_at:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This verification challenge has expired"
        )
    
    return VerificationChallengeResponse(
        id=challenge.id,
        verification_type=VerificationTypeEnum(challenge.verification_type.value),
        prompt=challenge.challenge_prompt,
        context=challenge.challenge_context,
        original_code=challenge.original_code,
        min_response_length=challenge.min_response_length,
        expires_at=challenge.expires_at,
        attempt_number=challenge.attempt_number,
        max_attempts=challenge.max_attempts
    )


@router.post(
    "/verification/{challenge_id}/submit",
    response_model=VerificationResultResponse,
    summary="Submit response to verification challenge"
)
async def submit_verification(
    challenge_id: UUID,
    request: VerificationSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a response to a verification challenge"""
    challenge = await db.get(VerificationChallenge, challenge_id)
    
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    if challenge.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if challenge.status in [VerificationStatus.PASSED, VerificationStatus.EXPIRED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Challenge is already {challenge.status.value}"
        )
    
    verification_service = VerificationService(db)
    return await verification_service.evaluate_response(
        challenge_id=challenge_id,
        response=request.response,
        typing_metrics=request.typing_metrics
    )


@router.post(
    "/verification/{challenge_id}/start",
    response_model=VerificationChallengeResponse,
    summary="Start a verification challenge"
)
async def start_verification(
    challenge_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a verification challenge as started"""
    challenge = await db.get(VerificationChallenge, challenge_id)
    
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    if challenge.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if challenge.status != VerificationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge already started or completed"
        )
    
    challenge.status = VerificationStatus.IN_PROGRESS
    challenge.started_at = datetime.now(timezone.utc)
    await db.commit()
    
    return VerificationChallengeResponse(
        id=challenge.id,
        verification_type=VerificationTypeEnum(challenge.verification_type.value),
        prompt=challenge.challenge_prompt,
        context=challenge.challenge_context,
        original_code=challenge.original_code,
        min_response_length=challenge.min_response_length,
        expires_at=challenge.expires_at,
        attempt_number=challenge.attempt_number,
        max_attempts=challenge.max_attempts
    )


# ============================================================================
# User Integrity Profile Endpoints
# ============================================================================

@router.get(
    "/profile",
    response_model=IntegrityProfileResponse,
    summary="Get your integrity profile"
)
async def get_my_integrity_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current user's integrity profile"""
    integrity_service = IntegrityService(db)
    profile = await integrity_service.get_or_create_profile(current_user.id)
    
    # Calculate verification pass rate
    total_verifications = profile.verifications_passed + profile.verifications_failed
    pass_rate = (
        profile.verifications_passed / total_verifications 
        if total_verifications > 0 else 1.0
    )
    
    return IntegrityProfileResponse(
        user_id=profile.user_id,
        trust_score=profile.trust_score,
        integrity_level=IntegrityLevelEnum(profile.integrity_level),
        total_submissions=profile.total_submissions,
        flagged_submissions=profile.flagged_submissions,
        verification_pass_rate=pass_rate,
        is_restricted=profile.is_restricted,
        restriction_reason=profile.restriction_reason,
        restricted_until=profile.restricted_until
    )


@router.get(
    "/profile/stats",
    response_model=IntegrityStatsResponse,
    summary="Get detailed integrity statistics"
)
async def get_integrity_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed integrity statistics for the current user"""
    integrity_service = IntegrityService(db)
    profile = await integrity_service.get_or_create_profile(current_user.id)
    
    # Get recent verifications
    result = await db.execute(
        select(VerificationChallenge)
        .where(VerificationChallenge.user_id == current_user.id)
        .order_by(desc(VerificationChallenge.created_at))
        .limit(10)
    )
    recent_verifications = result.scalars().all()
    
    # Calculate verification pass rate
    total_verifications = profile.verifications_passed + profile.verifications_failed
    pass_rate = (
        profile.verifications_passed / total_verifications 
        if total_verifications > 0 else 1.0
    )
    
    profile_response = IntegrityProfileResponse(
        user_id=profile.user_id,
        trust_score=profile.trust_score,
        integrity_level=IntegrityLevelEnum(profile.integrity_level),
        total_submissions=profile.total_submissions,
        flagged_submissions=profile.flagged_submissions,
        verification_pass_rate=pass_rate,
        is_restricted=profile.is_restricted,
        restriction_reason=profile.restriction_reason,
        restricted_until=profile.restricted_until
    )
    
    verification_history = [
        VerificationHistoryItem(
            id=v.id,
            verification_type=VerificationTypeEnum(v.verification_type.value),
            status=VerificationStatusEnum(v.status.value),
            passed=v.passed,
            created_at=v.created_at
        )
        for v in recent_verifications
    ]
    
    # Calculate improvements
    improvements = []
    if profile.trust_score > 0.8:
        improvements.append("Your trust score is excellent!")
    if profile.flagged_submissions == 0:
        improvements.append("Perfect record - no flagged submissions!")
    if profile.verifications_passed > 0:
        improvements.append(f"Successfully passed {profile.verifications_passed} verification(s)")
    
    # Calculate streak days without flags
    streak_days = 0  # Would calculate from suspicious activity log
    
    return IntegrityStatsResponse(
        profile=profile_response,
        recent_verifications=verification_history,
        avg_submission_time=None,  # Would calculate from submissions
        typical_response_length=None,
        streak_days_without_flags=streak_days,
        improvements_noted=improvements
    )


# ============================================================================
# Reminder Messages Endpoints
# ============================================================================

@router.get(
    "/reminder/{reminder_type}",
    response_model=GenuineLearnerReminder,
    summary="Get a reminder message"
)
async def get_reminder_message(
    reminder_type: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific reminder message by type"""
    if reminder_type not in REMINDER_MESSAGES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder type not found"
        )
    
    return REMINDER_MESSAGES[reminder_type]


@router.get(
    "/reminder",
    response_model=GenuineLearnerReminder,
    summary="Get general integrity reminder"
)
async def get_general_reminder(
    current_user: User = Depends(get_current_user)
):
    """Get the general integrity reminder message"""
    return REMINDER_MESSAGES["general_integrity"]


# ============================================================================
# Activity Log Endpoints
# ============================================================================

@router.get(
    "/activity",
    response_model=List[SuspiciousActivityResponse],
    summary="Get your suspicious activity log"
)
async def get_my_activity_log(
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current user's suspicious activity log"""
    result = await db.execute(
        select(SuspiciousActivityLog)
        .where(SuspiciousActivityLog.user_id == current_user.id)
        .order_by(desc(SuspiciousActivityLog.detected_at))
        .limit(limit)
    )
    activities = result.scalars().all()
    
    return [
        SuspiciousActivityResponse(
            id=a.id,
            suspicion_type=a.suspicion_type.value,
            severity=SuspicionLevelEnum(a.severity.value),
            description=a.description,
            detected_at=a.detected_at,
            resolved=a.resolved
        )
        for a in activities
    ]


# ============================================================================
# Admin Endpoints
# ============================================================================

@router.get(
    "/admin/analytics",
    response_model=IntegrityAnalyticsSummary,
    summary="Get platform integrity analytics (Admin)",
    dependencies=[Depends(get_current_admin_user)]
)
async def get_integrity_analytics(
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get platform-wide integrity analytics (admin only)"""
    from datetime import timedelta
    
    period_start = datetime.now(timezone.utc) - timedelta(days=days)
    period_end = datetime.now(timezone.utc)
    
    # Get submission stats
    total_result = await db.execute(
        select(func.count(SubmissionAnalysis.id))
        .where(SubmissionAnalysis.created_at >= period_start)
    )
    total_submissions = total_result.scalar() or 0
    
    flagged_result = await db.execute(
        select(func.count(SubmissionAnalysis.id))
        .where(
            and_(
                SubmissionAnalysis.created_at >= period_start,
                SubmissionAnalysis.is_flagged == True
            )
        )
    )
    flagged_submissions = flagged_result.scalar() or 0
    
    # Verification stats
    verifications_result = await db.execute(
        select(func.count(VerificationChallenge.id))
        .where(VerificationChallenge.created_at >= period_start)
    )
    verifications_issued = verifications_result.scalar() or 0
    
    passed_result = await db.execute(
        select(func.count(VerificationChallenge.id))
        .where(
            and_(
                VerificationChallenge.created_at >= period_start,
                VerificationChallenge.passed == True
            )
        )
    )
    verifications_passed = passed_result.scalar() or 0
    
    failed_result = await db.execute(
        select(func.count(VerificationChallenge.id))
        .where(
            and_(
                VerificationChallenge.created_at >= period_start,
                VerificationChallenge.passed == False
            )
        )
    )
    verifications_failed = failed_result.scalar() or 0
    
    # User stats
    users_flagged_result = await db.execute(
        select(func.count(func.distinct(SubmissionAnalysis.user_id)))
        .where(
            and_(
                SubmissionAnalysis.created_at >= period_start,
                SubmissionAnalysis.is_flagged == True
            )
        )
    )
    users_with_flags = users_flagged_result.scalar() or 0
    
    restricted_result = await db.execute(
        select(func.count(UserIntegrityProfile.id))
        .where(UserIntegrityProfile.is_restricted == True)
    )
    users_restricted = restricted_result.scalar() or 0
    
    # Top suspicion types
    # (Simplified - would need proper aggregation in production)
    top_types = [
        {"type": "large_paste", "count": 0},
        {"type": "identical_answer", "count": 0},
        {"type": "rapid_submission", "count": 0}
    ]
    
    return IntegrityAnalyticsSummary(
        period_start=period_start,
        period_end=period_end,
        total_submissions=total_submissions,
        flagged_submissions=flagged_submissions,
        flag_rate=flagged_submissions / max(total_submissions, 1),
        verifications_issued=verifications_issued,
        verifications_passed=verifications_passed,
        verifications_failed=verifications_failed,
        pass_rate=verifications_passed / max(verifications_issued, 1),
        top_suspicion_types=top_types,
        users_with_flags=users_with_flags,
        users_restricted=users_restricted
    )


@router.get(
    "/admin/flagged",
    response_model=List[FlaggedSubmissionResponse],
    summary="Get flagged submissions (Admin)",
    dependencies=[Depends(get_current_admin_user)]
)
async def get_flagged_submissions(
    reviewed: Optional[bool] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get list of flagged submissions for admin review"""
    query = select(SubmissionAnalysis).where(
        SubmissionAnalysis.is_flagged == True
    )
    
    if reviewed is not None:
        query = query.where(SubmissionAnalysis.reviewed_by_admin == reviewed)
    
    query = query.order_by(desc(SubmissionAnalysis.created_at)).limit(limit)
    
    result = await db.execute(query)
    submissions = result.scalars().all()
    
    return [
        FlaggedSubmissionResponse(
            id=s.id,
            user_id=s.user_id,
            task_assignment_id=s.task_assignment_id,
            suspicion_level=SuspicionLevelEnum(s.suspicion_level.value),
            suspicion_types=s.suspicion_types,
            suspicion_score=s.suspicion_score,
            suspicion_details=s.suspicion_details,
            reviewed=s.reviewed_by_admin,
            admin_notes=s.admin_notes,
            created_at=s.created_at
        )
        for s in submissions
    ]


@router.patch(
    "/admin/flagged/{analysis_id}/review",
    response_model=FlaggedSubmissionResponse,
    summary="Review a flagged submission (Admin)",
    dependencies=[Depends(get_current_admin_user)]
)
async def review_flagged_submission(
    analysis_id: UUID,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Mark a flagged submission as reviewed with notes"""
    analysis = await db.get(SubmissionAnalysis, analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    analysis.reviewed_by_admin = True
    analysis.admin_notes = notes
    
    await db.commit()
    await db.refresh(analysis)
    
    return FlaggedSubmissionResponse(
        id=analysis.id,
        user_id=analysis.user_id,
        task_assignment_id=analysis.task_assignment_id,
        suspicion_level=SuspicionLevelEnum(analysis.suspicion_level.value),
        suspicion_types=analysis.suspicion_types,
        suspicion_score=analysis.suspicion_score,
        suspicion_details=analysis.suspicion_details,
        reviewed=analysis.reviewed_by_admin,
        admin_notes=analysis.admin_notes,
        created_at=analysis.created_at
    )


@router.get(
    "/admin/user/{user_id}/profile",
    response_model=IntegrityProfileResponse,
    summary="Get user integrity profile (Admin)",
    dependencies=[Depends(get_current_admin_user)]
)
async def get_user_integrity_profile_admin(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific user's integrity profile (admin only)"""
    integrity_service = IntegrityService(db)
    profile = await integrity_service.get_or_create_profile(user_id)
    
    total_verifications = profile.verifications_passed + profile.verifications_failed
    pass_rate = (
        profile.verifications_passed / total_verifications 
        if total_verifications > 0 else 1.0
    )
    
    return IntegrityProfileResponse(
        user_id=profile.user_id,
        trust_score=profile.trust_score,
        integrity_level=IntegrityLevelEnum(profile.integrity_level),
        total_submissions=profile.total_submissions,
        flagged_submissions=profile.flagged_submissions,
        verification_pass_rate=pass_rate,
        is_restricted=profile.is_restricted,
        restriction_reason=profile.restriction_reason,
        restricted_until=profile.restricted_until
    )


@router.patch(
    "/admin/user/{user_id}/restrict",
    response_model=IntegrityProfileResponse,
    summary="Restrict a user (Admin)",
    dependencies=[Depends(get_current_admin_user)]
)
async def restrict_user(
    user_id: UUID,
    reason: str,
    duration_days: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Restrict a user from submitting without verification (admin only)"""
    from datetime import timedelta
    
    integrity_service = IntegrityService(db)
    profile = await integrity_service.get_or_create_profile(user_id)
    
    profile.is_restricted = True
    profile.restriction_reason = reason
    profile.requires_verification_always = True
    
    if duration_days:
        profile.restricted_until = datetime.now(timezone.utc) + timedelta(days=duration_days)
    
    await db.commit()
    await db.refresh(profile)
    
    total_verifications = profile.verifications_passed + profile.verifications_failed
    pass_rate = (
        profile.verifications_passed / total_verifications 
        if total_verifications > 0 else 1.0
    )
    
    return IntegrityProfileResponse(
        user_id=profile.user_id,
        trust_score=profile.trust_score,
        integrity_level=IntegrityLevelEnum(profile.integrity_level),
        total_submissions=profile.total_submissions,
        flagged_submissions=profile.flagged_submissions,
        verification_pass_rate=pass_rate,
        is_restricted=profile.is_restricted,
        restriction_reason=profile.restriction_reason,
        restricted_until=profile.restricted_until
    )


@router.patch(
    "/admin/user/{user_id}/unrestrict",
    response_model=IntegrityProfileResponse,
    summary="Remove user restriction (Admin)",
    dependencies=[Depends(get_current_admin_user)]
)
async def unrestrict_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Remove restriction from a user (admin only)"""
    integrity_service = IntegrityService(db)
    profile = await integrity_service.get_or_create_profile(user_id)
    
    profile.is_restricted = False
    profile.restriction_reason = None
    profile.restricted_until = None
    
    # Optionally remove always-verify requirement based on trust score
    if profile.trust_score > 0.7:
        profile.requires_verification_always = False
    
    await db.commit()
    await db.refresh(profile)
    
    total_verifications = profile.verifications_passed + profile.verifications_failed
    pass_rate = (
        profile.verifications_passed / total_verifications 
        if total_verifications > 0 else 1.0
    )
    
    return IntegrityProfileResponse(
        user_id=profile.user_id,
        trust_score=profile.trust_score,
        integrity_level=IntegrityLevelEnum(profile.integrity_level),
        total_submissions=profile.total_submissions,
        flagged_submissions=profile.flagged_submissions,
        verification_pass_rate=pass_rate,
        is_restricted=profile.is_restricted,
        restriction_reason=profile.restriction_reason,
        restricted_until=profile.restricted_until
    )
