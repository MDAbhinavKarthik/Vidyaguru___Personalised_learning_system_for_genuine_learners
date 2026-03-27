"""
VidyaGuru Learning Engine Service
Database persistence and business logic
"""
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from redis.asyncio import Redis

from app.learning_engine.engine import (
    LearningEngine,
    LearningSessionState,
    LearningStage,
    StageStatus,
    StageProgress,
    STAGE_CONTENT,
    STAGE_REQUIREMENTS
)

logger = logging.getLogger(__name__)


class LearningEngineService:
    """
    Service layer for the Learning Engine.
    Handles database persistence and Redis caching.
    """
    
    def __init__(
        self,
        db: Optional[AsyncSession] = None,
        redis: Optional[Redis] = None,
        cache_ttl: int = 7200  # 2 hours
    ):
        self.db = db
        self.redis = redis
        self.cache_ttl = cache_ttl
        self.engine = LearningEngine()
        
        # Redis key prefixes
        self.session_prefix = "vidyaguru:learning_session:"
        self.user_sessions_prefix = "vidyaguru:user_learning_sessions:"
    
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    async def create_session(
        self,
        user_id: str,
        topic: str,
        concept: Optional[str] = None,
        difficulty: str = "intermediate",
        experience_level: str = "intermediate",
        interests: Optional[List[str]] = None
    ) -> LearningSessionState:
        """Create a new learning session with persistence"""
        session = self.engine.create_session(
            user_id=user_id,
            topic=topic,
            concept=concept,
            difficulty=difficulty,
            experience_level=experience_level,
            interests=interests
        )
        
        # Cache session
        await self._cache_session(session)
        
        # Track user's sessions
        await self._track_user_session(user_id, session.session_id)
        
        # Persist to database
        await self._persist_session(session)
        
        logger.info(f"Created learning session {session.session_id} for user {user_id}")
        
        return session
    
    async def get_session(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> Optional[LearningSessionState]:
        """Get a session with caching"""
        # Try cache first
        session = await self._get_cached_session(session_id)
        
        if session:
            if user_id and session.user_id != user_id:
                return None
            return session
        
        # Load from database
        session = await self._load_session_from_db(session_id)
        
        if session:
            if user_id and session.user_id != user_id:
                return None
            # Re-cache
            await self._cache_session(session)
            # Restore to engine
            self.engine.sessions[session.session_id] = session
        
        return session
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10,
        include_completed: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        sessions = []
        
        # Get from engine (in-memory)
        for session in self.engine.sessions.values():
            if session.user_id == user_id:
                if include_completed or not session.is_complete:
                    sessions.append(self._session_to_dict(session))
        
        # Sort and limit
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        return sessions[:limit]
    
    async def update_session(
        self,
        session: LearningSessionState
    ) -> None:
        """Update session in cache and database"""
        session.updated_at = datetime.utcnow()
        
        # Update in engine
        self.engine.save_session(session)
        
        # Update cache
        await self._cache_session(session)
        
        # Persist changes (debounced in production)
        await self._persist_session(session)
    
    async def delete_session(
        self,
        session_id: str,
        user_id: str
    ) -> bool:
        """Delete a learning session"""
        session = await self.get_session(session_id, user_id)
        
        if not session:
            return False
        
        # Remove from engine
        if session_id in self.engine.sessions:
            del self.engine.sessions[session_id]
        
        # Remove from cache
        await self._delete_cached_session(session_id)
        
        # Remove from user's sessions
        await self._untrack_user_session(user_id, session_id)
        
        # Remove from database
        await self._delete_session_from_db(session_id)
        
        logger.info(f"Deleted learning session {session_id}")
        
        return True
    
    # =========================================================================
    # STAGE OPERATIONS
    # =========================================================================
    
    async def record_interaction(
        self,
        session_id: str,
        user_id: str,
        user_message: str,
        mentor_response: str
    ) -> Dict[str, Any]:
        """Record an interaction and return progress"""
        session = await self.get_session(session_id, user_id)
        
        if not session:
            raise ValueError("Session not found")
        
        progress = self.engine.record_interaction(session, user_message, mentor_response)
        
        await self.update_session(session)
        
        can_advance, unmet = self.engine.can_advance_stage(session)
        
        return {
            "stage": session.current_stage.value,
            "interactions": progress.interactions,
            "total_words": progress.total_words,
            "can_advance": can_advance,
            "unmet_requirements": unmet
        }
    
    async def record_submission(
        self,
        session_id: str,
        user_id: str,
        submission: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record a submission"""
        session = await self.get_session(session_id, user_id)
        
        if not session:
            raise ValueError("Session not found")
        
        progress = self.engine.record_submission(session, submission)
        
        await self.update_session(session)
        
        can_advance, unmet = self.engine.can_advance_stage(session)
        
        return {
            "submission_count": len(progress.submissions),
            "explanation_provided": progress.explanation_provided,
            "verification_passed": progress.verification_passed,
            "can_advance": can_advance,
            "unmet_requirements": unmet
        }
    
    async def mark_verification_passed(
        self,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Mark verification as passed"""
        session = await self.get_session(session_id, user_id)
        
        if not session:
            raise ValueError("Session not found")
        
        self.engine.mark_verification_passed(session)
        
        await self.update_session(session)
        
        can_advance, unmet = self.engine.can_advance_stage(session)
        
        return {
            "verification_passed": True,
            "can_advance": can_advance,
            "unmet_requirements": unmet
        }
    
    async def advance_stage(
        self,
        session_id: str,
        user_id: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """Advance to next stage"""
        session = await self.get_session(session_id, user_id)
        
        if not session:
            raise ValueError("Session not found")
        
        success, message, new_stage = self.engine.advance_to_next_stage(session, force)
        
        if success:
            await self.update_session(session)
        
        return {
            "success": success,
            "message": message,
            "new_stage": new_stage.value if new_stage else None,
            "xp_earned": session.stage_progress[
                self.engine.STAGE_ORDER[
                    self.engine.STAGE_ORDER.index(new_stage) - 1
                ].value
            ].xp_earned if new_stage and self.engine.STAGE_ORDER.index(new_stage) > 0 else 0
        }
    
    async def complete_session(
        self,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Complete a learning session"""
        session = await self.get_session(session_id, user_id)
        
        if not session:
            raise ValueError("Session not found")
        
        result = self.engine.complete_session(session)
        
        if result["success"]:
            await self.update_session(session)
            
            # Record completion analytics
            await self._record_completion(session, result["summary"])
        
        return result
    
    # =========================================================================
    # ANALYTICS
    # =========================================================================
    
    async def get_user_learning_stats(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get learning statistics for a user"""
        sessions = await self.get_user_sessions(user_id, limit=100, include_completed=True)
        
        total_xp = sum(s.get("total_xp", 0) for s in sessions)
        completed = sum(1 for s in sessions if s.get("is_complete"))
        total_time = sum(s.get("total_time_seconds", 0) for s in sessions)
        
        topics_covered = list(set(s.get("topic") for s in sessions))
        
        stage_completions = {}
        for session in sessions:
            for stage, progress in session.get("stage_progress", {}).items():
                if progress.get("status") == "completed":
                    stage_completions[stage] = stage_completions.get(stage, 0) + 1
        
        return {
            "user_id": user_id,
            "total_sessions": len(sessions),
            "completed_sessions": completed,
            "total_xp": total_xp,
            "total_learning_minutes": total_time // 60,
            "topics_covered": topics_covered,
            "stage_completions": stage_completions,
            "avg_completion_rate": int((completed / max(len(sessions), 1)) * 100)
        }
    
    # =========================================================================
    # CACHING
    # =========================================================================
    
    async def _cache_session(
        self,
        session: LearningSessionState
    ) -> None:
        """Cache session to Redis"""
        if not self.redis:
            return
        
        key = f"{self.session_prefix}{session.session_id}"
        data = session.model_dump_json()
        
        await self.redis.setex(key, self.cache_ttl, data)
    
    async def _get_cached_session(
        self,
        session_id: str
    ) -> Optional[LearningSessionState]:
        """Get session from cache"""
        if not self.redis:
            # Fall back to in-memory
            return self.engine.get_session(session_id)
        
        key = f"{self.session_prefix}{session_id}"
        data = await self.redis.get(key)
        
        if data:
            return LearningSessionState.model_validate_json(data)
        
        # Try in-memory
        return self.engine.get_session(session_id)
    
    async def _delete_cached_session(
        self,
        session_id: str
    ) -> None:
        """Delete session from cache"""
        if not self.redis:
            return
        
        key = f"{self.session_prefix}{session_id}"
        await self.redis.delete(key)
    
    async def _track_user_session(
        self,
        user_id: str,
        session_id: str
    ) -> None:
        """Track user's session"""
        if not self.redis:
            return
        
        key = f"{self.user_sessions_prefix}{user_id}"
        await self.redis.sadd(key, session_id)
        await self.redis.expire(key, 86400 * 30)  # 30 days
    
    async def _untrack_user_session(
        self,
        user_id: str,
        session_id: str
    ) -> None:
        """Untrack user's session"""
        if not self.redis:
            return
        
        key = f"{self.user_sessions_prefix}{user_id}"
        await self.redis.srem(key, session_id)
    
    # =========================================================================
    # DATABASE PERSISTENCE
    # =========================================================================
    
    async def _persist_session(
        self,
        session: LearningSessionState
    ) -> None:
        """Persist session to database"""
        if not self.db:
            logger.debug(f"No database connection, skipping persistence for {session.session_id}")
            return
        
        # In production, this would use the SQLAlchemy models
        # For now, just log
        logger.debug(f"Would persist session {session.session_id} to database")
    
    async def _load_session_from_db(
        self,
        session_id: str
    ) -> Optional[LearningSessionState]:
        """Load session from database"""
        if not self.db:
            return None
        
        # In production, this would query the database
        logger.debug(f"Would load session {session_id} from database")
        return None
    
    async def _delete_session_from_db(
        self,
        session_id: str
    ) -> None:
        """Delete session from database"""
        if not self.db:
            return
        
        logger.debug(f"Would delete session {session_id} from database")
    
    async def _record_completion(
        self,
        session: LearningSessionState,
        summary: Dict[str, Any]
    ) -> None:
        """Record session completion for analytics"""
        if not self.db:
            return
        
        logger.info(
            f"Session {session.session_id} completed: "
            f"XP={summary.get('total_xp', 0)}, "
            f"Time={summary.get('total_time_minutes', 0)}min"
        )
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _session_to_dict(
        self,
        session: LearningSessionState
    ) -> Dict[str, Any]:
        """Convert session to dictionary"""
        progress = self.engine.get_session_progress(session)
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "topic": session.topic,
            "concept": session.concept,
            "difficulty": session.difficulty,
            "current_stage": session.current_stage.value,
            "overall_progress_percent": progress["overall_progress_percent"],
            "total_xp": session.total_xp,
            "total_time_seconds": session.total_time_seconds,
            "is_complete": session.is_complete,
            "is_paused": session.is_paused,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "stage_progress": {
                k: {
                    "status": v.status.value,
                    "interactions": v.interactions,
                    "xp_earned": v.xp_earned
                }
                for k, v in session.stage_progress.items()
            }
        }


# =============================================================================
# SINGLETON SERVICE
# =============================================================================

learning_service = LearningEngineService()
