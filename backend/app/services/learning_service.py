"""
Learning Service
Learning paths, modules, and content management
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.learning import (
    LearningPath, Module, ModuleContent,
    PathStatus, ModuleStatus
)
from app.models.user import User, UserProfile
from app.schemas.learning import (
    LearningPathCreate, LearningPathUpdate, LearningPathGenerate,
    ModuleCreate, ModuleUpdate,
    ModuleContentCreate, ModuleContentUpdate,
    LearningPathResponse, LearningPathDetailResponse,
    ModuleResponse, ModuleDetailResponse,
    RecommendationResponse
)
from app.dependencies import PaginationParams


class LearningService:
    """Learning management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Learning Path Methods
    async def get_learning_paths(
        self, 
        user_id: UUID, 
        pagination: PaginationParams,
        status_filter: Optional[PathStatus] = None
    ) -> dict:
        """Get user's learning paths with pagination"""
        query = select(LearningPath).where(LearningPath.user_id == user_id)
        
        if status_filter:
            query = query.where(LearningPath.status == status_filter)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)
        
        # Get paginated results
        query = query.order_by(LearningPath.updated_at.desc())
        query = query.offset(pagination.offset).limit(pagination.size)
        
        result = await self.db.execute(query)
        paths = result.scalars().all()
        
        return {
            "items": [LearningPathResponse.model_validate(p) for p in paths],
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": (total + pagination.size - 1) // pagination.size
        }
    
    async def get_learning_path(self, path_id: UUID, user_id: UUID) -> LearningPath:
        """Get learning path by ID"""
        result = await self.db.execute(
            select(LearningPath)
            .options(selectinload(LearningPath.modules))
            .where(LearningPath.id == path_id, LearningPath.user_id == user_id)
        )
        path = result.scalar_one_or_none()
        
        if not path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learning path not found"
            )
        
        return path
    
    async def create_learning_path(self, user_id: UUID, data: LearningPathCreate) -> LearningPath:
        """Create a new learning path"""
        path = LearningPath(
            user_id=user_id,
            title=data.title,
            description=data.description,
            estimated_duration_hours=data.estimated_duration_hours,
            target_completion_date=data.target_completion_date
        )
        
        self.db.add(path)
        await self.db.commit()
        await self.db.refresh(path)
        
        return path
    
    async def generate_learning_path(self, user_id: UUID, data: LearningPathGenerate) -> LearningPath:
        """Generate a personalized learning path using AI"""
        # Get user profile for personalization
        profile_result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = profile_result.scalar_one_or_none()
        
        # Create learning path
        path = LearningPath(
            user_id=user_id,
            title=f"Learning {data.topic}",
            description=f"Personalized path for mastering {data.topic}",
            status=PathStatus.ACTIVE
        )
        self.db.add(path)
        await self.db.flush()
        
        # Generate modules (simplified - in production, use AI to generate)
        modules_to_create = self._generate_curriculum(
            data.topic,
            data.target_level,
            data.weekly_hours,
            data.include_projects,
            data.focus_areas
        )
        
        total_xp = 0
        for idx, module_data in enumerate(modules_to_create):
            module = Module(
                path_id=path.id,
                title=module_data["title"],
                description=module_data["description"],
                content_type=module_data["content_type"],
                difficulty=module_data["difficulty"],
                order_index=idx,
                xp_reward=module_data["xp_reward"],
                estimated_minutes=module_data["estimated_minutes"],
                status=ModuleStatus.AVAILABLE if idx == 0 else ModuleStatus.LOCKED
            )
            total_xp += module_data["xp_reward"]
            self.db.add(module)
        
        path.total_xp = total_xp
        
        await self.db.commit()
        await self.db.refresh(path)
        
        # Load modules
        result = await self.db.execute(
            select(LearningPath)
            .options(selectinload(LearningPath.modules))
            .where(LearningPath.id == path.id)
        )
        return result.scalar_one()
    
    def _generate_curriculum(
        self,
        topic: str,
        target_level: str,
        weekly_hours: int,
        include_projects: bool,
        focus_areas: Optional[List[str]]
    ) -> List[dict]:
        """Generate curriculum modules (simplified)"""
        from app.models.learning import ContentType, Difficulty
        
        # Example curriculum structure
        modules = [
            {
                "title": f"Introduction to {topic}",
                "description": f"Learn the fundamentals of {topic}",
                "content_type": ContentType.THEORY,
                "difficulty": Difficulty.BEGINNER,
                "xp_reward": 20,
                "estimated_minutes": 30
            },
            {
                "title": f"Core Concepts of {topic}",
                "description": f"Deep dive into core concepts",
                "content_type": ContentType.THEORY,
                "difficulty": Difficulty.EASY,
                "xp_reward": 30,
                "estimated_minutes": 45
            },
            {
                "title": f"Hands-on Practice: {topic}",
                "description": f"Practice exercises for {topic}",
                "content_type": ContentType.PRACTICE,
                "difficulty": Difficulty.MEDIUM,
                "xp_reward": 40,
                "estimated_minutes": 60
            },
            {
                "title": f"Advanced {topic}",
                "description": f"Advanced topics and patterns",
                "content_type": ContentType.THEORY,
                "difficulty": Difficulty.HARD,
                "xp_reward": 50,
                "estimated_minutes": 60
            },
        ]
        
        if include_projects:
            modules.append({
                "title": f"Project: Build with {topic}",
                "description": f"Apply your knowledge in a real project",
                "content_type": ContentType.PROJECT,
                "difficulty": Difficulty.HARD,
                "xp_reward": 100,
                "estimated_minutes": 180
            })
        
        return modules
    
    async def update_learning_path(
        self, 
        path_id: UUID, 
        user_id: UUID, 
        data: LearningPathUpdate
    ) -> LearningPath:
        """Update learning path"""
        path = await self.get_learning_path(path_id, user_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(path, field, value)
        
        await self.db.commit()
        await self.db.refresh(path)
        
        return path
    
    async def delete_learning_path(self, path_id: UUID, user_id: UUID) -> dict:
        """Delete learning path"""
        path = await self.get_learning_path(path_id, user_id)
        
        await self.db.delete(path)
        await self.db.commit()
        
        return {"message": "Learning path deleted successfully"}
    
    # Module Methods
    async def get_module(self, module_id: UUID, user_id: UUID) -> Module:
        """Get module by ID"""
        result = await self.db.execute(
            select(Module)
            .options(
                selectinload(Module.contents),
                selectinload(Module.learning_path)
            )
            .where(Module.id == module_id)
        )
        module = result.scalar_one_or_none()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Verify user owns the path
        if module.learning_path.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return module
    
    async def complete_module(self, module_id: UUID, user_id: UUID) -> dict:
        """Mark module as completed"""
        module = await self.get_module(module_id, user_id)
        
        if module.status == ModuleStatus.COMPLETED:
            return {"message": "Module already completed", "xp_earned": 0}
        
        module.status = ModuleStatus.COMPLETED
        module.completed_at = datetime.utcnow()
        
        # Update path progress
        path = module.learning_path
        completed_count = await self.db.scalar(
            select(func.count())
            .select_from(Module)
            .where(Module.path_id == path.id, Module.status == ModuleStatus.COMPLETED)
        )
        total_modules = await self.db.scalar(
            select(func.count())
            .select_from(Module)
            .where(Module.path_id == path.id)
        )
        
        path.progress_percentage = (completed_count / total_modules) * 100
        path.earned_xp += module.xp_reward
        
        # Unlock next module
        next_module = await self.db.execute(
            select(Module)
            .where(
                Module.path_id == path.id,
                Module.order_index == module.order_index + 1
            )
        )
        next_mod = next_module.scalar_one_or_none()
        if next_mod:
            next_mod.status = ModuleStatus.AVAILABLE
        
        # Check if path is completed
        if completed_count == total_modules:
            path.status = PathStatus.COMPLETED
            path.completed_at = datetime.utcnow()
        
        await self.db.commit()
        
        return {
            "message": "Module completed",
            "xp_earned": module.xp_reward,
            "path_progress": path.progress_percentage,
            "next_module_id": str(next_mod.id) if next_mod else None
        }
    
    async def get_recommendations(self, user_id: UUID) -> List[RecommendationResponse]:
        """Get personalized learning recommendations"""
        # Get user's active paths
        result = await self.db.execute(
            select(Module)
            .join(LearningPath)
            .where(
                LearningPath.user_id == user_id,
                LearningPath.status == PathStatus.ACTIVE,
                Module.status.in_([ModuleStatus.AVAILABLE, ModuleStatus.IN_PROGRESS])
            )
            .limit(5)
        )
        modules = result.scalars().all()
        
        recommendations = []
        for idx, module in enumerate(modules):
            recommendations.append(RecommendationResponse(
                module_id=module.id,
                module_title=module.title,
                reason="Continue your learning journey" if module.status == ModuleStatus.IN_PROGRESS else "Ready to start",
                priority=idx + 1,
                estimated_time=module.estimated_minutes
            ))
        
        return recommendations
