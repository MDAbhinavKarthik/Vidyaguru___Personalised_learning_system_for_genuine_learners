"""
Journal Endpoints
"""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.journal_service import JournalService
from app.schemas.journal import (
    JournalEntryCreate,
    JournalEntryUpdate,
    TagCreate,
    TagResponse,
    JournalEntryResponse,
    JournalEntryListResponse,
    JournalInsightsResponse,
    JournalSearchRequest,
    JournalReflectionResponse
)
from app.models.journal import EntryType
from app.dependencies import get_current_active_user, PaginationParams
from app.models.user import User


router = APIRouter(prefix="/journal", tags=["Journal"])


@router.get(
    "/entries",
    response_model=JournalEntryListResponse,
    summary="Get journal entries"
)
async def get_entries(
    entry_type: Optional[EntryType] = Query(None, description="Filter by type"),
    tag_ids: Optional[List[UUID]] = Query(None, description="Filter by tags"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all journal entries for the current user.
    """
    service = JournalService(db)
    return await service.get_entries(current_user.id, pagination, entry_type, tag_ids)


@router.get(
    "/entries/{entry_id}",
    response_model=JournalEntryResponse,
    summary="Get journal entry"
)
async def get_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific journal entry.
    """
    service = JournalService(db)
    entry = await service.get_entry(entry_id, current_user.id)
    # Convert tags
    tags = [TagResponse.model_validate(et.tag) for et in entry.entry_tags]
    return JournalEntryResponse(
        id=entry.id,
        user_id=entry.user_id,
        title=entry.title,
        content=entry.content,
        entry_type=entry.entry_type,
        mood=entry.mood,
        rich_content=entry.rich_content,
        ai_insights=entry.ai_insights,
        linked_entry_ids=entry.linked_entry_ids or [],
        related_module_id=entry.related_module_id,
        related_task_id=entry.related_task_id,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
        tags=tags
    )


@router.post(
    "/entries",
    response_model=JournalEntryResponse,
    status_code=201,
    summary="Create journal entry"
)
async def create_entry(
    data: JournalEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new journal entry.
    """
    service = JournalService(db)
    entry = await service.create_entry(current_user.id, data)
    tags = [TagResponse.model_validate(et.tag) for et in entry.entry_tags]
    return JournalEntryResponse(
        id=entry.id,
        user_id=entry.user_id,
        title=entry.title,
        content=entry.content,
        entry_type=entry.entry_type,
        mood=entry.mood,
        rich_content=entry.rich_content,
        ai_insights=entry.ai_insights,
        linked_entry_ids=entry.linked_entry_ids or [],
        related_module_id=entry.related_module_id,
        related_task_id=entry.related_task_id,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
        tags=tags
    )


@router.patch(
    "/entries/{entry_id}",
    response_model=JournalEntryResponse,
    summary="Update journal entry"
)
async def update_entry(
    entry_id: UUID,
    data: JournalEntryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a journal entry.
    """
    service = JournalService(db)
    entry = await service.update_entry(entry_id, current_user.id, data)
    return JournalEntryResponse.model_validate(entry)


@router.delete(
    "/entries/{entry_id}",
    response_model=dict,
    summary="Delete journal entry"
)
async def delete_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a journal entry.
    """
    service = JournalService(db)
    return await service.delete_entry(entry_id, current_user.id)


@router.get(
    "/entries/{entry_id}/reflection",
    response_model=JournalReflectionResponse,
    summary="Get AI reflection"
)
async def get_reflection(
    entry_id: UUID,
    reflection_type: str = Query("general", description="Type of reflection"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-generated reflection on a journal entry.
    """
    service = JournalService(db)
    return await service.get_reflection(entry_id, current_user.id, reflection_type)


@router.post(
    "/search",
    response_model=JournalEntryListResponse,
    summary="Search entries"
)
async def search_entries(
    search: JournalSearchRequest,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search journal entries.
    """
    service = JournalService(db)
    return await service.search_entries(current_user.id, search, pagination)


@router.get(
    "/insights",
    response_model=JournalInsightsResponse,
    summary="Get journal insights"
)
async def get_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get journal analytics and insights.
    """
    service = JournalService(db)
    return await service.get_insights(current_user.id)


# Tags
@router.get(
    "/tags",
    response_model=list[TagResponse],
    summary="Get all tags"
)
async def get_tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all available tags.
    """
    service = JournalService(db)
    tags = await service.get_tags(current_user.id)
    return [TagResponse.model_validate(t) for t in tags]


@router.post(
    "/tags",
    response_model=TagResponse,
    status_code=201,
    summary="Create tag"
)
async def create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new tag.
    """
    service = JournalService(db)
    tag = await service.create_tag(data)
    return TagResponse.model_validate(tag)
