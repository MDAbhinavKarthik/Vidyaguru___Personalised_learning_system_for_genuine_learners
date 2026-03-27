"""
VidyaGuru Learning Engine
Controls the flow of educational content through 8 stages with strict progression rules

"अभ्यासेन तु कौन्तेय वैराग्येण च गृह्यते" - Through practice it is attained
"""
from enum import Enum, auto
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from uuid import uuid4
import json

from pydantic import BaseModel, Field


# =============================================================================
# LEARNING STAGES
# =============================================================================

class LearningStage(str, Enum):
    """
    The 8 stages of learning flow.
    Users must complete each stage before advancing.
    """
    CONCEPT_INTRODUCTION = "concept_introduction"      # Stage 1
    EXPLANATION = "explanation"                        # Stage 2
    REAL_WORLD_APPLICATION = "real_world_application"  # Stage 3
    ANCIENT_KNOWLEDGE = "ancient_knowledge"            # Stage 4
    PRACTICAL_TASK = "practical_task"                  # Stage 5
    COMMUNICATION_TASK = "communication_task"          # Stage 6
    INDUSTRY_CHALLENGE = "industry_challenge"          # Stage 7
    REFLECTION_SUMMARY = "reflection_summary"          # Stage 8


class StageStatus(str, Enum):
    """Status of a learning stage"""
    LOCKED = "locked"           # Cannot access yet
    AVAILABLE = "available"     # Can start
    IN_PROGRESS = "in_progress" # Currently working on
    COMPLETED = "completed"     # Successfully finished
    SKIPPED = "skipped"         # Skipped with penalty (admin only)


# =============================================================================
# STAGE REQUIREMENTS
# =============================================================================

@dataclass
class StageRequirement:
    """Requirements to complete a stage"""
    min_interactions: int = 2           # Minimum back-and-forth exchanges
    min_time_seconds: int = 60          # Minimum time spent in stage
    requires_submission: bool = False   # Needs code/text submission
    requires_explanation: bool = False  # Needs verbal explanation
    requires_verification: bool = False # Needs understanding verification
    min_word_count: int = 0             # Minimum words in responses
    custom_validator: Optional[str] = None  # Custom validation function name


# Stage-specific requirements
STAGE_REQUIREMENTS: Dict[LearningStage, StageRequirement] = {
    LearningStage.CONCEPT_INTRODUCTION: StageRequirement(
        min_interactions=2,
        min_time_seconds=30,
        min_word_count=20
    ),
    LearningStage.EXPLANATION: StageRequirement(
        min_interactions=3,
        min_time_seconds=120,
        requires_verification=True,
        min_word_count=50
    ),
    LearningStage.REAL_WORLD_APPLICATION: StageRequirement(
        min_interactions=2,
        min_time_seconds=60,
        min_word_count=30
    ),
    LearningStage.ANCIENT_KNOWLEDGE: StageRequirement(
        min_interactions=1,
        min_time_seconds=30,
        min_word_count=10
    ),
    LearningStage.PRACTICAL_TASK: StageRequirement(
        min_interactions=4,
        min_time_seconds=300,  # 5 minutes minimum
        requires_submission=True,
        requires_explanation=True,
        requires_verification=True,
        min_word_count=100
    ),
    LearningStage.COMMUNICATION_TASK: StageRequirement(
        min_interactions=3,
        min_time_seconds=180,
        requires_submission=True,
        min_word_count=100
    ),
    LearningStage.INDUSTRY_CHALLENGE: StageRequirement(
        min_interactions=4,
        min_time_seconds=600,  # 10 minutes minimum
        requires_submission=True,
        requires_explanation=True,
        requires_verification=True,
        min_word_count=150
    ),
    LearningStage.REFLECTION_SUMMARY: StageRequirement(
        min_interactions=2,
        min_time_seconds=60,
        min_word_count=50
    )
}


# =============================================================================
# STAGE CONTENT TEMPLATES
# =============================================================================

@dataclass
class StageContent:
    """Content template for each stage"""
    title: str
    description: str
    objectives: List[str]
    mentor_prompt: str
    completion_criteria: str
    xp_reward: int


STAGE_CONTENT: Dict[LearningStage, StageContent] = {
    LearningStage.CONCEPT_INTRODUCTION: StageContent(
        title="Concept Introduction",
        description="Get introduced to the concept and understand why it matters",
        objectives=[
            "Understand what the concept is",
            "Know why it's important",
            "Connect it to what you already know"
        ],
        mentor_prompt="""Introduce the concept of {topic} to the learner.
        
Your goals:
1. Start with an intriguing hook or question
2. Explain what this concept is in simple terms
3. Share why it matters in the real world
4. Ask what they already know about it
5. Set expectations for the learning journey

Keep it engaging and curiosity-driven. End with a question to check their initial understanding.""",
        completion_criteria="Learner demonstrates basic awareness of the concept",
        xp_reward=10
    ),
    
    LearningStage.EXPLANATION: StageContent(
        title="Deep Explanation",
        description="Understand the concept thoroughly through guided exploration",
        objectives=[
            "Grasp core principles",
            "Understand how it works",
            "Identify key components"
        ],
        mentor_prompt="""Explain {topic} in depth to the learner using the Socratic method.

Your approach:
1. Break down the concept into digestible parts
2. Use analogies relevant to their interests: {interests}
3. Ask guiding questions instead of giving direct answers
4. Check understanding at each step
5. Adapt depth based on their level: {experience_level}

Do NOT give complete explanations. Guide them to discover insights themselves.
Verify understanding before moving on.""",
        completion_criteria="Learner can explain the concept in their own words",
        xp_reward=25
    ),
    
    LearningStage.REAL_WORLD_APPLICATION: StageContent(
        title="Real-World Applications",
        description="See how this concept is used in actual products and systems",
        objectives=[
            "See practical applications",
            "Understand industry usage",
            "Connect theory to practice"
        ],
        mentor_prompt="""Show real-world applications of {topic}.

Include:
1. How major tech companies use this (Google, Amazon, Netflix, etc.)
2. Indian tech examples (Flipkart, Zomato, Razorpay)
3. Day-to-day applications they interact with
4. A personalized example based on their interests: {interests}

Ask them to identify other applications they've encountered.
Make the abstract concrete and relevant.""",
        completion_criteria="Learner identifies real applications of the concept",
        xp_reward=15
    ),
    
    LearningStage.ANCIENT_KNOWLEDGE: StageContent(
        title="Ancient Wisdom Connection",
        description="Connect modern knowledge to timeless wisdom",
        objectives=[
            "See the historical context",
            "Appreciate timeless principles",
            "Gain deeper perspective"
        ],
        mentor_prompt="""Connect {topic} to ancient knowledge and wisdom.

Find genuine connections to:
- Indian mathematics (Aryabhata, Brahmagupta, Bhaskara)
- Sanskrit grammar and formal systems (Panini)
- Vedic/philosophical texts
- Other ancient civilizations (Greek, Chinese, Arabic)

Include:
1. A relevant Sanskrit shloka with translation
2. Historical context of the discovery/principle
3. How ancient insights apply today

Only use ACCURATE historical connections. If no direct connection exists, 
share wisdom about knowledge and learning from ancient texts.""",
        completion_criteria="Learner reflects on the historical connection",
        xp_reward=10
    ),
    
    LearningStage.PRACTICAL_TASK: StageContent(
        title="Hands-On Practice",
        description="Apply your understanding through a practical coding task",
        objectives=[
            "Apply the concept in code",
            "Solve a structured problem",
            "Verify understanding through practice"
        ],
        mentor_prompt="""Create a practical task for {topic} at {difficulty} difficulty.

Task requirements:
1. Build on the concepts explained
2. Have 3 parts (Foundation → Extension → Challenge)
3. Include unique constraints to prevent copy-paste
4. Require explanation alongside code
5. Include verification questions

Anti-cheating elements:
- Ask for step-by-step reasoning
- Request alternative approaches
- Include "what if" variations
- Verify understanding verbally

Do not accept solutions without explanations.""",
        completion_criteria="Learner submits working code with proper explanation",
        xp_reward=50
    ),
    
    LearningStage.COMMUNICATION_TASK: StageContent(
        title="Communication Exercise",
        description="Practice explaining technical concepts to different audiences",
        objectives=[
            "Develop technical communication skills",
            "Reinforce understanding through teaching",
            "Build confidence in explanation"
        ],
        mentor_prompt="""Create a communication exercise for {topic}.

Exercise types:
1. "Explain to a 5-year-old" - simplify maximally
2. "Explain to your non-technical manager" - focus on impact
3. "Write documentation for new team members" - be precise
4. "Interview scenario" - be concise and clear

Evaluate their response on:
- Clarity (Is it understandable?)
- Accuracy (Is it correct?)
- Appropriateness (Right level for audience?)
- Engagement (Is it interesting?)

Provide constructive feedback.""",
        completion_criteria="Learner successfully explains to a given audience",
        xp_reward=30
    ),
    
    LearningStage.INDUSTRY_CHALLENGE: StageContent(
        title="Industry Challenge",
        description="Solve a realistic industry problem with real constraints",
        objectives=[
            "Apply knowledge to realistic scenarios",
            "Consider trade-offs and constraints",
            "Think like a professional"
        ],
        mentor_prompt="""Present an industry challenge related to {topic}.

Challenge structure:
1. Company context (realistic scenario)
2. Business requirements
3. Technical constraints (budget, timeline, legacy systems, scale)
4. Deliverables expected

Evaluation criteria:
- Does it meet business requirements?
- Is it technically sound?
- Are trade-offs considered?
- Is it scalable?
- Can they explain their decisions?

Push for depth and professional-level thinking.""",
        completion_criteria="Learner provides a well-reasoned solution with trade-off analysis",
        xp_reward=75
    ),
    
    LearningStage.REFLECTION_SUMMARY: StageContent(
        title="Reflection & Summary",
        description="Consolidate learning and plan next steps",
        objectives=[
            "Reflect on what was learned",
            "Identify strengths and gaps",
            "Plan continued learning"
        ],
        mentor_prompt="""Guide the learner through reflection on {topic}.

Reflection structure:
1. Celebrate their achievement genuinely
2. Quick verbal check on key concepts
3. Self-assessment questions:
   - Confidence level (1-10)
   - Most challenging part
   - Most interesting discovery
   - Remaining questions
4. Connection to previous learning
5. Next steps and related topics
6. Closing wisdom quote

End with an inspiring note about their growth.""",
        completion_criteria="Learner completes self-assessment and identifies next steps",
        xp_reward=20
    )
}


# =============================================================================
# LEARNING SESSION STATE
# =============================================================================

class StageProgress(BaseModel):
    """Progress within a single stage"""
    stage: LearningStage
    status: StageStatus = StageStatus.LOCKED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    interactions: int = 0
    total_words: int = 0
    submissions: List[Dict[str, Any]] = Field(default_factory=list)
    verification_passed: bool = False
    explanation_provided: bool = False
    attempts: int = 0
    hints_used: int = 0
    xp_earned: int = 0
    feedback: Optional[str] = None


class LearningSessionState(BaseModel):
    """Complete state of a learning session"""
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    topic: str
    concept: Optional[str] = None
    difficulty: str = "intermediate"
    
    # Stage tracking
    current_stage: LearningStage = LearningStage.CONCEPT_INTRODUCTION
    stage_progress: Dict[str, StageProgress] = Field(default_factory=dict)
    
    # Session metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Learner context
    experience_level: str = "intermediate"
    interests: List[str] = Field(default_factory=list)
    
    # Totals
    total_xp: int = 0
    total_time_seconds: int = 0
    
    # Flags
    is_complete: bool = False
    is_paused: bool = False
    
    def model_post_init(self, __context):
        """Initialize stage progress for all stages"""
        if not self.stage_progress:
            for stage in LearningStage:
                status = StageStatus.AVAILABLE if stage == LearningStage.CONCEPT_INTRODUCTION else StageStatus.LOCKED
                self.stage_progress[stage.value] = StageProgress(stage=stage, status=status)


# =============================================================================
# LEARNING ENGINE
# =============================================================================

class LearningEngine:
    """
    Core engine that controls the learning flow.
    Ensures users progress through stages properly without skipping.
    """
    
    # Stage order for traversal
    STAGE_ORDER = [
        LearningStage.CONCEPT_INTRODUCTION,
        LearningStage.EXPLANATION,
        LearningStage.REAL_WORLD_APPLICATION,
        LearningStage.ANCIENT_KNOWLEDGE,
        LearningStage.PRACTICAL_TASK,
        LearningStage.COMMUNICATION_TASK,
        LearningStage.INDUSTRY_CHALLENGE,
        LearningStage.REFLECTION_SUMMARY
    ]
    
    def __init__(self):
        self.sessions: Dict[str, LearningSessionState] = {}
    
    # -------------------------------------------------------------------------
    # SESSION MANAGEMENT
    # -------------------------------------------------------------------------
    
    def create_session(
        self,
        user_id: str,
        topic: str,
        concept: Optional[str] = None,
        difficulty: str = "intermediate",
        experience_level: str = "intermediate",
        interests: Optional[List[str]] = None
    ) -> LearningSessionState:
        """Create a new learning session"""
        session = LearningSessionState(
            user_id=user_id,
            topic=topic,
            concept=concept or topic,
            difficulty=difficulty,
            experience_level=experience_level,
            interests=interests or []
        )
        
        # Mark first stage as available and in progress
        first_stage = self.STAGE_ORDER[0]
        session.stage_progress[first_stage.value].status = StageStatus.IN_PROGRESS
        session.stage_progress[first_stage.value].started_at = datetime.utcnow()
        
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[LearningSessionState]:
        """Retrieve a session by ID"""
        return self.sessions.get(session_id)
    
    def save_session(self, session: LearningSessionState) -> None:
        """Save session state"""
        session.updated_at = datetime.utcnow()
        self.sessions[session.session_id] = session
    
    # -------------------------------------------------------------------------
    # STAGE PROGRESSION
    # -------------------------------------------------------------------------
    
    def get_current_stage_content(self, session: LearningSessionState) -> StageContent:
        """Get content for the current stage"""
        return STAGE_CONTENT[session.current_stage]
    
    def get_current_stage_requirements(self, session: LearningSessionState) -> StageRequirement:
        """Get requirements for the current stage"""
        return STAGE_REQUIREMENTS[session.current_stage]
    
    def can_advance_stage(self, session: LearningSessionState) -> Tuple[bool, List[str]]:
        """
        Check if user can advance to the next stage.
        Returns (can_advance, list_of_unmet_requirements)
        """
        current = session.current_stage
        progress = session.stage_progress[current.value]
        requirements = STAGE_REQUIREMENTS[current]
        
        unmet = []
        
        # Check minimum interactions
        if progress.interactions < requirements.min_interactions:
            unmet.append(
                f"Need {requirements.min_interactions - progress.interactions} more interactions"
            )
        
        # Check minimum time
        if progress.started_at:
            time_spent = (datetime.utcnow() - progress.started_at).total_seconds()
            if time_spent < requirements.min_time_seconds:
                remaining = requirements.min_time_seconds - time_spent
                unmet.append(f"Need {int(remaining)} more seconds in this stage")
        
        # Check submission requirement
        if requirements.requires_submission and not progress.submissions:
            unmet.append("Submission required for this stage")
        
        # Check explanation requirement
        if requirements.requires_explanation and not progress.explanation_provided:
            unmet.append("Explanation required for this stage")
        
        # Check verification requirement
        if requirements.requires_verification and not progress.verification_passed:
            unmet.append("Understanding verification required")
        
        # Check minimum word count
        if progress.total_words < requirements.min_word_count:
            unmet.append(
                f"Need {requirements.min_word_count - progress.total_words} more words in responses"
            )
        
        return len(unmet) == 0, unmet
    
    def advance_to_next_stage(
        self,
        session: LearningSessionState,
        force: bool = False
    ) -> Tuple[bool, str, Optional[LearningStage]]:
        """
        Advance to the next stage if requirements are met.
        
        Args:
            session: Current session state
            force: Force advancement (admin only, with XP penalty)
            
        Returns:
            (success, message, new_stage)
        """
        can_advance, unmet = self.can_advance_stage(session)
        
        if not can_advance and not force:
            return False, f"Cannot advance. Unmet requirements: {', '.join(unmet)}", None
        
        current_idx = self.STAGE_ORDER.index(session.current_stage)
        
        # Check if already at last stage
        if current_idx >= len(self.STAGE_ORDER) - 1:
            return False, "Already at the final stage", None
        
        # Complete current stage
        current_progress = session.stage_progress[session.current_stage.value]
        current_progress.status = StageStatus.COMPLETED
        current_progress.completed_at = datetime.utcnow()
        
        # Award XP (with penalty if forced)
        stage_content = STAGE_CONTENT[session.current_stage]
        xp_earned = stage_content.xp_reward
        if force:
            xp_earned = int(xp_earned * 0.5)  # 50% penalty for forcing
            current_progress.status = StageStatus.SKIPPED
        
        current_progress.xp_earned = xp_earned
        session.total_xp += xp_earned
        
        # Move to next stage
        next_stage = self.STAGE_ORDER[current_idx + 1]
        session.current_stage = next_stage
        
        # Initialize next stage
        next_progress = session.stage_progress[next_stage.value]
        next_progress.status = StageStatus.IN_PROGRESS
        next_progress.started_at = datetime.utcnow()
        
        # Unlock the stage
        session.stage_progress[next_stage.value] = next_progress
        
        self.save_session(session)
        
        message = f"Advanced to {next_stage.value}"
        if force:
            message += " (forced - 50% XP penalty applied)"
        
        return True, message, next_stage
    
    def complete_session(self, session: LearningSessionState) -> Dict[str, Any]:
        """Complete the learning session"""
        # Verify all stages are complete
        incomplete = []
        for stage in self.STAGE_ORDER:
            progress = session.stage_progress[stage.value]
            if progress.status not in [StageStatus.COMPLETED, StageStatus.SKIPPED]:
                incomplete.append(stage.value)
        
        if incomplete:
            return {
                "success": False,
                "message": f"Cannot complete session. Incomplete stages: {', '.join(incomplete)}"
            }
        
        # Finalize last stage
        last_progress = session.stage_progress[self.STAGE_ORDER[-1].value]
        if last_progress.status == StageStatus.IN_PROGRESS:
            last_progress.status = StageStatus.COMPLETED
            last_progress.completed_at = datetime.utcnow()
            last_progress.xp_earned = STAGE_CONTENT[self.STAGE_ORDER[-1]].xp_reward
            session.total_xp += last_progress.xp_earned
        
        # Mark session complete
        session.is_complete = True
        session.completed_at = datetime.utcnow()
        
        # Calculate total time
        session.total_time_seconds = int(
            (session.completed_at - session.created_at).total_seconds()
        )
        
        self.save_session(session)
        
        return {
            "success": True,
            "message": "Learning session completed!",
            "summary": {
                "topic": session.topic,
                "total_xp": session.total_xp,
                "total_time_minutes": session.total_time_seconds // 60,
                "stages_completed": sum(
                    1 for s in session.stage_progress.values()
                    if s.status == StageStatus.COMPLETED
                ),
                "stages_skipped": sum(
                    1 for s in session.stage_progress.values()
                    if s.status == StageStatus.SKIPPED
                )
            }
        }
    
    # -------------------------------------------------------------------------
    # INTERACTION TRACKING
    # -------------------------------------------------------------------------
    
    def record_interaction(
        self,
        session: LearningSessionState,
        user_message: str,
        mentor_response: str
    ) -> StageProgress:
        """Record an interaction in the current stage"""
        progress = session.stage_progress[session.current_stage.value]
        
        # Increment interactions
        progress.interactions += 1
        
        # Count words
        user_words = len(user_message.split())
        progress.total_words += user_words
        
        self.save_session(session)
        return progress
    
    def record_submission(
        self,
        session: LearningSessionState,
        submission: Dict[str, Any]
    ) -> StageProgress:
        """Record a submission (code, explanation, etc.)"""
        progress = session.stage_progress[session.current_stage.value]
        
        submission["submitted_at"] = datetime.utcnow().isoformat()
        progress.submissions.append(submission)
        progress.attempts += 1
        
        # Check if explanation was provided
        if submission.get("explanation") and len(submission["explanation"]) > 50:
            progress.explanation_provided = True
        
        self.save_session(session)
        return progress
    
    def mark_verification_passed(self, session: LearningSessionState) -> StageProgress:
        """Mark that understanding verification has passed"""
        progress = session.stage_progress[session.current_stage.value]
        progress.verification_passed = True
        self.save_session(session)
        return progress
    
    def use_hint(self, session: LearningSessionState) -> Tuple[bool, str]:
        """Record hint usage (with XP penalty)"""
        progress = session.stage_progress[session.current_stage.value]
        
        max_hints = 3
        if progress.hints_used >= max_hints:
            return False, "No more hints available for this stage"
        
        progress.hints_used += 1
        
        # XP penalty for hints in task stages
        if session.current_stage in [
            LearningStage.PRACTICAL_TASK,
            LearningStage.INDUSTRY_CHALLENGE
        ]:
            penalty = 5 * progress.hints_used
            session.total_xp = max(0, session.total_xp - penalty)
        
        self.save_session(session)
        return True, f"Hint {progress.hints_used}/{max_hints} used"
    
    # -------------------------------------------------------------------------
    # PROGRESS QUERIES
    # -------------------------------------------------------------------------
    
    def get_session_progress(self, session: LearningSessionState) -> Dict[str, Any]:
        """Get complete progress report for a session"""
        stages_info = []
        
        for stage in self.STAGE_ORDER:
            progress = session.stage_progress[stage.value]
            content = STAGE_CONTENT[stage]
            requirements = STAGE_REQUIREMENTS[stage]
            
            stage_info = {
                "stage": stage.value,
                "title": content.title,
                "status": progress.status.value,
                "xp_reward": content.xp_reward,
                "xp_earned": progress.xp_earned,
                "is_current": stage == session.current_stage,
                "interactions": progress.interactions,
                "min_interactions": requirements.min_interactions,
                "time_spent_seconds": (
                    (datetime.utcnow() - progress.started_at).total_seconds()
                    if progress.started_at else 0
                ),
                "min_time_seconds": requirements.min_time_seconds
            }
            
            if stage == session.current_stage:
                can_advance, unmet = self.can_advance_stage(session)
                stage_info["can_advance"] = can_advance
                stage_info["unmet_requirements"] = unmet
            
            stages_info.append(stage_info)
        
        # Calculate overall progress
        completed = sum(
            1 for s in session.stage_progress.values()
            if s.status in [StageStatus.COMPLETED, StageStatus.SKIPPED]
        )
        
        return {
            "session_id": session.session_id,
            "topic": session.topic,
            "current_stage": session.current_stage.value,
            "overall_progress_percent": int((completed / len(self.STAGE_ORDER)) * 100),
            "total_xp": session.total_xp,
            "max_xp": sum(c.xp_reward for c in STAGE_CONTENT.values()),
            "stages": stages_info,
            "is_complete": session.is_complete
        }
    
    def get_stage_prompt(
        self,
        session: LearningSessionState,
        stage: Optional[LearningStage] = None
    ) -> str:
        """Get the mentor prompt for a stage with context filled in"""
        stage = stage or session.current_stage
        content = STAGE_CONTENT[stage]
        
        return content.mentor_prompt.format(
            topic=session.topic,
            concept=session.concept or session.topic,
            difficulty=session.difficulty,
            experience_level=session.experience_level,
            interests=", ".join(session.interests) if session.interests else "general technology"
        )


# =============================================================================
# STAGE VALIDATORS
# =============================================================================

class StageValidator:
    """
    Validates stage completion requirements.
    Prevents cheating and ensures genuine engagement.
    """
    
    @staticmethod
    def validate_concept_introduction(
        progress: StageProgress,
        session: LearningSessionState
    ) -> Tuple[bool, List[str]]:
        """Validate concept introduction stage"""
        issues = []
        
        if progress.interactions < 2:
            issues.append("Need more engagement with the introduction")
        
        if progress.total_words < 20:
            issues.append("Please share more of your thoughts")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_explanation(
        progress: StageProgress,
        session: LearningSessionState
    ) -> Tuple[bool, List[str]]:
        """Validate explanation stage"""
        issues = []
        
        if progress.interactions < 3:
            issues.append("Need more back-and-forth to ensure understanding")
        
        if not progress.verification_passed:
            issues.append("Please demonstrate understanding by explaining the concept")
        
        if progress.total_words < 50:
            issues.append("Need more detailed responses to verify understanding")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_practical_task(
        progress: StageProgress,
        session: LearningSessionState
    ) -> Tuple[bool, List[str]]:
        """Validate practical task stage"""
        issues = []
        
        if not progress.submissions:
            issues.append("Please submit your solution")
        
        if progress.submissions:
            last_submission = progress.submissions[-1]
            
            # Check for explanation
            if not last_submission.get("explanation"):
                issues.append("Please explain your approach")
            elif len(last_submission.get("explanation", "")) < 50:
                issues.append("Please provide a more detailed explanation")
            
            # Check for code
            if not last_submission.get("code"):
                issues.append("Please include your code solution")
        
        if not progress.verification_passed:
            issues.append("Please answer the verification questions")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_industry_challenge(
        progress: StageProgress,
        session: LearningSessionState
    ) -> Tuple[bool, List[str]]:
        """Validate industry challenge stage"""
        issues = []
        
        if not progress.submissions:
            issues.append("Please submit your solution")
        
        if progress.submissions:
            last_submission = progress.submissions[-1]
            
            # Check for design/explanation
            if not last_submission.get("explanation"):
                issues.append("Please explain your design decisions")
            elif len(last_submission.get("explanation", "")) < 100:
                issues.append("Please provide a more comprehensive explanation")
            
            # Check for trade-off discussion
            explanation = last_submission.get("explanation", "").lower()
            trade_off_keywords = ["trade-off", "tradeoff", "alternative", "instead", "versus", "pros", "cons"]
            if not any(kw in explanation for kw in trade_off_keywords):
                issues.append("Please discuss trade-offs in your solution")
        
        if not progress.verification_passed:
            issues.append("Please answer the follow-up questions")
        
        return len(issues) == 0, issues


# =============================================================================
# SINGLETON ENGINE INSTANCE
# =============================================================================

learning_engine = LearningEngine()
