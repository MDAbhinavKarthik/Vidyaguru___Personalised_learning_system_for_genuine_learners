"""
VidyaGuru Session Manager
Handles session persistence, retrieval, and state management
"""
import json
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload
from redis.asyncio import Redis

from app.mentor.engine import (
    LearningSession,
    Message,
    MessageRole,
    MentorResponse,
    LearningPhase,
    MentorPersonality,
    LearnerContext
)

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages learning session lifecycle:
    - Session creation and initialization
    - Persistence to database and Redis cache
    - Session recovery and state management
    - Analytics and progress tracking
    """
    
    def __init__(
        self,
        db: Optional[AsyncSession] = None,
        redis: Optional[Redis] = None,
        cache_ttl: int = 3600  # 1 hour cache TTL
    ):
        self.db = db
        self.redis = redis
        self.cache_ttl = cache_ttl
        
        # Session prefix for Redis
        self.cache_prefix = "vidyaguru:session:"
        self.active_sessions_key = "vidyaguru:active_sessions"
    
    # -------------------------------------------------------------------------
    # SESSION LIFECYCLE
    # -------------------------------------------------------------------------
    
    async def create_session(
        self,
        user_id: str,
        topic: str,
        concept: Optional[str] = None,
        personality: MentorPersonality = MentorPersonality.SOCRATIC,
        learner_context: Optional[LearnerContext] = None
    ) -> LearningSession:
        """Create a new learning session"""
        import uuid
        
        session_id = str(uuid.uuid4())
        
        session = LearningSession(
            session_id=session_id,
            user_id=user_id,
            topic=topic,
            current_phase=LearningPhase.TOPIC_INTRODUCTION,
            personality=personality,
            learner_context=learner_context,
            metadata={
                "current_concept": concept or topic,
                "created_via": "session_manager"
            }
        )
        
        # Persist to cache
        await self._cache_session(session)
        
        # Track active session
        await self._track_active_session(user_id, session_id)
        
        logger.info(f"Created session {session_id} for user {user_id} on topic '{topic}'")
        
        return session
    
    async def get_session(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> Optional[LearningSession]:
        """Retrieve a session by ID"""
        # Try cache first
        session = await self._get_cached_session(session_id)
        
        if session:
            # Verify user ownership if user_id provided
            if user_id and session.user_id != user_id:
                logger.warning(f"User {user_id} attempted to access session {session_id}")
                return None
            return session
        
        # If not in cache, try database
        if self.db:
            session = await self._load_session_from_db(session_id)
            if session:
                # Re-cache for faster access
                await self._cache_session(session)
                return session
        
        return None
    
    async def update_session(
        self,
        session: LearningSession,
        user_message: str,
        assistant_response: MentorResponse
    ) -> LearningSession:
        """Update session with new interaction"""
        # Add messages
        session.messages.append(Message(
            role=MessageRole.USER,
            content=user_message,
            phase=session.current_phase
        ))
        session.messages.append(Message(
            role=MessageRole.ASSISTANT,
            content=assistant_response.content,
            phase=session.current_phase
        ))
        
        # Update XP
        session.xp_earned += assistant_response.xp_awarded
        
        # Update phase if completed
        if assistant_response.phase_complete:
            session.phase_progress[session.current_phase.value] = True
            if assistant_response.next_phase:
                session.current_phase = assistant_response.next_phase
        
        # Update last activity
        session.last_activity = datetime.utcnow()
        
        # Persist updates
        await self._cache_session(session)
        
        # Periodically persist to DB (every 5 messages)
        if len(session.messages) % 10 == 0:
            await self._persist_session_to_db(session)
        
        return session
    
    async def end_session(
        self,
        session_id: str,
        user_id: str,
        summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """End a learning session and generate summary"""
        session = await self.get_session(session_id, user_id)
        
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Calculate statistics
        stats = self._calculate_session_stats(session)
        
        # Add summary to metadata
        session.metadata["session_summary"] = summary or self._generate_auto_summary(session)
        session.metadata["ended_at"] = datetime.utcnow().isoformat()
        session.metadata["final_stats"] = stats
        
        # Persist final state to DB
        await self._persist_session_to_db(session)
        
        # Remove from active sessions
        await self._untrack_active_session(user_id, session_id)
        
        # Keep in cache for a while (for review)
        await self._cache_session(session, ttl=self.cache_ttl * 2)
        
        logger.info(f"Ended session {session_id} for user {user_id}")
        
        return {
            "session_id": session_id,
            "topic": session.topic,
            "duration_minutes": stats["duration_minutes"],
            "phases_completed": stats["phases_completed"],
            "xp_earned": session.xp_earned,
            "message_count": len(session.messages),
            "summary": session.metadata.get("session_summary")
        }
    
    # -------------------------------------------------------------------------
    # SESSION QUERIES
    # -------------------------------------------------------------------------
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10,
        include_active: bool = True,
        include_completed: bool = True
    ) -> List[Dict[str, Any]]:
        """Get a user's recent sessions"""
        sessions = []
        
        # Get active sessions from tracking
        if include_active:
            active_ids = await self._get_active_session_ids(user_id)
            for session_id in active_ids:
                session = await self.get_session(session_id, user_id)
                if session:
                    sessions.append(self._session_to_summary(session, is_active=True))
        
        # Get completed sessions from DB
        if include_completed and self.db:
            db_sessions = await self._query_user_sessions_from_db(
                user_id,
                limit=limit,
                exclude_ids=[s["session_id"] for s in sessions]
            )
            sessions.extend(db_sessions)
        
        # Sort by last activity
        sessions.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
        
        return sessions[:limit]
    
    async def get_active_session(
        self,
        user_id: str,
        topic: Optional[str] = None
    ) -> Optional[LearningSession]:
        """Get user's current active session, optionally filtered by topic"""
        active_ids = await self._get_active_session_ids(user_id)
        
        for session_id in active_ids:
            session = await self.get_session(session_id, user_id)
            if session:
                if topic is None or session.topic.lower() == topic.lower():
                    return session
        
        return None
    
    async def resume_or_create_session(
        self,
        user_id: str,
        topic: str,
        personality: MentorPersonality = MentorPersonality.SOCRATIC,
        learner_context: Optional[LearnerContext] = None
    ) -> tuple[LearningSession, bool]:
        """Resume existing session or create new one"""
        # Check for existing active session on same topic
        existing = await self.get_active_session(user_id, topic)
        
        if existing:
            # Check if session is not too old (24 hours)
            age = datetime.utcnow() - existing.started_at
            if age < timedelta(hours=24):
                logger.info(f"Resuming session {existing.session_id} for user {user_id}")
                return existing, True  # True = resumed
        
        # Create new session
        new_session = await self.create_session(
            user_id=user_id,
            topic=topic,
            personality=personality,
            learner_context=learner_context
        )
        
        return new_session, False  # False = newly created
    
    # -------------------------------------------------------------------------
    # ANALYTICS AND PROGRESS
    # -------------------------------------------------------------------------
    
    async def get_session_analytics(
        self,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Get detailed analytics for a session"""
        session = await self.get_session(session_id, user_id)
        
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        stats = self._calculate_session_stats(session)
        
        # Message analysis
        user_messages = [m for m in session.messages if m.role == MessageRole.USER]
        assistant_messages = [m for m in session.messages if m.role == MessageRole.ASSISTANT]
        
        return {
            "session_id": session_id,
            "topic": session.topic,
            "current_phase": session.current_phase.value,
            "phases_completed": list(session.phase_progress.keys()),
            "stats": stats,
            "message_analysis": {
                "total_messages": len(session.messages),
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "avg_user_message_length": sum(len(m.content) for m in user_messages) / max(len(user_messages), 1),
                "avg_assistant_message_length": sum(len(m.content) for m in assistant_messages) / max(len(assistant_messages), 1)
            },
            "phase_timestamps": self._get_phase_timestamps(session),
            "engagement_score": self._calculate_engagement_score(session)
        }
    
    async def get_user_learning_progress(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get aggregated learning progress for a user"""
        sessions = await self.get_user_sessions(
            user_id,
            limit=100,
            include_active=True,
            include_completed=True
        )
        
        # Filter by date
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_sessions = [
            s for s in sessions
            if datetime.fromisoformat(s.get("started_at", "2000-01-01")) > cutoff
        ]
        
        # Aggregate stats
        total_xp = sum(s.get("xp_earned", 0) for s in recent_sessions)
        total_time = sum(s.get("duration_minutes", 0) for s in recent_sessions)
        topics_covered = list(set(s.get("topic") for s in recent_sessions))
        phases_distribution = {}
        
        for session in recent_sessions:
            for phase in session.get("phases_completed", []):
                phases_distribution[phase] = phases_distribution.get(phase, 0) + 1
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_sessions": len(recent_sessions),
            "total_xp_earned": total_xp,
            "total_learning_minutes": total_time,
            "topics_covered": topics_covered,
            "phases_distribution": phases_distribution,
            "sessions": recent_sessions
        }
    
    # -------------------------------------------------------------------------
    # CACHING LAYER
    # -------------------------------------------------------------------------
    
    async def _cache_session(
        self,
        session: LearningSession,
        ttl: Optional[int] = None
    ) -> None:
        """Cache session to Redis"""
        if not self.redis:
            return
        
        key = f"{self.cache_prefix}{session.session_id}"
        data = session.model_dump_json()
        
        await self.redis.setex(
            key,
            ttl or self.cache_ttl,
            data
        )
    
    async def _get_cached_session(
        self,
        session_id: str
    ) -> Optional[LearningSession]:
        """Get session from Redis cache"""
        if not self.redis:
            return None
        
        key = f"{self.cache_prefix}{session_id}"
        data = await self.redis.get(key)
        
        if data:
            return LearningSession.model_validate_json(data)
        
        return None
    
    async def _track_active_session(
        self,
        user_id: str,
        session_id: str
    ) -> None:
        """Track an active session for a user"""
        if not self.redis:
            return
        
        key = f"{self.active_sessions_key}:{user_id}"
        await self.redis.sadd(key, session_id)
        await self.redis.expire(key, 86400 * 7)  # 7 days
    
    async def _untrack_active_session(
        self,
        user_id: str,
        session_id: str
    ) -> None:
        """Remove session from active tracking"""
        if not self.redis:
            return
        
        key = f"{self.active_sessions_key}:{user_id}"
        await self.redis.srem(key, session_id)
    
    async def _get_active_session_ids(
        self,
        user_id: str
    ) -> List[str]:
        """Get all active session IDs for a user"""
        if not self.redis:
            return []
        
        key = f"{self.active_sessions_key}:{user_id}"
        session_ids = await self.redis.smembers(key)
        
        return [sid.decode() if isinstance(sid, bytes) else sid for sid in session_ids]
    
    # -------------------------------------------------------------------------
    # DATABASE PERSISTENCE
    # -------------------------------------------------------------------------
    
    async def _persist_session_to_db(
        self,
        session: LearningSession
    ) -> None:
        """Persist session to database"""
        if not self.db:
            return
        
        # This would integrate with the existing database models
        # For now, logging the intent
        logger.info(f"Persisting session {session.session_id} to database")
        
        # Example SQL would be:
        # INSERT INTO mentor_conversations (...)
        # VALUES (...)
        # ON CONFLICT (id) DO UPDATE SET ...
    
    async def _load_session_from_db(
        self,
        session_id: str
    ) -> Optional[LearningSession]:
        """Load session from database"""
        if not self.db:
            return None
        
        logger.info(f"Loading session {session_id} from database")
        
        # This would query the mentor_conversations table
        # and reconstruct the LearningSession object
        return None
    
    async def _query_user_sessions_from_db(
        self,
        user_id: str,
        limit: int = 10,
        exclude_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Query user's sessions from database"""
        if not self.db:
            return []
        
        # This would query the mentor_conversations table
        # filtered by user_id and excluding active sessions
        return []
    
    # -------------------------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------------------------
    
    def _calculate_session_stats(
        self,
        session: LearningSession
    ) -> Dict[str, Any]:
        """Calculate statistics for a session"""
        duration = session.last_activity - session.started_at
        
        return {
            "duration_minutes": int(duration.total_seconds() / 60),
            "phases_completed": len(session.phase_progress),
            "total_phases": 8,
            "xp_earned": session.xp_earned,
            "message_count": len(session.messages),
            "completion_percentage": int(len(session.phase_progress) / 8 * 100)
        }
    
    def _generate_auto_summary(
        self,
        session: LearningSession
    ) -> str:
        """Generate automatic session summary"""
        phases_done = len(session.phase_progress)
        duration = session.last_activity - session.started_at
        mins = int(duration.total_seconds() / 60)
        
        return (
            f"Learned about '{session.topic}' for {mins} minutes. "
            f"Completed {phases_done}/8 phases and earned {session.xp_earned} XP."
        )
    
    def _session_to_summary(
        self,
        session: LearningSession,
        is_active: bool = False
    ) -> Dict[str, Any]:
        """Convert session to summary dict"""
        return {
            "session_id": session.session_id,
            "topic": session.topic,
            "current_phase": session.current_phase.value,
            "phases_completed": list(session.phase_progress.keys()),
            "xp_earned": session.xp_earned,
            "message_count": len(session.messages),
            "started_at": session.started_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "is_active": is_active,
            "duration_minutes": int((session.last_activity - session.started_at).total_seconds() / 60)
        }
    
    def _get_phase_timestamps(
        self,
        session: LearningSession
    ) -> Dict[str, str]:
        """Get timestamps for when each phase was reached"""
        timestamps = {}
        
        for msg in session.messages:
            if msg.phase and msg.phase.value not in timestamps:
                timestamps[msg.phase.value] = msg.timestamp.isoformat()
        
        return timestamps
    
    def _calculate_engagement_score(
        self,
        session: LearningSession
    ) -> float:
        """Calculate an engagement score (0-100)"""
        user_messages = [m for m in session.messages if m.role == MessageRole.USER]
        
        if not user_messages:
            return 0.0
        
        # Factors:
        # 1. Message length (longer = more engaged)
        avg_length = sum(len(m.content) for m in user_messages) / len(user_messages)
        length_score = min(avg_length / 200, 1.0) * 25  # Max 25 points
        
        # 2. Number of interactions
        interaction_score = min(len(user_messages) / 20, 1.0) * 25  # Max 25 points
        
        # 3. Phase progression
        phase_score = (len(session.phase_progress) / 8) * 25  # Max 25 points
        
        # 4. Session duration
        duration = session.last_activity - session.started_at
        duration_mins = duration.total_seconds() / 60
        duration_score = min(duration_mins / 30, 1.0) * 25  # Max 25 points
        
        return round(length_score + interaction_score + phase_score + duration_score, 1)


# =============================================================================
# SESSION STATE MACHINE
# =============================================================================

class PhaseStateMachine:
    """
    Manages phase transitions and validates state changes
    """
    
    # Valid phase transitions
    TRANSITIONS = {
        LearningPhase.TOPIC_INTRODUCTION: [LearningPhase.CONCEPT_EXPLANATION],
        LearningPhase.CONCEPT_EXPLANATION: [
            LearningPhase.REAL_WORLD_EXAMPLES,
            LearningPhase.PRACTICAL_TASK  # Can skip if advanced
        ],
        LearningPhase.REAL_WORLD_EXAMPLES: [
            LearningPhase.ANCIENT_KNOWLEDGE,
            LearningPhase.PRACTICAL_TASK
        ],
        LearningPhase.ANCIENT_KNOWLEDGE: [LearningPhase.PRACTICAL_TASK],
        LearningPhase.PRACTICAL_TASK: [
            LearningPhase.COMMUNICATION_EXERCISE,
            LearningPhase.INDUSTRY_CHALLENGE
        ],
        LearningPhase.COMMUNICATION_EXERCISE: [
            LearningPhase.INDUSTRY_CHALLENGE,
            LearningPhase.REFLECTION
        ],
        LearningPhase.INDUSTRY_CHALLENGE: [LearningPhase.REFLECTION],
        LearningPhase.REFLECTION: []  # Terminal state
    }
    
    # Minimum messages per phase before transition
    MIN_MESSAGES = {
        LearningPhase.TOPIC_INTRODUCTION: 2,
        LearningPhase.CONCEPT_EXPLANATION: 4,
        LearningPhase.REAL_WORLD_EXAMPLES: 2,
        LearningPhase.ANCIENT_KNOWLEDGE: 1,
        LearningPhase.PRACTICAL_TASK: 6,
        LearningPhase.COMMUNICATION_EXERCISE: 4,
        LearningPhase.INDUSTRY_CHALLENGE: 4,
        LearningPhase.REFLECTION: 2
    }
    
    @classmethod
    def can_transition(
        cls,
        from_phase: LearningPhase,
        to_phase: LearningPhase,
        session: LearningSession
    ) -> tuple[bool, str]:
        """Check if a phase transition is valid"""
        # Check if transition is allowed
        allowed_targets = cls.TRANSITIONS.get(from_phase, [])
        if to_phase not in allowed_targets:
            return False, f"Cannot transition from {from_phase.value} to {to_phase.value}"
        
        # Check minimum messages
        phase_messages = [
            m for m in session.messages
            if m.phase == from_phase
        ]
        min_required = cls.MIN_MESSAGES.get(from_phase, 2)
        
        if len(phase_messages) < min_required:
            return False, f"Need at least {min_required} messages in {from_phase.value}"
        
        return True, "Transition allowed"
    
    @classmethod
    def get_next_phase(
        cls,
        current_phase: LearningPhase,
        session: LearningSession
    ) -> Optional[LearningPhase]:
        """Get the default next phase"""
        allowed = cls.TRANSITIONS.get(current_phase, [])
        return allowed[0] if allowed else None
    
    @classmethod
    def get_progress_percentage(
        cls,
        session: LearningSession
    ) -> int:
        """Calculate overall progress percentage"""
        phase_order = [
            LearningPhase.TOPIC_INTRODUCTION,
            LearningPhase.CONCEPT_EXPLANATION,
            LearningPhase.REAL_WORLD_EXAMPLES,
            LearningPhase.ANCIENT_KNOWLEDGE,
            LearningPhase.PRACTICAL_TASK,
            LearningPhase.COMMUNICATION_EXERCISE,
            LearningPhase.INDUSTRY_CHALLENGE,
            LearningPhase.REFLECTION
        ]
        
        try:
            current_index = phase_order.index(session.current_phase)
            # Add extra credit for completed phases
            completed_bonus = len(session.phase_progress) * 5
            base_progress = (current_index / len(phase_order)) * 100
            return min(int(base_progress + completed_bonus), 100)
        except ValueError:
            return 0
