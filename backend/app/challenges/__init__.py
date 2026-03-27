"""
Industry Challenges Module

Generates real-world industry challenges:
- System Design Problems
- Scalability Challenges
- Algorithm Optimization
- Software Architecture Problems

Features:
- AI-generated challenges based on real industry scenarios
- Solution evaluation with detailed feedback
- Resume recommendations for innovative solutions
"""

from app.challenges.api import router as challenges_router
from app.challenges.models import (
    IndustryChallenge,
    ChallengeSolution,
    ResumeHighlight,
    ChallengeCategory,
    ChallengeDifficulty,
    SolutionStatus,
)
from app.challenges.service import (
    challenge_service,
    evaluation_service,
    resume_service,
)

__all__ = [
    "challenges_router",
    "IndustryChallenge",
    "ChallengeSolution",
    "ResumeHighlight",
    "ChallengeCategory",
    "ChallengeDifficulty",
    "SolutionStatus",
    "challenge_service",
    "evaluation_service",
    "resume_service",
]
