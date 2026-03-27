"""
VidyaGuru Task Management & Skill Tracking - API Endpoints
"""
from typing import Optional, List
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.database import get_db
from app.dependencies import get_redis, get_current_user
from app.tasks.models import TaskType, TaskStatus, TaskDifficulty, SkillCategory
from app.tasks.schemas import (
    # Task schemas
    TaskCreateRequest, TaskUpdateRequest, TaskAssignRequest,
    TaskSubmissionRequest, TaskProgressUpdate, HintRequestSchema,
    TaskResponse, TaskListResponse, TaskAssignmentResponse,
    TaskAssignmentListResponse, TaskFeedbackResponse, HintResponseSchema,
    # Skill schemas
    SkillResponse, SkillSummaryResponse, SkillHistoryResponse,
    SkillProgressChart,
    # Assessment schemas
    AssessmentStartRequest, AssessmentSubmitRequest, AssessmentResponse,
    # Milestone schemas
    MilestoneProgressResponse,
    # Analytics schemas
    OverallAnalyticsResponse, TaskAnalytics, SkillAnalytics,
    # Enums
    TaskTypeEnum, TaskStatusEnum, TaskDifficultyEnum, SkillCategoryEnum
)
from app.tasks.service import TaskService, SkillService, TaskAnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Tasks & Skills"])


# =============================================================================
# DEPENDENCIES
# =============================================================================

async def get_task_service(
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis)
) -> TaskService:
    """Get task service instance"""
    return TaskService(db=db, redis=redis)


async def get_skill_service(
    db: AsyncSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis)
) -> SkillService:
    """Get skill service instance"""
    return SkillService(db=db, redis=redis)


async def get_analytics_service(
    db: AsyncSession = Depends(get_db)
) -> TaskAnalyticsService:
    """Get analytics service instance"""
    return TaskAnalyticsService(db=db)


# =============================================================================
# TASK ENDPOINTS
# =============================================================================

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
async def create_task(
    data: TaskCreateRequest,
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Create a new learning task.
    
    Task types:
    - **coding_exercise**: Programming challenges with test cases
    - **concept_explanation**: Explain a concept to demonstrate understanding
    - **communication_task**: Professional communication scenarios
    - **research_task**: Research and summarize information
    - **industry_problem**: Real-world problem solving
    """
    task = await task_service.create_task(
        data=data,
        created_by=UUID(current_user["id"])
    )
    return task


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List available tasks"
)
async def list_tasks(
    topic: Optional[str] = Query(None, description="Filter by topic"),
    task_type: Optional[TaskTypeEnum] = Query(None, description="Filter by task type"),
    difficulty: Optional[TaskDifficultyEnum] = Query(None, description="Filter by difficulty"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """List available tasks with filtering options"""
    tag_list = tags.split(",") if tags else None
    
    task_type_model = TaskType(task_type.value) if task_type else None
    difficulty_model = TaskDifficulty(difficulty.value) if difficulty else None
    
    tasks, total = await task_service.get_tasks(
        topic=topic,
        task_type=task_type_model,
        difficulty=difficulty_model,
        tags=tag_list,
        page=page,
        page_size=page_size
    )
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task details"
)
async def get_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Get detailed information about a specific task"""
    task = await task_service.get_task(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task"
)
async def update_task(
    task_id: UUID,
    data: TaskUpdateRequest,
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Update an existing task"""
    task = await task_service.update_task(task_id, data)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task"
)
async def delete_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Soft delete a task"""
    success = await task_service.delete_task(task_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


# =============================================================================
# TASK ASSIGNMENT ENDPOINTS
# =============================================================================

@router.post(
    "/assignments",
    response_model=TaskAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign a task to yourself"
)
async def assign_task(
    data: TaskAssignRequest,
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Assign a task to the current user"""
    try:
        assignment = await task_service.assign_task(
            user_id=UUID(current_user["id"]),
            data=data
        )
        
        # Load task relationship
        assignment = await task_service.get_assignment(assignment.id)
        return assignment
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/assignments",
    response_model=TaskAssignmentListResponse,
    summary="List your task assignments"
)
async def list_assignments(
    status_filter: Optional[TaskStatusEnum] = Query(None, alias="status"),
    task_type: Optional[TaskTypeEnum] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """List your task assignments with filtering"""
    status_model = TaskStatus(status_filter.value) if status_filter else None
    type_model = TaskType(task_type.value) if task_type else None
    
    assignments, total = await task_service.get_user_assignments(
        user_id=UUID(current_user["id"]),
        status=status_model,
        task_type=type_model,
        page=page,
        page_size=page_size
    )
    
    return TaskAssignmentListResponse(
        assignments=assignments,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/assignments/{assignment_id}",
    response_model=TaskAssignmentResponse,
    summary="Get assignment details"
)
async def get_assignment(
    assignment_id: UUID,
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Get details of a specific assignment"""
    assignment = await task_service.get_assignment(
        assignment_id=assignment_id,
        user_id=UUID(current_user["id"])
    )
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return assignment


@router.post(
    "/assignments/{assignment_id}/start",
    response_model=TaskAssignmentResponse,
    summary="Start working on a task"
)
async def start_task(
    assignment_id: UUID,
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Start working on an assigned task"""
    try:
        assignment = await task_service.start_task(
            assignment_id=assignment_id,
            user_id=UUID(current_user["id"])
        )
        
        assignment = await task_service.get_assignment(assignment.id)
        return assignment
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/assignments/{assignment_id}/submit",
    response_model=TaskAssignmentResponse,
    summary="Submit task solution"
)
async def submit_task(
    assignment_id: UUID,
    submission: TaskSubmissionRequest,
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Submit a solution for a task"""
    try:
        assignment = await task_service.submit_task(
            assignment_id=assignment_id,
            user_id=UUID(current_user["id"]),
            submission=submission
        )
        
        assignment = await task_service.get_assignment(assignment.id)
        return assignment
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/assignments/{assignment_id}/evaluate",
    response_model=TaskFeedbackResponse,
    summary="Evaluate submitted task"
)
async def evaluate_task(
    assignment_id: UUID,
    score: float = Query(..., ge=0, le=100),
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
    skill_service: SkillService = Depends(get_skill_service)
):
    """
    Evaluate a submitted task (typically called by AI or admin).
    In production, this would be automated with AI evaluation.
    """
    try:
        # Generate feedback (simplified - would use AI in production)
        feedback = {
            "strengths": ["Good approach", "Clear code"],
            "improvements": ["Consider edge cases"],
            "detailed_scores": {
                "correctness": score,
                "efficiency": score * 0.9,
                "readability": score * 0.95
            }
        }
        
        assignment = await task_service.evaluate_task(
            assignment_id=assignment_id,
            score=score,
            feedback=feedback,
            skill_service=skill_service
        )
        
        return TaskFeedbackResponse(
            assignment_id=assignment.id,
            score=assignment.score,
            passed=assignment.status == TaskStatus.COMPLETED,
            feedback=assignment.feedback,
            skill_gains=assignment.skill_gains,
            xp_earned=assignment.xp_earned,
            bonus_xp=assignment.bonus_xp,
            next_recommended_tasks=[]  # Would recommend based on performance
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/assignments/{assignment_id}/hint",
    response_model=HintResponseSchema,
    summary="Request a hint"
)
async def request_hint(
    assignment_id: UUID,
    request: HintRequestSchema,
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """Request a hint for a task (costs XP)"""
    try:
        hint_content, xp_penalty = await task_service.get_hint(
            assignment_id=assignment_id,
            user_id=UUID(current_user["id"]),
            hint_number=request.hint_number
        )
        
        # Get total hints available
        assignment = await task_service.get_assignment(assignment_id)
        total_hints = len(assignment.task.content.get("hints", []))
        
        return HintResponseSchema(
            hint_number=request.hint_number,
            total_hints=total_hints,
            hint_content=hint_content,
            xp_penalty=xp_penalty
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# SKILL ENDPOINTS
# =============================================================================

@router.get(
    "/skills",
    response_model=SkillSummaryResponse,
    summary="Get your skill summary"
)
async def get_skill_summary(
    current_user: dict = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """Get comprehensive summary of all your skills"""
    summary = await skill_service.get_skill_summary(
        user_id=UUID(current_user["id"])
    )
    return summary


@router.get(
    "/skills/{category}",
    response_model=SkillResponse,
    summary="Get specific skill details"
)
async def get_skill(
    category: SkillCategoryEnum,
    topic: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """Get details of a specific skill"""
    skill = await skill_service.get_or_create_skill(
        user_id=UUID(current_user["id"]),
        category=SkillCategory(category.value),
        topic=topic
    )
    return skill


@router.get(
    "/skills/{category}/history",
    response_model=SkillHistoryResponse,
    summary="Get skill change history"
)
async def get_skill_history(
    category: SkillCategoryEnum,
    days: int = Query(30, ge=1, le=365),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """Get history of skill level changes"""
    skill = await skill_service.get_or_create_skill(
        user_id=UUID(current_user["id"]),
        category=SkillCategory(category.value)
    )
    
    history = await skill_service.get_skill_history(
        user_id=UUID(current_user["id"]),
        skill_id=skill.id,
        days=days,
        limit=page_size
    )
    
    return SkillHistoryResponse(
        history=history,
        total=len(history),
        page=page,
        page_size=page_size
    )


# =============================================================================
# ASSESSMENT ENDPOINTS
# =============================================================================

@router.post(
    "/assessments",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a skill assessment"
)
async def start_assessment(
    data: AssessmentStartRequest,
    current_user: dict = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """
    Start a skill assessment.
    
    Assessment types:
    - **initial**: First assessment for a skill
    - **periodic**: Regular progress check
    - **challenge**: Advanced assessment for certification
    """
    assessment = await skill_service.create_assessment(
        user_id=UUID(current_user["id"]),
        category=SkillCategory(data.category.value),
        topic=data.topic,
        assessment_type=data.assessment_type
    )
    return assessment


@router.post(
    "/assessments/{assessment_id}/submit",
    response_model=AssessmentResponse,
    summary="Submit assessment responses"
)
async def submit_assessment(
    assessment_id: UUID,
    data: AssessmentSubmitRequest,
    current_user: dict = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """Submit responses for an assessment"""
    try:
        assessment = await skill_service.complete_assessment(
            assessment_id=assessment_id,
            user_id=UUID(current_user["id"]),
            responses=data.responses
        )
        return assessment
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# MILESTONE ENDPOINTS
# =============================================================================

@router.get(
    "/milestones",
    response_model=MilestoneProgressResponse,
    summary="Get milestone progress"
)
async def get_milestones(
    current_user: dict = Depends(get_current_user),
    skill_service: SkillService = Depends(get_skill_service)
):
    """Get achieved milestones and progress towards others"""
    achieved, in_progress = await skill_service.get_user_milestones(
        user_id=UUID(current_user["id"])
    )
    
    return MilestoneProgressResponse(
        achieved=achieved,
        in_progress=in_progress,
        total_achieved=len(achieved),
        total_available=len(achieved) + len(in_progress)
    )


# =============================================================================
# ANALYTICS ENDPOINTS
# =============================================================================

@router.get(
    "/analytics",
    response_model=OverallAnalyticsResponse,
    summary="Get learning analytics"
)
async def get_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    analytics_service: TaskAnalyticsService = Depends(get_analytics_service),
    skill_service: SkillService = Depends(get_skill_service)
):
    """Get comprehensive learning analytics"""
    user_id = UUID(current_user["id"])
    
    task_analytics = await analytics_service.get_task_analytics(user_id, days)
    skill_analytics = await analytics_service.get_skill_analytics(user_id, days)
    
    # Get skill summary for additional metrics
    skill_summary = await skill_service.get_skill_summary(user_id)
    
    # Get milestones count
    achieved, _ = await skill_service.get_user_milestones(user_id)
    
    return OverallAnalyticsResponse(
        user_id=user_id,
        period_days=days,
        task_analytics=TaskAnalytics(**task_analytics),
        skill_analytics=SkillAnalytics(**skill_analytics),
        milestones_achieved=len(achieved),
        current_streak=max(
            (s.streak_days for s in skill_summary.get("skills", {}).values() 
             if hasattr(s, "streak_days")),
            default=0
        ),
        total_learning_minutes=int(task_analytics["average_time_minutes"] * task_analytics["total_tasks_completed"]),
        xp_earned_period=skill_summary.get("total_xp", 0)
    )


@router.get(
    "/analytics/tasks",
    response_model=TaskAnalytics,
    summary="Get task analytics"
)
async def get_task_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    analytics_service: TaskAnalyticsService = Depends(get_analytics_service)
):
    """Get detailed task completion analytics"""
    analytics = await analytics_service.get_task_analytics(
        user_id=UUID(current_user["id"]),
        days=days
    )
    return TaskAnalytics(**analytics)


@router.get(
    "/analytics/skills",
    response_model=SkillAnalytics,
    summary="Get skill analytics"
)
async def get_skill_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    analytics_service: TaskAnalyticsService = Depends(get_analytics_service)
):
    """Get detailed skill development analytics"""
    analytics = await analytics_service.get_skill_analytics(
        user_id=UUID(current_user["id"]),
        days=days
    )
    return SkillAnalytics(**analytics)


# =============================================================================
# TASK TYPE SPECIFIC ENDPOINTS
# =============================================================================

@router.get(
    "/coding-exercises",
    response_model=TaskListResponse,
    summary="List coding exercises"
)
async def list_coding_exercises(
    topic: Optional[str] = None,
    difficulty: Optional[TaskDifficultyEnum] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """List available coding exercises"""
    difficulty_model = TaskDifficulty(difficulty.value) if difficulty else None
    
    tasks, total = await task_service.get_tasks(
        topic=topic,
        task_type=TaskType.CODING_EXERCISE,
        difficulty=difficulty_model,
        page=page,
        page_size=page_size
    )
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )


@router.get(
    "/industry-problems",
    response_model=TaskListResponse,
    summary="List industry problems"
)
async def list_industry_problems(
    topic: Optional[str] = None,
    difficulty: Optional[TaskDifficultyEnum] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """List available industry problem-solving tasks"""
    difficulty_model = TaskDifficulty(difficulty.value) if difficulty else None
    
    tasks, total = await task_service.get_tasks(
        topic=topic,
        task_type=TaskType.INDUSTRY_PROBLEM,
        difficulty=difficulty_model,
        page=page,
        page_size=page_size
    )
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total
    )
