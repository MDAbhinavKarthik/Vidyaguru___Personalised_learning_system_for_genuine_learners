"""
VidyaGuru Task Management & Skill Tracking - Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# ENUMS
# =============================================================================

class TaskTypeEnum(str, Enum):
    CODING_EXERCISE = "coding_exercise"
    CONCEPT_EXPLANATION = "concept_explanation"
    COMMUNICATION_TASK = "communication_task"
    RESEARCH_TASK = "research_task"
    INDUSTRY_PROBLEM = "industry_problem"


class TaskStatusEnum(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskDifficultyEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillCategoryEnum(str, Enum):
    CONCEPT_UNDERSTANDING = "concept_understanding"
    PRACTICAL_SKILLS = "practical_skills"
    COMMUNICATION_ABILITY = "communication_ability"
    PROBLEM_SOLVING = "problem_solving"


class SkillLevelEnum(str, Enum):
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


# =============================================================================
# SKILL WEIGHTS
# =============================================================================

class SkillWeights(BaseModel):
    """Skill impact weights for a task"""
    concept_understanding: float = Field(default=0.0, ge=0.0, le=1.0)
    practical_skills: float = Field(default=0.0, ge=0.0, le=1.0)
    communication_ability: float = Field(default=0.0, ge=0.0, le=1.0)
    problem_solving: float = Field(default=0.0, ge=0.0, le=1.0)


# =============================================================================
# TASK SCHEMAS
# =============================================================================

class CodingExerciseContent(BaseModel):
    """Content specific to coding exercises"""
    language: str = "python"
    starter_code: Optional[str] = None
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    expected_output: Optional[str] = None
    hints: List[str] = Field(default_factory=list)
    solution: Optional[str] = None  # Hidden from user


class ConceptExplanationContent(BaseModel):
    """Content specific to concept explanation tasks"""
    key_points: List[str] = Field(default_factory=list)
    required_depth: str = "intermediate"  # basic, intermediate, detailed
    target_audience: str = "peer"  # child, peer, expert
    required_examples: int = 2
    format: str = "written"  # written, video_script, presentation


class CommunicationTaskContent(BaseModel):
    """Content specific to communication tasks"""
    scenario: str
    audience: str
    tone: str = "professional"
    format: str = "written"
    word_limit: Optional[int] = None
    key_points_to_cover: List[str] = Field(default_factory=list)


class ResearchTaskContent(BaseModel):
    """Content specific to research tasks"""
    research_question: str
    sources_required: int = 3
    citation_format: str = "APA"
    deliverable: str = "summary"  # summary, report, presentation
    word_limit: Optional[int] = None


class IndustryProblemContent(BaseModel):
    """Content specific to industry problem solving"""
    problem_statement: str
    constraints: List[str] = Field(default_factory=list)
    real_world_context: str
    stakeholders: List[str] = Field(default_factory=list)
    expected_deliverables: List[str] = Field(default_factory=list)
    evaluation_criteria: List[str] = Field(default_factory=list)


class EvaluationRubric(BaseModel):
    """Evaluation criteria for tasks"""
    criteria: List[Dict[str, Any]] = Field(default_factory=list)
    # Each criteria: {name, weight, description, levels: {excellent, good, fair, poor}}
    auto_evaluation: bool = True
    requires_peer_review: bool = False


# =============================================================================
# TASK REQUEST SCHEMAS
# =============================================================================

class TaskCreateRequest(BaseModel):
    """Request to create a new task"""
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    instructions: str = Field(..., min_length=10)
    task_type: TaskTypeEnum
    difficulty: TaskDifficultyEnum = TaskDifficultyEnum.INTERMEDIATE
    topic: str = Field(..., min_length=1, max_length=255)
    concept: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    estimated_minutes: int = Field(default=30, ge=5, le=480)
    prerequisites: List[str] = Field(default_factory=list)
    skill_weights: SkillWeights = Field(default_factory=SkillWeights)
    base_xp: int = Field(default=10, ge=1, le=500)
    content: Dict[str, Any] = Field(default_factory=dict)
    evaluation_rubric: Dict[str, Any] = Field(default_factory=dict)
    passing_score: float = Field(default=70.0, ge=0.0, le=100.0)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Implement Binary Search",
                "description": "Implement binary search algorithm from scratch",
                "instructions": "Write a function that performs binary search...",
                "task_type": "coding_exercise",
                "difficulty": "intermediate",
                "topic": "Data Structures & Algorithms",
                "concept": "Binary Search",
                "tags": ["algorithms", "searching", "python"],
                "estimated_minutes": 45,
                "skill_weights": {
                    "concept_understanding": 0.3,
                    "practical_skills": 0.5,
                    "problem_solving": 0.2
                },
                "base_xp": 50
            }
        }


class TaskUpdateRequest(BaseModel):
    """Request to update an existing task"""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    difficulty: Optional[TaskDifficultyEnum] = None
    tags: Optional[List[str]] = None
    estimated_minutes: Optional[int] = Field(None, ge=5, le=480)
    prerequisites: Optional[List[str]] = None
    skill_weights: Optional[SkillWeights] = None
    base_xp: Optional[int] = Field(None, ge=1, le=500)
    content: Optional[Dict[str, Any]] = None
    evaluation_rubric: Optional[Dict[str, Any]] = None
    passing_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    is_active: Optional[bool] = None


class TaskAssignRequest(BaseModel):
    """Request to assign a task to a user"""
    task_id: UUID
    session_id: Optional[str] = None
    max_attempts: int = Field(default=3, ge=1, le=10)


class TaskSubmissionRequest(BaseModel):
    """Request to submit a task solution"""
    submission_type: str  # code, explanation, response, research
    content: str = Field(..., min_length=1)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskProgressUpdate(BaseModel):
    """Update task progress"""
    progress_percent: float = Field(..., ge=0.0, le=100.0)
    time_spent_seconds: int = Field(default=0, ge=0)


class HintRequestSchema(BaseModel):
    """Request a hint for a task"""
    hint_number: int = Field(default=1, ge=1, le=5)


# =============================================================================
# TASK RESPONSE SCHEMAS
# =============================================================================

class TaskResponse(BaseModel):
    """Task details response"""
    id: UUID
    title: str
    description: str
    instructions: str
    task_type: TaskTypeEnum
    difficulty: TaskDifficultyEnum
    topic: str
    concept: Optional[str]
    tags: List[str]
    estimated_minutes: int
    prerequisites: List[str]
    skill_weights: Dict[str, float]
    base_xp: int
    content: Dict[str, Any]
    passing_score: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """List of tasks"""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class TaskAssignmentResponse(BaseModel):
    """Task assignment details"""
    id: UUID
    task_id: UUID
    task: TaskResponse
    status: TaskStatusEnum
    progress_percent: float
    attempts: int
    max_attempts: int
    score: Optional[float]
    feedback: Optional[Dict[str, Any]]
    skill_gains: Dict[str, float]
    xp_earned: int
    bonus_xp: int
    hints_used: int
    started_at: Optional[datetime]
    submitted_at: Optional[datetime]
    completed_at: Optional[datetime]
    time_spent_seconds: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskAssignmentListResponse(BaseModel):
    """List of task assignments"""
    assignments: List[TaskAssignmentResponse]
    total: int
    page: int
    page_size: int


class TaskFeedbackResponse(BaseModel):
    """Feedback after task evaluation"""
    assignment_id: UUID
    score: float
    passed: bool
    feedback: Dict[str, Any]
    # detailed_scores, strengths, improvements, ai_feedback
    skill_gains: Dict[str, float]
    xp_earned: int
    bonus_xp: int
    next_recommended_tasks: List[UUID]


class HintResponseSchema(BaseModel):
    """Hint response"""
    hint_number: int
    total_hints: int
    hint_content: str
    xp_penalty: int


# =============================================================================
# SKILL SCHEMAS
# =============================================================================

class SkillCreateRequest(BaseModel):
    """Initialize a skill for a user"""
    category: SkillCategoryEnum
    topic: Optional[str] = None


class SkillResponse(BaseModel):
    """User skill details"""
    id: UUID
    category: SkillCategoryEnum
    topic: Optional[str]
    level: float
    proficiency: SkillLevelEnum
    total_xp: int
    tasks_completed: int
    average_score: float
    streak_days: int
    best_streak: int
    xp_to_next_level: int
    last_activity: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SkillSummaryResponse(BaseModel):
    """Summary of all user skills"""
    user_id: UUID
    overall_level: float
    skills: Dict[str, SkillResponse]
    # {category: skill_response}
    top_skills: List[SkillResponse]
    skills_to_improve: List[SkillResponse]
    recent_progress: List[Dict[str, Any]]
    total_xp: int
    total_tasks_completed: int


class SkillHistoryEntry(BaseModel):
    """Single skill history entry"""
    id: UUID
    skill_id: UUID
    category: SkillCategoryEnum
    source_type: str
    previous_level: float
    new_level: float
    change_amount: float
    xp_gained: int
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SkillHistoryResponse(BaseModel):
    """Skill history for a user"""
    history: List[SkillHistoryEntry]
    total: int
    page: int
    page_size: int


class SkillProgressChart(BaseModel):
    """Data for skill progress visualization"""
    category: SkillCategoryEnum
    topic: Optional[str]
    data_points: List[Dict[str, Any]]
    # [{date, level, xp}]
    period_start: datetime
    period_end: datetime
    total_change: float


# =============================================================================
# ASSESSMENT SCHEMAS
# =============================================================================

class AssessmentQuestion(BaseModel):
    """Single assessment question"""
    id: str
    question: str
    question_type: str  # multiple_choice, coding, explanation
    options: Optional[List[str]] = None
    points: int = 10


class AssessmentStartRequest(BaseModel):
    """Request to start a skill assessment"""
    category: SkillCategoryEnum
    topic: Optional[str] = None
    assessment_type: str = "periodic"  # initial, periodic, challenge


class AssessmentSubmitRequest(BaseModel):
    """Submit assessment responses"""
    responses: List[Dict[str, Any]]
    # [{question_id, answer, time_taken}]


class AssessmentResponse(BaseModel):
    """Assessment details"""
    id: UUID
    category: SkillCategoryEnum
    topic: Optional[str]
    assessment_type: str
    questions: List[AssessmentQuestion]
    score: Optional[float]
    passed: Optional[bool]
    level_before: float
    level_after: Optional[float]
    breakdown: Optional[Dict[str, Any]]
    recommendations: Optional[List[str]]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# =============================================================================
# MILESTONE SCHEMAS
# =============================================================================

class MilestoneResponse(BaseModel):
    """Milestone details"""
    id: UUID
    name: str
    description: str
    icon: Optional[str]
    category: Optional[SkillCategoryEnum]
    required_level: float
    required_tasks: int
    required_streak: int
    xp_reward: int
    badge_id: Optional[str]

    class Config:
        from_attributes = True


class UserMilestoneResponse(BaseModel):
    """User's achieved milestone"""
    id: UUID
    milestone: MilestoneResponse
    achieved_at: datetime
    context: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class MilestoneProgressResponse(BaseModel):
    """Progress towards milestones"""
    achieved: List[UserMilestoneResponse]
    in_progress: List[Dict[str, Any]]
    # [{milestone, current_progress, required, percent_complete}]
    total_achieved: int
    total_available: int


# =============================================================================
# ANALYTICS SCHEMAS
# =============================================================================

class TaskAnalytics(BaseModel):
    """Analytics for task performance"""
    total_tasks_attempted: int
    total_tasks_completed: int
    completion_rate: float
    average_score: float
    average_time_minutes: float
    tasks_by_type: Dict[str, int]
    tasks_by_difficulty: Dict[str, int]
    recent_completions: List[Dict[str, Any]]


class SkillAnalytics(BaseModel):
    """Analytics for skill development"""
    skill_distribution: Dict[str, float]
    strongest_skill: SkillCategoryEnum
    weakest_skill: SkillCategoryEnum
    total_skill_xp: int
    skill_growth_rate: float  # % change over period
    recommended_focus: List[SkillCategoryEnum]


class OverallAnalyticsResponse(BaseModel):
    """Combined analytics response"""
    user_id: UUID
    period_days: int
    task_analytics: TaskAnalytics
    skill_analytics: SkillAnalytics
    milestones_achieved: int
    current_streak: int
    total_learning_minutes: int
    xp_earned_period: int
