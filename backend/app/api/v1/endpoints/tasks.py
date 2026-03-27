"""
Task Endpoints
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.task_service import TaskService
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    SubmissionCreate,
    TaskResponse,
    TaskDetailResponse,
    TaskListResponse,
    TaskEvaluationResult,
    HintResponse,
    DailyTasksResponse
)
from app.models.task import TaskStatus, TaskType
from app.dependencies import get_current_active_user, PaginationParams
from app.models.user import User


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "",
    response_model=TaskListResponse,
    summary="Get tasks"
)
async def get_tasks(
    status_filter: Optional[TaskStatus] = Query(None, description="Filter by status"),
    type_filter: Optional[TaskType] = Query(None, description="Filter by type"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all tasks for the current user.
    """
    service = TaskService(db)
    return await service.get_tasks(current_user.id, pagination, status_filter, type_filter)


@router.get(
    "/daily",
    response_model=DailyTasksResponse,
    summary="Get daily tasks"
)
async def get_daily_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get today's daily tasks.
    """
    service = TaskService(db)
    return await service.get_daily_tasks(current_user.id)


@router.get(
    "/{task_id}",
    response_model=TaskDetailResponse,
    summary="Get task details"
)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a task.
    """
    service = TaskService(db)
    task = await service.get_task(task_id, current_user.id)
    return TaskDetailResponse.model_validate(task)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=201,
    summary="Create task"
)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new task.
    """
    service = TaskService(db)
    task = await service.create_task(current_user.id, data)
    return TaskResponse.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task"
)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a task.
    """
    service = TaskService(db)
    task = await service.update_task(task_id, current_user.id, data)
    return TaskResponse.model_validate(task)


@router.delete(
    "/{task_id}",
    response_model=dict,
    summary="Delete task"
)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a task.
    """
    service = TaskService(db)
    return await service.delete_task(task_id, current_user.id)


@router.post(
    "/{task_id}/start",
    response_model=TaskResponse,
    summary="Start task"
)
async def start_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start working on a task.
    """
    service = TaskService(db)
    task = await service.start_task(task_id, current_user.id)
    return TaskResponse.model_validate(task)


@router.post(
    "/submit",
    response_model=TaskEvaluationResult,
    summary="Submit task solution"
)
async def submit_task(
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit a solution for a task.
    """
    service = TaskService(db)
    return await service.submit_task(current_user.id, data)


@router.get(
    "/{task_id}/hint",
    response_model=HintResponse,
    summary="Get hint"
)
async def get_hint(
    task_id: UUID,
    hint_index: Optional[int] = Query(None, description="Specific hint index"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a hint for a task.
    
    Using hints will reduce XP earned.
    """
    service = TaskService(db)
    return await service.get_hint(task_id, current_user.id, hint_index)
