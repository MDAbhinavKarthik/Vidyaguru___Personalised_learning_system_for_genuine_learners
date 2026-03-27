"""
Journal Service
Idea journal and note management
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.journal import JournalEntry, Tag, EntryTag, EntryType
from app.schemas.journal import (
    JournalEntryCreate, JournalEntryUpdate,
    TagCreate, TagResponse,
    JournalEntryResponse, JournalEntryListResponse,
    JournalInsightsResponse, JournalSearchRequest,
    JournalReflectionResponse
)
from app.dependencies import PaginationParams


class JournalService:
    """Journal management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_entries(
        self,
        user_id: UUID,
        pagination: PaginationParams,
        entry_type: Optional[EntryType] = None,
        tag_ids: Optional[List[UUID]] = None
    ) -> JournalEntryListResponse:
        """Get journal entries with pagination"""
        query = select(JournalEntry).where(JournalEntry.user_id == user_id)
        
        if entry_type:
            query = query.where(JournalEntry.entry_type == entry_type)
        
        if tag_ids:
            query = query.join(EntryTag).where(EntryTag.tag_id.in_(tag_ids))
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)
        
        # Get paginated results
        query = query.options(selectinload(JournalEntry.entry_tags).selectinload(EntryTag.tag))
        query = query.order_by(JournalEntry.created_at.desc())
        query = query.offset(pagination.offset).limit(pagination.size)
        
        result = await self.db.execute(query)
        entries = result.scalars().unique().all()
        
        # Convert to response
        entry_responses = []
        for entry in entries:
            tags = [TagResponse.model_validate(et.tag) for et in entry.entry_tags]
            response = JournalEntryResponse(
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
            entry_responses.append(response)
        
        return JournalEntryListResponse(
            items=entry_responses,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
    
    async def get_entry(self, entry_id: UUID, user_id: UUID) -> JournalEntry:
        """Get entry by ID"""
        result = await self.db.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.entry_tags).selectinload(EntryTag.tag))
            .where(JournalEntry.id == entry_id, JournalEntry.user_id == user_id)
        )
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        
        return entry
    
    async def create_entry(self, user_id: UUID, data: JournalEntryCreate) -> JournalEntry:
        """Create a new journal entry"""
        entry = JournalEntry(
            user_id=user_id,
            title=data.title,
            content=data.content,
            entry_type=data.entry_type,
            mood=data.mood,
            rich_content=data.rich_content,
            linked_entry_ids=data.linked_entry_ids or [],
            related_module_id=data.related_module_id,
            related_task_id=data.related_task_id
        )
        
        self.db.add(entry)
        await self.db.flush()
        
        # Add tags
        if data.tag_ids:
            for tag_id in data.tag_ids:
                entry_tag = EntryTag(entry_id=entry.id, tag_id=tag_id)
                self.db.add(entry_tag)
        
        # Generate AI insights
        entry.ai_insights = await self._generate_insights(entry)
        
        await self.db.commit()
        await self.db.refresh(entry)
        
        return entry
    
    async def update_entry(self, entry_id: UUID, user_id: UUID, data: JournalEntryUpdate) -> JournalEntry:
        """Update journal entry"""
        entry = await self.get_entry(entry_id, user_id)
        
        update_data = data.model_dump(exclude_unset=True, exclude={"tag_ids"})
        for field, value in update_data.items():
            setattr(entry, field, value)
        
        # Update tags if provided
        if data.tag_ids is not None:
            # Remove existing tags
            await self.db.execute(
                select(EntryTag).where(EntryTag.entry_id == entry_id)
            )
            for et in entry.entry_tags:
                await self.db.delete(et)
            
            # Add new tags
            for tag_id in data.tag_ids:
                entry_tag = EntryTag(entry_id=entry.id, tag_id=tag_id)
                self.db.add(entry_tag)
        
        await self.db.commit()
        await self.db.refresh(entry)
        
        return entry
    
    async def delete_entry(self, entry_id: UUID, user_id: UUID) -> dict:
        """Delete journal entry"""
        entry = await self.get_entry(entry_id, user_id)
        
        await self.db.delete(entry)
        await self.db.commit()
        
        return {"message": "Entry deleted successfully"}
    
    async def _generate_insights(self, entry: JournalEntry) -> dict:
        """Generate AI insights for entry"""
        # Simplified - in production, use LLM
        return {
            "summary": f"Entry about {entry.entry_type.value}",
            "keywords": ["learning", "progress"],
            "sentiment": "positive",
            "suggestions": ["Consider connecting this to related topics"]
        }
    
    # Tag Methods
    async def get_tags(self, user_id: UUID) -> List[Tag]:
        """Get all tags"""
        result = await self.db.execute(select(Tag))
        return result.scalars().all()
    
    async def create_tag(self, data: TagCreate) -> Tag:
        """Create a new tag"""
        # Check if tag exists
        existing = await self.db.execute(
            select(Tag).where(Tag.name == data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag already exists"
            )
        
        tag = Tag(name=data.name, color=data.color)
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        
        return tag
    
    async def get_reflection(self, entry_id: UUID, user_id: UUID, reflection_type: str) -> JournalReflectionResponse:
        """Generate AI reflection on entry"""
        entry = await self.get_entry(entry_id, user_id)
        
        # Generate reflection (simplified)
        reflection = f"""
## Reflection on your entry

Your {entry.entry_type.value} entry shows great progress in your learning journey.

### Key Observations:
- You're actively documenting your learning
- This shows commitment to genuine understanding

### Suggested Actions:
1. Review this concept again in 2-3 days
2. Try to explain this to someone else
3. Connect this to previous learnings
"""
        
        return JournalReflectionResponse(
            entry_id=entry.id,
            reflection=reflection,
            suggested_connections=[],
            action_items=[
                "Review in 2-3 days",
                "Practice with examples",
                "Connect to related concepts"
            ],
            insights={"sentiment": "positive", "growth_area": "consistency"}
        )
    
    async def get_insights(self, user_id: UUID) -> JournalInsightsResponse:
        """Get journal insights summary"""
        # Count entries by type
        type_counts = {}
        for entry_type in EntryType:
            count = await self.db.scalar(
                select(func.count())
                .select_from(JournalEntry)
                .where(
                    JournalEntry.user_id == user_id,
                    JournalEntry.entry_type == entry_type
                )
            )
            type_counts[entry_type.value] = count
        
        total = sum(type_counts.values())
        
        # Get mood distribution
        from app.models.journal import Mood
        mood_counts = {}
        for mood in Mood:
            count = await self.db.scalar(
                select(func.count())
                .select_from(JournalEntry)
                .where(
                    JournalEntry.user_id == user_id,
                    JournalEntry.mood == mood
                )
            )
            mood_counts[mood.value] = count
        
        # Get top tags
        top_tags_result = await self.db.execute(
            select(Tag, func.count(EntryTag.entry_id).label("count"))
            .join(EntryTag)
            .join(JournalEntry)
            .where(JournalEntry.user_id == user_id)
            .group_by(Tag.id)
            .order_by(func.count(EntryTag.entry_id).desc())
            .limit(5)
        )
        top_tags = [TagResponse.model_validate(row[0]) for row in top_tags_result.all()]
        
        # Get weekly activity
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_activity = []
        for i in range(7):
            day = (datetime.utcnow() - timedelta(days=i)).date()
            count = await self.db.scalar(
                select(func.count())
                .select_from(JournalEntry)
                .where(
                    JournalEntry.user_id == user_id,
                    func.date(JournalEntry.created_at) == day
                )
            )
            weekly_activity.append({"date": str(day), "count": count})
        
        return JournalInsightsResponse(
            total_entries=total,
            entries_by_type=type_counts,
            mood_distribution=mood_counts,
            top_tags=top_tags,
            weekly_activity=weekly_activity,
            ai_summary="You've been consistently journaling your learning journey. Great job!" if total > 5 else "Start journaling more to get personalized insights.",
            patterns_detected=["Regular note-taking", "Active questioning"] if total > 10 else []
        )
    
    async def search_entries(self, user_id: UUID, search: JournalSearchRequest, pagination: PaginationParams) -> JournalEntryListResponse:
        """Search journal entries"""
        query = select(JournalEntry).where(JournalEntry.user_id == user_id)
        
        # Text search
        query = query.where(
            or_(
                JournalEntry.title.ilike(f"%{search.query}%"),
                JournalEntry.content.ilike(f"%{search.query}%")
            )
        )
        
        if search.entry_types:
            query = query.where(JournalEntry.entry_type.in_(search.entry_types))
        
        if search.mood:
            query = query.where(JournalEntry.mood == search.mood)
        
        if search.date_from:
            query = query.where(JournalEntry.created_at >= search.date_from)
        
        if search.date_to:
            query = query.where(JournalEntry.created_at <= search.date_to)
        
        # Count and paginate
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)
        
        query = query.order_by(JournalEntry.created_at.desc())
        query = query.offset(pagination.offset).limit(pagination.size)
        
        result = await self.db.execute(query)
        entries = result.scalars().all()
        
        return JournalEntryListResponse(
            items=[JournalEntryResponse.model_validate(e) for e in entries],
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
