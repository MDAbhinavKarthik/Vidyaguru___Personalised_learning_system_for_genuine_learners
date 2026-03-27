"""
Progress Service
Progress tracking and analytics
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException, status

from app.models.progress import (
    DailyProgress, SkillLevel, Achievement, UserAchievement
)
from app.schemas.progress import (
    ProgressOverviewResponse, DailyProgressResponse,
    SkillLevelResponse, SkillRadarResponse,
    AchievementResponse, UserAchievementResponse,
    AchievementListResponse, StreakResponse,
    ActivityItem, TimelineResponse,
    ProgressAnalyticsResponse, LeaderboardResponse, LeaderboardEntry
)


class ProgressService:
    """Progress tracking service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_overview(self, user_id: UUID) -> ProgressOverviewResponse:
        """Get overall progress overview"""
        # Get total XP
        total_xp = await self.db.scalar(
            select(func.sum(DailyProgress.xp_earned))
            .where(DailyProgress.user_id == user_id)
        ) or 0
        
        # Calculate level (simple formula: level = sqrt(xp/100))
        import math
        current_level = int(math.sqrt(total_xp / 100)) + 1
        xp_for_current = (current_level - 1) ** 2 * 100
        xp_for_next = current_level ** 2 * 100
        xp_to_next_level = xp_for_next - total_xp
        
        # Get streak info
        streak_info = await self._get_streak_info(user_id)
        
        # Get total time
        total_minutes = await self.db.scalar(
            select(func.sum(DailyProgress.time_spent_minutes))
            .where(DailyProgress.user_id == user_id)
        ) or 0
        
        # Get completion counts
        modules_completed = await self.db.scalar(
            select(func.sum(DailyProgress.modules_completed))
            .where(DailyProgress.user_id == user_id)
        ) or 0
        
        tasks_completed = await self.db.scalar(
            select(func.sum(DailyProgress.tasks_completed))
            .where(DailyProgress.user_id == user_id)
        ) or 0
        
        challenges_completed = await self.db.scalar(
            select(func.sum(DailyProgress.challenges_attempted))
            .where(DailyProgress.user_id == user_id)
        ) or 0
        
        # Get achievements count
        achievements_earned = await self.db.scalar(
            select(func.count())
            .select_from(UserAchievement)
            .where(UserAchievement.user_id == user_id)
        ) or 0
        
        return ProgressOverviewResponse(
            total_xp=total_xp,
            current_level=current_level,
            xp_to_next_level=xp_to_next_level,
            current_streak=streak_info["current"],
            longest_streak=streak_info["longest"],
            total_time_spent_hours=total_minutes / 60,
            modules_completed=modules_completed,
            tasks_completed=tasks_completed,
            challenges_completed=challenges_completed,
            achievements_earned=achievements_earned,
            rank_percentile=None  # Would calculate from leaderboard
        )
    
    async def _get_streak_info(self, user_id: UUID) -> dict:
        """Get streak information"""
        today = date.today()
        
        # Get recent progress records
        result = await self.db.execute(
            select(DailyProgress)
            .where(DailyProgress.user_id == user_id)
            .order_by(DailyProgress.date.desc())
            .limit(365)
        )
        records = result.scalars().all()
        
        if not records:
            return {"current": 0, "longest": 0}
        
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        prev_date = None
        
        for record in records:
            if prev_date is None:
                # Check if today or yesterday
                if record.date == today or record.date == today - timedelta(days=1):
                    temp_streak = 1
                else:
                    break
            else:
                if prev_date - record.date == timedelta(days=1):
                    temp_streak += 1
                else:
                    break
            
            prev_date = record.date
        
        current_streak = temp_streak
        
        # Calculate longest streak (simplified)
        longest_streak = max(current_streak, await self.db.scalar(
            select(func.max(DailyProgress.current_streak))
            .where(DailyProgress.user_id == user_id)
        ) or 0)
        
        return {"current": current_streak, "longest": longest_streak}
    
    async def record_progress(
        self,
        user_id: UUID,
        xp_earned: int = 0,
        time_spent_minutes: int = 0,
        modules_completed: int = 0,
        tasks_completed: int = 0,
        challenges_attempted: int = 0,
        journal_entries: int = 0,
        mentor_messages: int = 0
    ) -> DailyProgress:
        """Record daily progress"""
        today = date.today()
        
        # Get or create daily progress
        result = await self.db.execute(
            select(DailyProgress)
            .where(
                DailyProgress.user_id == user_id,
                DailyProgress.date == today
            )
        )
        progress = result.scalar_one_or_none()
        
        if not progress:
            # Get yesterday's streak
            yesterday = today - timedelta(days=1)
            yesterday_result = await self.db.execute(
                select(DailyProgress)
                .where(
                    DailyProgress.user_id == user_id,
                    DailyProgress.date == yesterday
                )
            )
            yesterday_progress = yesterday_result.scalar_one_or_none()
            
            current_streak = 1
            if yesterday_progress and yesterday_progress.streak_maintained:
                current_streak = yesterday_progress.current_streak + 1
            
            progress = DailyProgress(
                user_id=user_id,
                date=today,
                current_streak=current_streak
            )
            self.db.add(progress)
        
        # Update metrics
        progress.xp_earned += xp_earned
        progress.time_spent_minutes += time_spent_minutes
        progress.modules_completed += modules_completed
        progress.tasks_completed += tasks_completed
        progress.challenges_attempted += challenges_attempted
        progress.journal_entries_created += journal_entries
        progress.mentor_messages_sent += mentor_messages
        progress.streak_maintained = True
        
        await self.db.commit()
        await self.db.refresh(progress)
        
        # Check for achievements
        await self._check_achievements(user_id)
        
        return progress
    
    async def get_skills(self, user_id: UUID) -> SkillRadarResponse:
        """Get skill levels for user"""
        result = await self.db.execute(
            select(SkillLevel)
            .where(SkillLevel.user_id == user_id)
            .order_by(SkillLevel.current_level.desc())
        )
        skills = result.scalars().all()
        
        if not skills:
            return SkillRadarResponse(
                skills=[],
                overall_score=0,
                strengths=[],
                areas_to_improve=[]
            )
        
        skill_responses = [SkillLevelResponse.model_validate(s) for s in skills]
        
        # Calculate overall score
        overall = sum(s.current_level for s in skills) / len(skills)
        
        # Find strengths and weaknesses
        sorted_skills = sorted(skills, key=lambda x: x.current_level, reverse=True)
        strengths = [s.skill_name for s in sorted_skills[:3] if s.current_level >= 60]
        areas_to_improve = [s.skill_name for s in sorted_skills[-3:] if s.current_level < 60]
        
        return SkillRadarResponse(
            skills=skill_responses,
            overall_score=overall,
            strengths=strengths,
            areas_to_improve=areas_to_improve
        )
    
    async def update_skill(
        self,
        user_id: UUID,
        skill_name: str,
        level_change: int,
        confidence_change: float = 0
    ) -> SkillLevel:
        """Update skill level"""
        result = await self.db.execute(
            select(SkillLevel)
            .where(
                SkillLevel.user_id == user_id,
                SkillLevel.skill_name == skill_name
            )
        )
        skill = result.scalar_one_or_none()
        
        if not skill:
            skill = SkillLevel(
                user_id=user_id,
                skill_name=skill_name,
                current_level=0,
                confidence_score=50
            )
            self.db.add(skill)
        
        # Update level
        skill.current_level = max(0, min(100, skill.current_level + level_change))
        skill.confidence_score = max(0, min(100, skill.confidence_score + confidence_change))
        skill.assessments_count += 1
        skill.last_assessed = datetime.utcnow()
        
        # Add to history
        history = skill.level_history or []
        history.append({
            "date": datetime.utcnow().isoformat(),
            "level": skill.current_level,
            "confidence": float(skill.confidence_score)
        })
        skill.level_history = history[-50:]  # Keep last 50 entries
        
        await self.db.commit()
        await self.db.refresh(skill)
        
        return skill
    
    async def get_achievements(self, user_id: UUID) -> AchievementListResponse:
        """Get user achievements"""
        # Get earned achievements
        earned_result = await self.db.execute(
            select(UserAchievement)
            .options()
            .where(UserAchievement.user_id == user_id)
        )
        earned = earned_result.scalars().all()
        earned_ids = {ua.achievement_id for ua in earned}
        
        # Get all achievements
        all_result = await self.db.execute(select(Achievement))
        all_achievements = all_result.scalars().all()
        
        # Separate earned and available
        earned_responses = []
        available_responses = []
        
        for achievement in all_achievements:
            if achievement.id in earned_ids:
                ua = next(ua for ua in earned if ua.achievement_id == achievement.id)
                earned_responses.append(UserAchievementResponse(
                    achievement=AchievementResponse.model_validate(achievement),
                    earned_at=ua.earned_at,
                    progress_snapshot=ua.progress_snapshot
                ))
            elif not achievement.is_hidden:
                available_responses.append(AchievementResponse.model_validate(achievement))
        
        return AchievementListResponse(
            earned=earned_responses,
            available=available_responses,
            total_earned=len(earned_responses),
            total_available=len(all_achievements)
        )
    
    async def _check_achievements(self, user_id: UUID) -> List[Achievement]:
        """Check and award achievements"""
        # Get all unearned achievements
        earned_result = await self.db.execute(
            select(UserAchievement.achievement_id)
            .where(UserAchievement.user_id == user_id)
        )
        earned_ids = {row[0] for row in earned_result.all()}
        
        achievements_result = await self.db.execute(
            select(Achievement)
            .where(Achievement.id.notin_(earned_ids) if earned_ids else True)
        )
        available = achievements_result.scalars().all()
        
        # Check each achievement (simplified)
        newly_earned = []
        for achievement in available:
            if await self._check_achievement_criteria(user_id, achievement):
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    earned_at=datetime.utcnow()
                )
                self.db.add(user_achievement)
                newly_earned.append(achievement)
        
        if newly_earned:
            await self.db.commit()
        
        return newly_earned
    
    async def _check_achievement_criteria(self, user_id: UUID, achievement: Achievement) -> bool:
        """Check if user meets achievement criteria"""
        criteria = achievement.criteria
        
        if criteria.get("type") == "streak":
            streak_info = await self._get_streak_info(user_id)
            return streak_info["current"] >= criteria.get("value", 0)
        
        if criteria.get("type") == "xp":
            total_xp = await self.db.scalar(
                select(func.sum(DailyProgress.xp_earned))
                .where(DailyProgress.user_id == user_id)
            ) or 0
            return total_xp >= criteria.get("value", 0)
        
        if criteria.get("type") == "modules":
            modules = await self.db.scalar(
                select(func.sum(DailyProgress.modules_completed))
                .where(DailyProgress.user_id == user_id)
            ) or 0
            return modules >= criteria.get("value", 0)
        
        return False
    
    async def get_streak(self, user_id: UUID) -> StreakResponse:
        """Get detailed streak information"""
        streak_info = await self._get_streak_info(user_id)
        
        # Get streak start date
        today = date.today()
        streak_start = today - timedelta(days=streak_info["current"] - 1) if streak_info["current"] > 0 else None
        
        # Get last activity
        last_result = await self.db.execute(
            select(DailyProgress.date)
            .where(DailyProgress.user_id == user_id)
            .order_by(DailyProgress.date.desc())
            .limit(1)
        )
        last_activity = last_result.scalar_one_or_none()
        
        # Check if at risk
        at_risk = last_activity != today if last_activity else True
        
        # Get streak history (last 30 days)
        thirty_days_ago = today - timedelta(days=30)
        history_result = await self.db.execute(
            select(DailyProgress.date, DailyProgress.xp_earned)
            .where(
                DailyProgress.user_id == user_id,
                DailyProgress.date >= thirty_days_ago
            )
            .order_by(DailyProgress.date)
        )
        history = [{"date": str(row[0]), "xp": row[1]} for row in history_result.all()]
        
        return StreakResponse(
            current_streak=streak_info["current"],
            longest_streak=streak_info["longest"],
            streak_start_date=streak_start,
            last_activity_date=last_activity,
            at_risk=at_risk,
            streak_history=history
        )
    
    async def get_timeline(self, user_id: UUID, page: int = 1, size: int = 20) -> TimelineResponse:
        """Get activity timeline"""
        offset = (page - 1) * size
        
        # Get daily progress as activities
        result = await self.db.execute(
            select(DailyProgress)
            .where(DailyProgress.user_id == user_id)
            .order_by(DailyProgress.date.desc())
            .offset(offset)
            .limit(size)
        )
        records = result.scalars().all()
        
        items = []
        for record in records:
            items.append(ActivityItem(
                id=record.id,
                activity_type="daily_progress",
                title=f"Learning activity on {record.date}",
                description=f"Earned {record.xp_earned} XP",
                xp_earned=record.xp_earned,
                timestamp=datetime.combine(record.date, datetime.min.time()),
                metadata={
                    "modules": record.modules_completed,
                    "tasks": record.tasks_completed,
                    "time_minutes": record.time_spent_minutes
                }
            ))
        
        total = await self.db.scalar(
            select(func.count())
            .select_from(DailyProgress)
            .where(DailyProgress.user_id == user_id)
        ) or 0
        
        return TimelineResponse(
            items=items,
            total=total,
            page=page,
            size=size
        )
    
    async def get_analytics(self, user_id: UUID, days: int = 30) -> ProgressAnalyticsResponse:
        """Get detailed progress analytics"""
        start_date = date.today() - timedelta(days=days)
        
        # Get daily progress
        result = await self.db.execute(
            select(DailyProgress)
            .where(
                DailyProgress.user_id == user_id,
                DailyProgress.date >= start_date
            )
            .order_by(DailyProgress.date)
        )
        daily_progress = [DailyProgressResponse.model_validate(r) for r in result.scalars().all()]
        
        # Calculate summaries
        weekly_summary = await self._calculate_weekly_summary(user_id)
        monthly_summary = await self._calculate_monthly_summary(user_id)
        
        # Calculate learning velocity
        modules_last_week = await self.db.scalar(
            select(func.sum(DailyProgress.modules_completed))
            .where(
                DailyProgress.user_id == user_id,
                DailyProgress.date >= date.today() - timedelta(days=7)
            )
        ) or 0
        learning_velocity = modules_last_week / 7
        
        # Consistency score
        days_active = len([d for d in daily_progress if d.xp_earned > 0])
        consistency_score = (days_active / days) * 100 if days > 0 else 0
        
        return ProgressAnalyticsResponse(
            daily_progress=daily_progress,
            weekly_summary=weekly_summary,
            monthly_summary=monthly_summary,
            learning_velocity=learning_velocity,
            consistency_score=consistency_score,
            peak_learning_hours=[9, 10, 14, 15, 20, 21],  # Would analyze from actual data
            skill_growth=[],
            predictions={
                "expected_completion_days": 30,
                "projected_level": 5
            }
        )
    
    async def _calculate_weekly_summary(self, user_id: UUID) -> dict:
        """Calculate weekly summary"""
        week_ago = date.today() - timedelta(days=7)
        
        result = await self.db.execute(
            select(
                func.sum(DailyProgress.xp_earned),
                func.sum(DailyProgress.time_spent_minutes),
                func.sum(DailyProgress.modules_completed),
                func.sum(DailyProgress.tasks_completed)
            )
            .where(
                DailyProgress.user_id == user_id,
                DailyProgress.date >= week_ago
            )
        )
        row = result.one()
        
        return {
            "xp_earned": row[0] or 0,
            "time_spent_minutes": row[1] or 0,
            "modules_completed": row[2] or 0,
            "tasks_completed": row[3] or 0
        }
    
    async def _calculate_monthly_summary(self, user_id: UUID) -> dict:
        """Calculate monthly summary"""
        month_ago = date.today() - timedelta(days=30)
        
        result = await self.db.execute(
            select(
                func.sum(DailyProgress.xp_earned),
                func.sum(DailyProgress.time_spent_minutes),
                func.sum(DailyProgress.modules_completed),
                func.sum(DailyProgress.tasks_completed)
            )
            .where(
                DailyProgress.user_id == user_id,
                DailyProgress.date >= month_ago
            )
        )
        row = result.one()
        
        return {
            "xp_earned": row[0] or 0,
            "time_spent_minutes": row[1] or 0,
            "modules_completed": row[2] or 0,
            "tasks_completed": row[3] or 0
        }
