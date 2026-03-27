"""
Industry Challenges Schemas

Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ChallengeCategory(str, Enum):
    SYSTEM_DESIGN = "system_design"
    SCALABILITY = "scalability"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"
    SOFTWARE_ARCHITECTURE = "software_architecture"


class ChallengeDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SolutionStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    EVALUATED = "evaluated"
    RESUME_WORTHY = "resume_worthy"


# ============== Challenge Schemas ==============

class ChallengeGenerateRequest(BaseModel):
    """Request to generate a new industry challenge"""
    category: ChallengeCategory
    difficulty: ChallengeDifficulty
    industry: Optional[str] = Field(None, description="Target industry (e.g., E-commerce, FinTech)")
    company_type: Optional[str] = Field(None, description="Company type (e.g., Startup, FAANG)")
    focus_areas: Optional[List[str]] = Field(None, description="Specific areas to focus on")
    user_skill_level: Optional[str] = Field(None, description="User's current skill level")


class ChallengeBase(BaseModel):
    title: str
    category: ChallengeCategory
    difficulty: ChallengeDifficulty
    problem_statement: str
    context: str
    constraints: List[str]
    requirements: List[str]
    evaluation_criteria: List[Dict[str, Any]]
    expected_concepts: List[str]
    industry: Optional[str] = None
    company_type: Optional[str] = None
    tech_stack_hints: Optional[List[str]] = None
    estimated_time_hours: float = 2.0
    xp_reward: int = 500


class ChallengeCreate(ChallengeBase):
    pass


class ChallengeResponse(ChallengeBase):
    id: int
    is_active: bool
    times_attempted: int
    success_rate: float
    created_at: datetime

    class Config:
        from_attributes = True


class ChallengeListResponse(BaseModel):
    challenges: List[ChallengeResponse]
    total: int
    page: int
    page_size: int


# ============== Solution Schemas ==============

class SolutionSubmitRequest(BaseModel):
    """Request to submit a solution"""
    challenge_id: int
    solution_text: str = Field(..., min_length=100, description="Detailed solution explanation")
    architecture_diagram: Optional[str] = Field(None, description="Architecture diagram (Mermaid/ASCII)")
    trade_offs_discussed: Optional[List[str]] = Field(None, description="Trade-offs considered")
    technologies_proposed: Optional[List[str]] = Field(None, description="Technologies chosen")


class SolutionDraftRequest(BaseModel):
    """Request to save a draft solution"""
    challenge_id: int
    solution_text: str
    architecture_diagram: Optional[str] = None
    trade_offs_discussed: Optional[List[str]] = None
    technologies_proposed: Optional[List[str]] = None


class SolutionEvaluationResponse(BaseModel):
    """AI evaluation of a solution"""
    solution_id: int
    status: SolutionStatus
    
    # Scores (0-100)
    innovation_score: float = Field(..., ge=0, le=100)
    practicality_score: float = Field(..., ge=0, le=100)
    completeness_score: float = Field(..., ge=0, le=100)
    overall_score: float = Field(..., ge=0, le=100)
    
    # Detailed feedback
    ai_feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]
    
    # Resume recommendation
    is_resume_worthy: bool
    resume_recommendation: Optional["ResumeRecommendation"] = None
    
    # XP earned
    xp_earned: int


class ResumeRecommendation(BaseModel):
    """Resume recommendation for outstanding solutions"""
    headline: str
    bullet_points: List[str]
    skills_demonstrated: List[str]
    impact_statement: str
    recommendation_reason: str


class SolutionResponse(BaseModel):
    id: int
    challenge_id: int
    user_id: int
    solution_text: str
    architecture_diagram: Optional[str]
    trade_offs_discussed: Optional[List[str]]
    technologies_proposed: Optional[List[str]]
    status: SolutionStatus
    
    # Evaluation (if evaluated)
    ai_feedback: Optional[str]
    strengths: Optional[List[str]]
    areas_for_improvement: Optional[List[str]]
    innovation_score: Optional[float]
    practicality_score: Optional[float]
    completeness_score: Optional[float]
    overall_score: Optional[float]
    
    # Resume
    is_resume_worthy: bool
    resume_bullet_points: Optional[List[str]]
    
    xp_earned: int
    created_at: datetime
    submitted_at: Optional[datetime]
    evaluated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============== Resume Highlight Schemas ==============

class ResumeHighlightCreate(BaseModel):
    solution_id: int
    headline: str
    bullet_points: List[str]
    skills_demonstrated: List[str]
    impact_statement: str


class ResumeHighlightResponse(BaseModel):
    id: int
    user_id: int
    solution_id: int
    headline: str
    bullet_points: List[str]
    skills_demonstrated: List[str]
    impact_statement: str
    added_to_resume: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserResumeHighlightsResponse(BaseModel):
    """All resume highlights for a user"""
    highlights: List[ResumeHighlightResponse]
    total_challenges_completed: int
    resume_worthy_solutions: int


# ============== Analytics Schemas ==============

class ChallengeStatsResponse(BaseModel):
    """Statistics for a challenge"""
    challenge_id: int
    total_attempts: int
    completion_rate: float
    average_score: float
    top_score: float
    resume_worthy_solutions: int


class UserChallengeStatsResponse(BaseModel):
    """User's challenge statistics"""
    total_attempted: int
    total_completed: int
    total_resume_worthy: int
    average_score: float
    total_xp_earned: int
    challenges_by_category: Dict[str, int]
    strongest_category: Optional[str]


# Update forward references
SolutionEvaluationResponse.model_rebuild()
