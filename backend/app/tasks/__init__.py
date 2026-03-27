"""
VidyaGuru Task Management & Skill Tracking Module
=================================================

A comprehensive system for managing learning tasks and tracking skill development.

Task Types:
- Coding Exercises: Programming challenges with test cases
- Concept Explanations: Demonstrate understanding by teaching
- Communication Tasks: Professional communication scenarios
- Research Tasks: Gather and synthesize information
- Industry Problems: Real-world problem solving

Skill Categories:
- Concept Understanding: Theoretical knowledge
- Practical Skills: Hands-on implementation ability
- Communication Ability: Explaining and presenting
- Problem Solving: Analytical and creative thinking

Usage:
    from app.tasks import (
        TaskService, SkillService,
        TaskType, SkillCategory,
        router
    )
    
    # Create a task
    task_service = TaskService(db)
    task = await task_service.create_task(data)
    
    # Track skills
    skill_service = SkillService(db)
    summary = await skill_service.get_skill_summary(user_id)
"""
from app.tasks.models import (
    # Enums
    TaskType,
    TaskStatus,
    TaskDifficulty,
    SkillCategory,
    SkillLevel,
    
    # Models
    SkillTask,
    TaskAssignment,
    UserSkill,
    SkillHistory,
    SkillAssessment,
    SkillMilestone,
    UserMilestone
)

from app.tasks.schemas import (
    # Enums
    TaskTypeEnum,
    TaskStatusEnum,
    TaskDifficultyEnum,
    SkillCategoryEnum,
    SkillLevelEnum,
    
    # Task schemas
    SkillWeights,
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskAssignRequest,
    TaskSubmissionRequest,
    TaskProgressUpdate,
    HintRequestSchema,
    TaskResponse,
    TaskListResponse,
    TaskAssignmentResponse,
    TaskAssignmentListResponse,
    TaskFeedbackResponse,
    HintResponseSchema,
    
    # Skill schemas
    SkillResponse,
    SkillSummaryResponse,
    SkillHistoryEntry,
    SkillHistoryResponse,
    SkillProgressChart,
    
    # Assessment schemas
    AssessmentQuestion,
    AssessmentStartRequest,
    AssessmentSubmitRequest,
    AssessmentResponse,
    
    # Milestone schemas
    MilestoneResponse,
    UserMilestoneResponse,
    MilestoneProgressResponse,
    
    # Analytics schemas
    TaskAnalytics,
    SkillAnalytics,
    OverallAnalyticsResponse
)

from app.tasks.service import (
    # Utility functions
    calculate_skill_level,
    calculate_task_xp,
    calculate_skill_gain,
    
    # Services
    TaskService,
    SkillService,
    TaskAnalyticsService
)

from app.tasks.api import router

__all__ = [
    # Model Enums
    "TaskType",
    "TaskStatus",
    "TaskDifficulty",
    "SkillCategory",
    "SkillLevel",
    
    # Schema Enums
    "TaskTypeEnum",
    "TaskStatusEnum",
    "TaskDifficultyEnum",
    "SkillCategoryEnum",
    "SkillLevelEnum",
    
    # Models
    "Task",
    "TaskAssignment",
    "UserSkill",
    "SkillHistory",
    "SkillAssessment",
    "SkillMilestone",
    "UserMilestone",
    
    # Task Schemas
    "SkillWeights",
    "TaskCreateRequest",
    "TaskUpdateRequest",
    "TaskAssignRequest",
    "TaskSubmissionRequest",
    "TaskProgressUpdate",
    "HintRequestSchema",
    "TaskResponse",
    "TaskListResponse",
    "TaskAssignmentResponse",
    "TaskAssignmentListResponse",
    "TaskFeedbackResponse",
    "HintResponseSchema",
    
    # Skill Schemas
    "SkillResponse",
    "SkillSummaryResponse",
    "SkillHistoryEntry",
    "SkillHistoryResponse",
    "SkillProgressChart",
    
    # Assessment Schemas
    "AssessmentQuestion",
    "AssessmentStartRequest",
    "AssessmentSubmitRequest",
    "AssessmentResponse",
    
    # Milestone Schemas
    "MilestoneResponse",
    "UserMilestoneResponse",
    "MilestoneProgressResponse",
    
    # Analytics Schemas
    "TaskAnalytics",
    "SkillAnalytics",
    "OverallAnalyticsResponse",
    
    # Utility Functions
    "calculate_skill_level",
    "calculate_task_xp",
    "calculate_skill_gain",
    
    # Services
    "TaskService",
    "SkillService",
    "TaskAnalyticsService",
    
    # Router
    "router"
]
