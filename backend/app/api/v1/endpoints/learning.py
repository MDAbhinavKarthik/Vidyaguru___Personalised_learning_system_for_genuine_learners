"""
Learning Endpoints
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.learning_service import LearningService
from app.schemas.learning import (
    LearningPathCreate,
    LearningPathUpdate,
    LearningPathGenerate,
    LearningPathResponse,
    LearningPathDetailResponse,
    ModuleResponse,
    ModuleDetailResponse,
    RecommendationResponse
)
from app.models.learning import PathStatus
from app.dependencies import get_current_active_user, PaginationParams
from app.models.user import User


router = APIRouter(prefix="/learning", tags=["Learning"])


# Learning Paths
@router.get(
    "/paths",
    response_model=dict,
    summary="Get learning paths"
)
async def get_learning_paths(
    status_filter: Optional[PathStatus] = Query(None, description="Filter by status"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all learning paths for the current user.
    """
    service = LearningService(db)
    return await service.get_learning_paths(current_user.id, pagination, status_filter)


@router.get(
    "/paths/{path_id}",
    response_model=LearningPathDetailResponse,
    summary="Get learning path details"
)
async def get_learning_path(
    path_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a learning path.
    """
    service = LearningService(db)
    path = await service.get_learning_path(path_id, current_user.id)
    return LearningPathDetailResponse.model_validate(path)


@router.post(
    "/paths",
    response_model=LearningPathResponse,
    status_code=201,
    summary="Create learning path"
)
async def create_learning_path(
    data: LearningPathCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new custom learning path.
    """
    service = LearningService(db)
    path = await service.create_learning_path(current_user.id, data)
    return LearningPathResponse.model_validate(path)


@router.post(
    "/paths/generate",
    response_model=LearningPathDetailResponse,
    status_code=201,
    summary="Generate AI learning path"
)
async def generate_learning_path(
    data: LearningPathGenerate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a personalized learning path using AI.
    """
    service = LearningService(db)
    path = await service.generate_learning_path(current_user.id, data)
    return LearningPathDetailResponse.model_validate(path)


@router.patch(
    "/paths/{path_id}",
    response_model=LearningPathResponse,
    summary="Update learning path"
)
async def update_learning_path(
    path_id: UUID,
    data: LearningPathUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a learning path.
    """
    service = LearningService(db)
    path = await service.update_learning_path(path_id, current_user.id, data)
    return LearningPathResponse.model_validate(path)


@router.delete(
    "/paths/{path_id}",
    response_model=dict,
    summary="Delete learning path"
)
async def delete_learning_path(
    path_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a learning path.
    """
    service = LearningService(db)
    return await service.delete_learning_path(path_id, current_user.id)


# Modules
@router.get(
    "/modules/{module_id}",
    response_model=ModuleDetailResponse,
    summary="Get module details"
)
async def get_module(
    module_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a module.
    """
    service = LearningService(db)
    module = await service.get_module(module_id, current_user.id)
    return ModuleDetailResponse.model_validate(module)


@router.post(
    "/modules/{module_id}/complete",
    response_model=dict,
    summary="Complete module"
)
async def complete_module(
    module_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark a module as completed and unlock the next module.
    """
    service = LearningService(db)
    return await service.complete_module(module_id, current_user.id)


# Recommendations
@router.get(
    "/recommendations",
    response_model=list[RecommendationResponse],
    summary="Get recommendations"
)
async def get_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get personalized learning recommendations.
    """
    service = LearningService(db)
    return await service.get_recommendations(current_user.id)
