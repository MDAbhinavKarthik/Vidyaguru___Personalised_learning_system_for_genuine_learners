"""
VidyaGuru SkillTask Management & Skill Tracking - Service Layer
"""
import math
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from redis.asyncio import Redis

from app.tasks.models import (
    SkillTask, TaskAssignment, UserSkill, SkillHistory, 
    SkillAssessment, SkillMilestone, UserMilestone,
    TaskType, TaskStatus, TaskDifficulty, SkillCategory, SkillLevel
)
from app.tasks.schemas import (
    TaskCreateRequest, TaskUpdateRequest, TaskAssignRequest,
    TaskSubmissionRequest, SkillWeights
)

logger = logging.getLogger(__name__)


# =============================================================================
# SKILL CALCULATIONS
# =============================================================================

def calculate_skill_level(xp: int) -> Tuple[float, SkillLevel, int]:
    """
    Calculate skill level from XP using logarithmic scaling.
    Returns: (level 0-100, proficiency enum, xp_to_next_level)
    """
    if xp <= 0:
        return 0.0, SkillLevel.NOVICE, 100
    
    # Logarithmic scaling: level = 10 * log2(xp/50 + 1)
    # This means:
    # 0 XP = level 0
    # 100 XP = level ~10
    # 500 XP = level ~25
    # 2000 XP = level ~50
    # 10000 XP = level ~75
    # 50000 XP = level ~100
    
    level = min(100, 10 * math.log2(xp / 50 + 1))
    
    # Determine proficiency
    if level < 20:
        proficiency = SkillLevel.NOVICE
    elif level < 40:
        proficiency = SkillLevel.BEGINNER
    elif level < 60:
        proficiency = SkillLevel.INTERMEDIATE
    elif level < 80:
        proficiency = SkillLevel.ADVANCED
    else:
        proficiency = SkillLevel.EXPERT
    
    # Calculate XP needed for next level
    next_level = min(100, level + 1)
    xp_for_next = int(50 * (2 ** (next_level / 10) - 1))
    xp_to_next = max(0, xp_for_next - xp)
    
    return round(level, 2), proficiency, xp_to_next


def calculate_task_xp(
    base_xp: int,
    score: float,
    difficulty: TaskDifficulty,
    hints_used: int,
    time_taken_minutes: int,
    estimated_minutes: int,
    first_attempt: bool
) -> Tuple[int, int]:
    """
    Calculate XP earned from a SkillTask.
    Returns: (base_xp_earned, bonus_xp)
    """
    # Difficulty multipliers
    difficulty_mult = {
        TaskDifficulty.BEGINNER: 1.0,
        TaskDifficulty.INTERMEDIATE: 1.25,
        TaskDifficulty.ADVANCED: 1.5,
        TaskDifficulty.EXPERT: 2.0
    }
    
    # Base XP scaled by score (0-100%)
    score_factor = score / 100.0
    base_earned = int(base_xp * score_factor * difficulty_mult.get(difficulty, 1.0))
    
    # Hint penalty (5% per hint)
    hint_penalty = min(0.25, hints_used * 0.05)
    base_earned = int(base_earned * (1 - hint_penalty))
    
    # Calculate bonuses
    bonus = 0
    
    # Time bonus (completed faster than estimated)
    if time_taken_minutes < estimated_minutes * 0.8:
        bonus += int(base_xp * 0.1)  # 10% bonus
    
    # First attempt bonus
    if first_attempt and score >= 70:
        bonus += int(base_xp * 0.15)  # 15% bonus
    
    # Perfect score bonus
    if score >= 95:
        bonus += int(base_xp * 0.2)  # 20% bonus
    
    return base_earned, bonus


def calculate_skill_gain(
    task_skill_weights: Dict[str, float],
    score: float,
    difficulty: TaskDifficulty
) -> Dict[str, float]:
    """
    Calculate skill gains from SkillTask completion.
    """
    # Base gain multiplier based on difficulty
    difficulty_gain = {
        TaskDifficulty.BEGINNER: 0.5,
        TaskDifficulty.INTERMEDIATE: 1.0,
        TaskDifficulty.ADVANCED: 1.5,
        TaskDifficulty.EXPERT: 2.0
    }
    
    base_mult = difficulty_gain.get(difficulty, 1.0)
    score_mult = score / 100.0
    
    gains = {}
    for skill, weight in task_skill_weights.items():
        # Each skill can gain 1-5 points based on weight, difficulty, and score
        gain = weight * base_mult * score_mult * 5
        gains[skill] = round(gain, 2)
    
    return gains


# =============================================================================
# SkillTask SERVICE
# =============================================================================

class TaskService:
    """Service for SkillTask management operations"""
    
    def __init__(self, db: AsyncSession, redis: Optional[Redis] = None):
        self.db = db
        self.redis = redis
        self.cache_ttl = 3600  # 1 hour
    
    # -------------------------------------------------------------------------
    # SkillTask CRUD
    # -------------------------------------------------------------------------
    
    async def create_task(
        self,
        data: TaskCreateRequest,
        created_by: Optional[UUID] = None
    ) -> SkillTask:
        """Create a new SkillTask"""
        SkillTask = SkillTask(
            title=data.title,
            description=data.description,
            instructions=data.instructions,
            task_type=TaskType(data.task_type.value),
            difficulty=TaskDifficulty(data.difficulty.value),
            topic=data.topic,
            concept=data.concept,
            tags=data.tags,
            estimated_minutes=data.estimated_minutes,
            prerequisites=data.prerequisites,
            skill_weights=data.skill_weights.model_dump(),
            base_xp=data.base_xp,
            content=data.content,
            evaluation_rubric=data.evaluation_rubric,
            passing_score=data.passing_score,
            created_by=created_by
        )
        
        self.db.add(SkillTask)
        await self.db.commit()
        await self.db.refresh(SkillTask)
        
        logger.info(f"Created SkillTask: {SkillTask.id} - {SkillTask.title}")
        return SkillTask
    
    async def get_task(self, task_id: UUID) -> Optional[SkillTask]:
        """Get a SkillTask by ID"""
        result = await self.db.execute(
            select(SkillTask).where(SkillTask.id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def get_tasks(
        self,
        topic: Optional[str] = None,
        task_type: Optional[TaskType] = None,
        difficulty: Optional[TaskDifficulty] = None,
        tags: Optional[List[str]] = None,
        is_active: bool = True,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[SkillTask], int]:
        """Get tasks with filtering"""
        query = select(SkillTask).where(SkillTask.is_active == is_active)
        count_query = select(func.count(SkillTask.id)).where(SkillTask.is_active == is_active)
        
        if topic:
            query = query.where(SkillTask.topic.ilike(f"%{topic}%"))
            count_query = count_query.where(SkillTask.topic.ilike(f"%{topic}%"))
        
        if task_type:
            query = query.where(SkillTask.task_type == task_type)
            count_query = count_query.where(SkillTask.task_type == task_type)
        
        if difficulty:
            query = query.where(SkillTask.difficulty == difficulty)
            count_query = count_query.where(SkillTask.difficulty == difficulty)
        
        if tags:
            query = query.where(SkillTask.tags.overlap(tags))
            count_query = count_query.where(SkillTask.tags.overlap(tags))
        
        # Get total count
        total = await self.db.scalar(count_query)
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(SkillTask.created_at.desc())
        
        result = await self.db.execute(query)
        tasks = result.scalars().all()
        
        return list(tasks), total or 0
    
    async def update_task(
        self,
        task_id: UUID,
        data: TaskUpdateRequest
    ) -> Optional[SkillTask]:
        """Update a SkillTask"""
        SkillTask = await self.get_task(task_id)
        if not SkillTask:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        if "skill_weights" in update_data and update_data["skill_weights"]:
            update_data["skill_weights"] = update_data["skill_weights"].model_dump()
        
        for field, value in update_data.items():
            if value is not None:
                setattr(SkillTask, field, value)
        
        await self.db.commit()
        await self.db.refresh(SkillTask)
        
        return SkillTask
    
    async def delete_task(self, task_id: UUID) -> bool:
        """Soft delete a SkillTask"""
        SkillTask = await self.get_task(task_id)
        if not SkillTask:
            return False
        
        SkillTask.is_active = False
        await self.db.commit()
        return True
    
    # -------------------------------------------------------------------------
    # SkillTask ASSIGNMENTS
    # -------------------------------------------------------------------------
    
    async def assign_task(
        self,
        user_id: UUID,
        data: TaskAssignRequest
    ) -> TaskAssignment:
        """Assign a SkillTask to a user"""
        # Check if already assigned
        existing = await self.db.execute(
            select(TaskAssignment).where(
                and_(
                    TaskAssignment.user_id == user_id,
                    TaskAssignment.task_id == data.task_id,
                    TaskAssignment.status.not_in([
                        TaskStatus.COMPLETED,
                        TaskStatus.FAILED,
                        TaskStatus.SKIPPED
                    ])
                )
            )
        )
        
        if existing.scalar_one_or_none():
            raise ValueError("SkillTask already assigned and in progress")
        
        assignment = TaskAssignment(
            user_id=user_id,
            task_id=data.task_id,
            session_id=data.session_id,
            max_attempts=data.max_attempts,
            status=TaskStatus.NOT_STARTED
        )
        
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        
        return assignment
    
    async def get_assignment(
        self,
        assignment_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Optional[TaskAssignment]:
        """Get a SkillTask assignment"""
        query = select(TaskAssignment).options(
            selectinload(TaskAssignment.SkillTask)
        ).where(TaskAssignment.id == assignment_id)
        
        if user_id:
            query = query.where(TaskAssignment.user_id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_assignments(
        self,
        user_id: UUID,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[TaskAssignment], int]:
        """Get user's SkillTask assignments"""
        query = select(TaskAssignment).options(
            selectinload(TaskAssignment.SkillTask)
        ).where(TaskAssignment.user_id == user_id)
        
        count_query = select(func.count(TaskAssignment.id)).where(
            TaskAssignment.user_id == user_id
        )
        
        if status:
            query = query.where(TaskAssignment.status == status)
            count_query = count_query.where(TaskAssignment.status == status)
        
        if task_type:
            query = query.join(SkillTask).where(SkillTask.task_type == task_type)
            count_query = count_query.join(SkillTask).where(SkillTask.task_type == task_type)
        
        total = await self.db.scalar(count_query)
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(
            TaskAssignment.updated_at.desc()
        )
        
        result = await self.db.execute(query)
        assignments = result.scalars().all()
        
        return list(assignments), total or 0
    
    async def start_task(
        self,
        assignment_id: UUID,
        user_id: UUID
    ) -> TaskAssignment:
        """Start working on a SkillTask"""
        assignment = await self.get_assignment(assignment_id, user_id)
        if not assignment:
            raise ValueError("Assignment not found")
        
        if assignment.status not in [TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS]:
            raise ValueError(f"Cannot start SkillTask with status: {assignment.status}")
        
        if assignment.status == TaskStatus.NOT_STARTED:
            assignment.status = TaskStatus.IN_PROGRESS
            assignment.started_at = datetime.utcnow()
            assignment.attempts += 1
        
        await self.db.commit()
        await self.db.refresh(assignment)
        
        return assignment
    
    async def submit_task(
        self,
        assignment_id: UUID,
        user_id: UUID,
        submission: TaskSubmissionRequest
    ) -> TaskAssignment:
        """Submit a SkillTask solution"""
        assignment = await self.get_assignment(assignment_id, user_id)
        if not assignment:
            raise ValueError("Assignment not found")
        
        if assignment.status != TaskStatus.IN_PROGRESS:
            raise ValueError(f"Cannot submit SkillTask with status: {assignment.status}")
        
        if assignment.attempts > assignment.max_attempts:
            raise ValueError("Maximum attempts exceeded")
        
        # Store submission
        assignment.submission = {
            "type": submission.submission_type,
            "content": submission.content,
            "attachments": submission.attachments,
            "metadata": submission.metadata,
            "submitted_at": datetime.utcnow().isoformat()
        }
        assignment.status = TaskStatus.SUBMITTED
        assignment.submitted_at = datetime.utcnow()
        
        # Calculate time spent
        if assignment.started_at:
            time_delta = datetime.utcnow() - assignment.started_at
            assignment.time_spent_seconds = int(time_delta.total_seconds())
        
        await self.db.commit()
        await self.db.refresh(assignment)
        
        return assignment
    
    async def evaluate_task(
        self,
        assignment_id: UUID,
        score: float,
        feedback: Dict[str, Any],
        skill_service: "SkillService"
    ) -> TaskAssignment:
        """Evaluate a submitted SkillTask"""
        assignment = await self.get_assignment(assignment_id)
        if not assignment:
            raise ValueError("Assignment not found")
        
        SkillTask = assignment.SkillTask
        
        # Calculate XP
        base_xp, bonus_xp = calculate_task_xp(
            base_xp=SkillTask.base_xp,
            score=score,
            difficulty=SkillTask.difficulty,
            hints_used=assignment.hints_used,
            time_taken_minutes=assignment.time_spent_seconds // 60,
            estimated_minutes=SkillTask.estimated_minutes,
            first_attempt=assignment.attempts == 1
        )
        
        # Calculate skill gains
        skill_gains = calculate_skill_gain(
            task_skill_weights=SkillTask.skill_weights,
            score=score,
            difficulty=SkillTask.difficulty
        )
        
        # Update assignment
        assignment.score = score
        assignment.feedback = feedback
        assignment.xp_earned = base_xp
        assignment.bonus_xp = bonus_xp
        assignment.skill_gains = skill_gains
        
        passed = score >= SkillTask.passing_score
        assignment.status = TaskStatus.COMPLETED if passed else TaskStatus.FAILED
        assignment.completed_at = datetime.utcnow()
        
        await self.db.commit()
        
        # Update user skills
        if passed:
            await skill_service.apply_skill_gains(
                user_id=assignment.user_id,
                skill_gains=skill_gains,
                xp_gains={cat: int(gain * 10) for cat, gain in skill_gains.items()},
                source_type="task_completion",
                source_id=assignment.id
            )
        
        await self.db.refresh(assignment)
        return assignment
    
    async def get_hint(
        self,
        assignment_id: UUID,
        user_id: UUID,
        hint_number: int
    ) -> Tuple[str, int]:
        """Get a hint for a SkillTask (with XP penalty)"""
        assignment = await self.get_assignment(assignment_id, user_id)
        if not assignment:
            raise ValueError("Assignment not found")
        
        SkillTask = assignment.SkillTask
        hints = SkillTask.content.get("hints", [])
        
        if not hints:
            raise ValueError("No hints available for this SkillTask")
        
        if hint_number > len(hints):
            raise ValueError(f"Only {len(hints)} hints available")
        
        # Track hints used
        assignment.hints_used = max(assignment.hints_used, hint_number)
        
        if hint_number <= len(assignment.hints_content or []):
            hint_content = assignment.hints_content[hint_number - 1]
        else:
            hint_content = hints[hint_number - 1]
            assignment.hints_content = (assignment.hints_content or []) + [hint_content]
        
        await self.db.commit()
        
        xp_penalty = 5 * hint_number  # Increasing penalty
        
        return hint_content, xp_penalty


# =============================================================================
# SKILL SERVICE
# =============================================================================

class SkillService:
    """Service for skill tracking operations"""
    
    def __init__(self, db: AsyncSession, redis: Optional[Redis] = None):
        self.db = db
        self.redis = redis
    
    # -------------------------------------------------------------------------
    # SKILL MANAGEMENT
    # -------------------------------------------------------------------------
    
    async def get_or_create_skill(
        self,
        user_id: UUID,
        category: SkillCategory,
        topic: Optional[str] = None
    ) -> UserSkill:
        """Get or create a user skill"""
        result = await self.db.execute(
            select(UserSkill).where(
                and_(
                    UserSkill.user_id == user_id,
                    UserSkill.category == category,
                    UserSkill.topic == topic if topic else UserSkill.topic.is_(None)
                )
            )
        )
        
        skill = result.scalar_one_or_none()
        
        if not skill:
            skill = UserSkill(
                user_id=user_id,
                category=category,
                topic=topic,
                level=0.0,
                proficiency=SkillLevel.NOVICE
            )
            self.db.add(skill)
            await self.db.commit()
            await self.db.refresh(skill)
        
        return skill
    
    async def get_user_skills(
        self,
        user_id: UUID,
        topic: Optional[str] = None
    ) -> List[UserSkill]:
        """Get all skills for a user"""
        query = select(UserSkill).where(UserSkill.user_id == user_id)
        
        if topic:
            query = query.where(UserSkill.topic == topic)
        
        result = await self.db.execute(query.order_by(UserSkill.level.desc()))
        return list(result.scalars().all())
    
    async def get_skill_summary(self, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive skill summary for a user"""
        skills = await self.get_user_skills(user_id)
        
        if not skills:
            # Initialize all skill categories
            for category in SkillCategory:
                await self.get_or_create_skill(user_id, category, None)
            skills = await self.get_user_skills(user_id)
        
        # Calculate overall level
        if skills:
            overall_level = sum(s.level for s in skills) / len(skills)
        else:
            overall_level = 0.0
        
        # Organize by category
        skills_by_category = {}
        for skill in skills:
            if skill.topic is None:  # General skills only
                skills_by_category[skill.category.value] = skill
        
        # Top and bottom skills
        sorted_skills = sorted(skills, key=lambda s: s.level, reverse=True)
        top_skills = sorted_skills[:3]
        skills_to_improve = sorted_skills[-3:] if len(sorted_skills) >= 3 else sorted_skills
        
        # Recent progress
        recent_history = await self.get_skill_history(
            user_id, 
            limit=10,
            days=7
        )
        
        return {
            "user_id": user_id,
            "overall_level": round(overall_level, 2),
            "skills": skills_by_category,
            "top_skills": top_skills,
            "skills_to_improve": skills_to_improve,
            "recent_progress": recent_history,
            "total_xp": sum(s.total_xp for s in skills),
            "total_tasks_completed": sum(s.tasks_completed for s in skills)
        }
    
    async def apply_skill_gains(
        self,
        user_id: UUID,
        skill_gains: Dict[str, float],
        xp_gains: Dict[str, int],
        source_type: str,
        source_id: Optional[UUID] = None,
        topic: Optional[str] = None
    ) -> Dict[str, UserSkill]:
        """Apply skill gains from SkillTask completion"""
        updated_skills = {}
        
        for category_str, gain in skill_gains.items():
            if gain <= 0:
                continue
            
            try:
                category = SkillCategory(category_str)
            except ValueError:
                continue
            
            skill = await self.get_or_create_skill(user_id, category, topic)
            
            previous_level = skill.level
            
            # Add XP
            xp_gain = xp_gains.get(category_str, int(gain * 10))
            skill.total_xp += xp_gain
            
            # Recalculate level
            new_level, proficiency, xp_to_next = calculate_skill_level(skill.total_xp)
            
            skill.level = new_level
            skill.proficiency = proficiency
            skill.xp_to_next_level = xp_to_next
            skill.tasks_completed += 1
            skill.last_activity = datetime.utcnow()
            
            # Update streak
            if skill.last_activity:
                days_since = (datetime.utcnow() - skill.last_activity).days
                if days_since <= 1:
                    skill.streak_days += 1
                    skill.best_streak = max(skill.best_streak, skill.streak_days)
                elif days_since > 1:
                    skill.streak_days = 1
            
            # Record history
            history = SkillHistory(
                user_id=user_id,
                skill_id=skill.id,
                source_type=source_type,
                source_id=source_id,
                previous_level=previous_level,
                new_level=new_level,
                change_amount=new_level - previous_level,
                xp_gained=xp_gain,
                description=f"Gained {round(new_level - previous_level, 2)} levels from {source_type}"
            )
            self.db.add(history)
            
            updated_skills[category_str] = skill
        
        await self.db.commit()
        
        # Check for milestones
        await self._check_milestones(user_id, updated_skills)
        
        return updated_skills
    
    async def get_skill_history(
        self,
        user_id: UUID,
        skill_id: Optional[UUID] = None,
        category: Optional[SkillCategory] = None,
        days: int = 30,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get skill change history"""
        query = select(SkillHistory).where(
            and_(
                SkillHistory.user_id == user_id,
                SkillHistory.created_at >= datetime.utcnow() - timedelta(days=days)
            )
        )
        
        if skill_id:
            query = query.where(SkillHistory.skill_id == skill_id)
        
        query = query.order_by(SkillHistory.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        history = result.scalars().all()
        
        return [
            {
                "id": str(h.id),
                "skill_id": str(h.skill_id),
                "source_type": h.source_type,
                "previous_level": h.previous_level,
                "new_level": h.new_level,
                "change_amount": h.change_amount,
                "xp_gained": h.xp_gained,
                "description": h.description,
                "created_at": h.created_at.isoformat()
            }
            for h in history
        ]
    
    # -------------------------------------------------------------------------
    # ASSESSMENTS
    # -------------------------------------------------------------------------
    
    async def create_assessment(
        self,
        user_id: UUID,
        category: SkillCategory,
        topic: Optional[str] = None,
        assessment_type: str = "periodic"
    ) -> SkillAssessment:
        """Create a new skill assessment"""
        skill = await self.get_or_create_skill(user_id, category, topic)
        
        # Generate questions based on category and level
        questions = self._generate_assessment_questions(category, skill.level, topic)
        
        assessment = SkillAssessment(
            user_id=user_id,
            category=category,
            topic=topic,
            assessment_type=assessment_type,
            questions=questions,
            level_before=skill.level
        )
        
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        
        return assessment
    
    def _generate_assessment_questions(
        self,
        category: SkillCategory,
        current_level: float,
        topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate assessment questions"""
        # In production, this would use AI or a question bank
        # For now, return placeholder structure
        num_questions = 5 if current_level < 50 else 10
        
        return [
            {
                "id": f"q{i}",
                "question": f"Assessment question {i} for {category.value}",
                "question_type": "multiple_choice",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "points": 10
            }
            for i in range(1, num_questions + 1)
        ]
    
    async def complete_assessment(
        self,
        assessment_id: UUID,
        user_id: UUID,
        responses: List[Dict[str, Any]]
    ) -> SkillAssessment:
        """Complete and score an assessment"""
        result = await self.db.execute(
            select(SkillAssessment).where(
                and_(
                    SkillAssessment.id == assessment_id,
                    SkillAssessment.user_id == user_id
                )
            )
        )
        
        assessment = result.scalar_one_or_none()
        if not assessment:
            raise ValueError("Assessment not found")
        
        # Score responses (simplified)
        total_points = sum(q["points"] for q in assessment.questions)
        earned_points = len(responses) * 10  # Placeholder scoring
        
        score = (earned_points / total_points) * 100 if total_points > 0 else 0
        
        assessment.responses = responses
        assessment.score = score
        assessment.passed = score >= 70
        assessment.completed_at = datetime.utcnow()
        
        # Update skill based on assessment
        if assessment.passed:
            skill = await self.get_or_create_skill(
                user_id, 
                assessment.category,
                assessment.topic
            )
            
            # Assessment can boost skill level
            bonus_xp = int(score * 2)  # Up to 200 XP bonus
            await self.apply_skill_gains(
                user_id=user_id,
                skill_gains={assessment.category.value: score / 20},
                xp_gains={assessment.category.value: bonus_xp},
                source_type="assessment",
                source_id=assessment.id
            )
            
            await self.db.refresh(skill)
            assessment.level_after = skill.level
        else:
            assessment.level_after = assessment.level_before
        
        assessment.recommendations = self._generate_recommendations(
            assessment.category,
            score,
            assessment.topic
        )
        
        await self.db.commit()
        await self.db.refresh(assessment)
        
        return assessment
    
    def _generate_recommendations(
        self,
        category: SkillCategory,
        score: float,
        topic: Optional[str] = None
    ) -> List[str]:
        """Generate learning recommendations based on assessment"""
        recommendations = []
        
        if score < 50:
            recommendations.append(f"Review fundamentals of {category.value}")
            recommendations.append("Complete more beginner-level tasks")
        elif score < 70:
            recommendations.append("Practice with intermediate challenges")
            recommendations.append(f"Focus on weak areas in {category.value}")
        elif score < 90:
            recommendations.append("Try advanced problems")
            recommendations.append("Consider teaching concepts to others")
        else:
            recommendations.append("Ready for expert-level challenges")
            recommendations.append("Help mentor other learners")
        
        return recommendations
    
    # -------------------------------------------------------------------------
    # MILESTONES
    # -------------------------------------------------------------------------
    
    async def _check_milestones(
        self,
        user_id: UUID,
        updated_skills: Dict[str, UserSkill]
    ) -> List[UserMilestone]:
        """Check and award any achieved milestones"""
        achieved = []
        
        # Get all milestones not yet achieved
        achieved_ids = await self.db.execute(
            select(UserMilestone.milestone_id).where(
                UserMilestone.user_id == user_id
            )
        )
        achieved_milestone_ids = [r for r in achieved_ids.scalars()]
        
        # Get available milestones
        result = await self.db.execute(
            select(SkillMilestone).where(
                and_(
                    SkillMilestone.is_active == True,
                    SkillMilestone.id.not_in(achieved_milestone_ids) if achieved_milestone_ids else True
                )
            )
        )
        
        milestones = result.scalars().all()
        
        for milestone in milestones:
            if await self._check_milestone_criteria(user_id, milestone, updated_skills):
                user_milestone = UserMilestone(
                    user_id=user_id,
                    milestone_id=milestone.id,
                    context={"triggered_by": list(updated_skills.keys())}
                )
                self.db.add(user_milestone)
                achieved.append(user_milestone)
                
                logger.info(f"User {user_id} achieved milestone: {milestone.name}")
        
        if achieved:
            await self.db.commit()
        
        return achieved
    
    async def _check_milestone_criteria(
        self,
        user_id: UUID,
        milestone: SkillMilestone,
        updated_skills: Dict[str, UserSkill]
    ) -> bool:
        """Check if user meets milestone criteria"""
        # Check level requirement
        if milestone.category and milestone.required_level > 0:
            skill = updated_skills.get(milestone.category.value)
            if not skill or skill.level < milestone.required_level:
                return False
        
        # Check tasks requirement
        if milestone.required_tasks > 0:
            total_tasks = sum(s.tasks_completed for s in updated_skills.values())
            if total_tasks < milestone.required_tasks:
                return False
        
        # Check streak requirement
        if milestone.required_streak > 0:
            max_streak = max((s.streak_days for s in updated_skills.values()), default=0)
            if max_streak < milestone.required_streak:
                return False
        
        return True
    
    async def get_user_milestones(
        self,
        user_id: UUID
    ) -> Tuple[List[UserMilestone], List[Dict[str, Any]]]:
        """Get achieved milestones and progress towards others"""
        # Get achieved
        achieved_result = await self.db.execute(
            select(UserMilestone).options(
                selectinload(UserMilestone.milestone)
            ).where(UserMilestone.user_id == user_id)
        )
        achieved = list(achieved_result.scalars().all())
        
        # Get in-progress (simplified)
        in_progress = []  # Would calculate progress towards unachieved milestones
        
        return achieved, in_progress


# =============================================================================
# ANALYTICS SERVICE
# =============================================================================

class TaskAnalyticsService:
    """Service for SkillTask and skill analytics"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_task_analytics(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get SkillTask completion analytics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total tasks
        total_result = await self.db.execute(
            select(func.count(TaskAssignment.id)).where(
                and_(
                    TaskAssignment.user_id == user_id,
                    TaskAssignment.created_at >= start_date
                )
            )
        )
        total_attempted = total_result.scalar() or 0
        
        # Completed tasks
        completed_result = await self.db.execute(
            select(func.count(TaskAssignment.id)).where(
                and_(
                    TaskAssignment.user_id == user_id,
                    TaskAssignment.status == TaskStatus.COMPLETED,
                    TaskAssignment.created_at >= start_date
                )
            )
        )
        total_completed = completed_result.scalar() or 0
        
        # Average score
        avg_result = await self.db.execute(
            select(func.avg(TaskAssignment.score)).where(
                and_(
                    TaskAssignment.user_id == user_id,
                    TaskAssignment.score.isnot(None),
                    TaskAssignment.created_at >= start_date
                )
            )
        )
        average_score = avg_result.scalar() or 0
        
        # Average time
        time_result = await self.db.execute(
            select(func.avg(TaskAssignment.time_spent_seconds)).where(
                and_(
                    TaskAssignment.user_id == user_id,
                    TaskAssignment.time_spent_seconds > 0,
                    TaskAssignment.created_at >= start_date
                )
            )
        )
        avg_time_seconds = time_result.scalar() or 0
        
        return {
            "total_tasks_attempted": total_attempted,
            "total_tasks_completed": total_completed,
            "completion_rate": (total_completed / total_attempted * 100) if total_attempted > 0 else 0,
            "average_score": round(average_score, 2),
            "average_time_minutes": round(avg_time_seconds / 60, 2),
            "tasks_by_type": {},  # Would aggregate by type
            "tasks_by_difficulty": {},  # Would aggregate by difficulty
            "recent_completions": []  # Would get recent
        }
    
    async def get_skill_analytics(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get skill development analytics"""
        skills = await self.db.execute(
            select(UserSkill).where(UserSkill.user_id == user_id)
        )
        skill_list = list(skills.scalars().all())
        
        if not skill_list:
            return {
                "skill_distribution": {},
                "strongest_skill": None,
                "weakest_skill": None,
                "total_skill_xp": 0,
                "skill_growth_rate": 0,
                "recommended_focus": []
            }
        
        # Distribution
        distribution = {s.category.value: s.level for s in skill_list if s.topic is None}
        
        # Strongest/weakest
        sorted_skills = sorted(skill_list, key=lambda s: s.level, reverse=True)
        strongest = sorted_skills[0].category if sorted_skills else None
        weakest = sorted_skills[-1].category if sorted_skills else None
        
        # Total XP
        total_xp = sum(s.total_xp for s in skill_list)
        
        # Recommended focus (skills below average)
        avg_level = sum(s.level for s in skill_list) / len(skill_list)
        recommended = [s.category for s in skill_list if s.level < avg_level]
        
        return {
            "skill_distribution": distribution,
            "strongest_skill": strongest.value if strongest else None,
            "weakest_skill": weakest.value if weakest else None,
            "total_skill_xp": total_xp,
            "skill_growth_rate": 0,  # Would calculate from history
            "recommended_focus": [r.value for r in recommended[:3]]
        }
