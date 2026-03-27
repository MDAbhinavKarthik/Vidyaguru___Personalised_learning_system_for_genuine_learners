"""
Industry Challenges Service

Business logic for:
1. Generating industry challenges using LLM
2. Evaluating user solutions
3. Identifying innovative solutions for resume recommendations
"""

import json
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.config import settings
from app.challenges.models import (
    IndustryChallenge,
    ChallengeSolution,
    ResumeHighlight,
    ChallengeCategory,
    ChallengeDifficulty,
    SolutionStatus,
)
from app.challenges.schemas import (
    ChallengeGenerateRequest,
    SolutionSubmitRequest,
    SolutionEvaluationResponse,
    ResumeRecommendation,
)
from app.challenges.prompts import (
    get_challenge_prompt,
    SOLUTION_EVALUATION_PROMPT,
    RESUME_RECOMMENDATION_PROMPT,
    CHALLENGE_HINT_PROMPT,
)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class IndustryChallengeService:
    """Service for managing industry challenges"""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro")
        self.generation_config = genai.GenerationConfig(
            temperature=0.8,
            top_p=0.95,
            max_output_tokens=4096,
        )

    async def generate_challenge(
        self,
        db: Session,
        request: ChallengeGenerateRequest,
    ) -> IndustryChallenge:
        """Generate a new industry challenge using LLM"""
        
        # Get the appropriate prompt based on category
        prompt_template = get_challenge_prompt(request.category.value)
        
        # Format the prompt with parameters
        prompt = prompt_template.format(
            difficulty=request.difficulty.value,
            industry=request.industry or "Technology",
            company_type=request.company_type or "Mid-size tech company",
            focus_areas=", ".join(request.focus_areas) if request.focus_areas else "General",
        )

        # Generate challenge using LLM
        response = await self.model.generate_content_async(
            prompt,
            generation_config=self.generation_config,
        )

        # Parse the JSON response
        try:
            # Extract JSON from response
            response_text = response.text
            # Find JSON in response (handle markdown code blocks)
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text
            
            challenge_data = json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError) as e:
            raise ValueError(f"Failed to parse LLM response: {e}")

        # Calculate XP based on difficulty
        xp_rewards = {
            "beginner": 200,
            "intermediate": 400,
            "advanced": 600,
            "expert": 1000,
        }

        # Create challenge in database
        challenge = IndustryChallenge(
            title=challenge_data["title"],
            category=request.category,
            difficulty=request.difficulty,
            problem_statement=challenge_data["problem_statement"],
            context=challenge_data["context"],
            constraints=challenge_data["constraints"],
            requirements=challenge_data["requirements"],
            evaluation_criteria=challenge_data["evaluation_criteria"],
            expected_concepts=challenge_data["expected_concepts"],
            industry=request.industry or challenge_data.get("industry"),
            company_type=request.company_type or challenge_data.get("company_type"),
            tech_stack_hints=challenge_data.get("tech_stack_hints", []),
            estimated_time_hours=challenge_data.get("estimated_time_hours", 2.0),
            xp_reward=xp_rewards.get(request.difficulty.value, 400),
        )

        db.add(challenge)
        db.commit()
        db.refresh(challenge)

        return challenge

    async def get_challenge(
        self,
        db: Session,
        challenge_id: int,
    ) -> Optional[IndustryChallenge]:
        """Get a challenge by ID"""
        return db.query(IndustryChallenge).filter(
            IndustryChallenge.id == challenge_id
        ).first()

    async def list_challenges(
        self,
        db: Session,
        category: Optional[ChallengeCategory] = None,
        difficulty: Optional[ChallengeDifficulty] = None,
        industry: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[IndustryChallenge], int]:
        """List challenges with filters"""
        query = db.query(IndustryChallenge).filter(
            IndustryChallenge.is_active == True
        )

        if category:
            query = query.filter(IndustryChallenge.category == category)
        if difficulty:
            query = query.filter(IndustryChallenge.difficulty == difficulty)
        if industry:
            query = query.filter(IndustryChallenge.industry.ilike(f"%{industry}%"))

        total = query.count()
        challenges = query.offset((page - 1) * page_size).limit(page_size).all()

        return challenges, total

    async def get_random_challenge(
        self,
        db: Session,
        category: Optional[ChallengeCategory] = None,
        difficulty: Optional[ChallengeDifficulty] = None,
        user_id: Optional[int] = None,
    ) -> Optional[IndustryChallenge]:
        """Get a random challenge, optionally excluding ones user has attempted"""
        query = db.query(IndustryChallenge).filter(
            IndustryChallenge.is_active == True
        )

        if category:
            query = query.filter(IndustryChallenge.category == category)
        if difficulty:
            query = query.filter(IndustryChallenge.difficulty == difficulty)

        # Exclude challenges user has already attempted
        if user_id:
            attempted_ids = db.query(ChallengeSolution.challenge_id).filter(
                ChallengeSolution.user_id == user_id
            ).subquery()
            query = query.filter(~IndustryChallenge.id.in_(attempted_ids))

        # Random selection
        challenge = query.order_by(func.random()).first()
        return challenge


class SolutionEvaluationService:
    """Service for evaluating user solutions"""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro")
        self.generation_config = genai.GenerationConfig(
            temperature=0.3,  # Lower temperature for consistent evaluation
            top_p=0.9,
            max_output_tokens=4096,
        )

    async def submit_solution(
        self,
        db: Session,
        user_id: int,
        request: SolutionSubmitRequest,
    ) -> ChallengeSolution:
        """Submit a solution for evaluation"""
        
        # Get the challenge
        challenge = db.query(IndustryChallenge).filter(
            IndustryChallenge.id == request.challenge_id
        ).first()
        
        if not challenge:
            raise ValueError("Challenge not found")

        # Check for existing solution
        existing = db.query(ChallengeSolution).filter(
            ChallengeSolution.user_id == user_id,
            ChallengeSolution.challenge_id == request.challenge_id,
        ).first()

        if existing and existing.status == SolutionStatus.EVALUATED:
            raise ValueError("You have already submitted a solution for this challenge")

        # Create or update solution
        if existing:
            solution = existing
            solution.solution_text = request.solution_text
            solution.architecture_diagram = request.architecture_diagram
            solution.trade_offs_discussed = request.trade_offs_discussed
            solution.technologies_proposed = request.technologies_proposed
        else:
            solution = ChallengeSolution(
                user_id=user_id,
                challenge_id=request.challenge_id,
                solution_text=request.solution_text,
                architecture_diagram=request.architecture_diagram,
                trade_offs_discussed=request.trade_offs_discussed,
                technologies_proposed=request.technologies_proposed,
            )
            db.add(solution)

        solution.status = SolutionStatus.SUBMITTED
        solution.submitted_at = datetime.utcnow()
        
        db.commit()
        db.refresh(solution)

        # Update challenge attempt count
        challenge.times_attempted += 1
        db.commit()

        return solution

    async def evaluate_solution(
        self,
        db: Session,
        solution_id: int,
    ) -> SolutionEvaluationResponse:
        """Evaluate a submitted solution using LLM"""
        
        # Get solution and challenge
        solution = db.query(ChallengeSolution).filter(
            ChallengeSolution.id == solution_id
        ).first()
        
        if not solution:
            raise ValueError("Solution not found")

        challenge = solution.challenge

        # Update status
        solution.status = SolutionStatus.UNDER_REVIEW
        db.commit()

        # Format evaluation prompt
        prompt = SOLUTION_EVALUATION_PROMPT.format(
            challenge_title=challenge.title,
            challenge_category=challenge.category.value,
            challenge_difficulty=challenge.difficulty.value,
            problem_statement=challenge.problem_statement,
            context=challenge.context,
            constraints=json.dumps(challenge.constraints, indent=2),
            requirements=json.dumps(challenge.requirements, indent=2),
            evaluation_criteria=json.dumps(challenge.evaluation_criteria, indent=2),
            expected_concepts=json.dumps(challenge.expected_concepts, indent=2),
            solution_text=solution.solution_text,
            architecture_diagram=solution.architecture_diagram or "Not provided",
            trade_offs=json.dumps(solution.trade_offs_discussed or [], indent=2),
            technologies=json.dumps(solution.technologies_proposed or [], indent=2),
        )

        # Get LLM evaluation
        response = await self.model.generate_content_async(
            prompt,
            generation_config=self.generation_config,
        )

        # Parse response
        try:
            response_text = response.text
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text
            
            eval_data = json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError) as e:
            raise ValueError(f"Failed to parse evaluation response: {e}")

        # Calculate XP earned
        base_xp = challenge.xp_reward
        xp_multiplier = eval_data.get("xp_multiplier", 1.0)
        score_multiplier = eval_data["overall_score"] / 100
        xp_earned = int(base_xp * xp_multiplier * score_multiplier)

        # Update solution with evaluation
        solution.status = SolutionStatus.EVALUATED
        solution.ai_feedback = eval_data["ai_feedback"]
        solution.strengths = eval_data["strengths"]
        solution.areas_for_improvement = eval_data["areas_for_improvement"]
        solution.innovation_score = eval_data["innovation_score"]
        solution.practicality_score = eval_data["practicality_score"]
        solution.completeness_score = eval_data["completeness_score"]
        solution.overall_score = eval_data["overall_score"]
        solution.is_resume_worthy = eval_data["is_resume_worthy"]
        solution.xp_earned = xp_earned
        solution.evaluated_at = datetime.utcnow()

        db.commit()

        # Generate resume recommendation if worthy
        resume_recommendation = None
        if solution.is_resume_worthy:
            solution.status = SolutionStatus.RESUME_WORTHY
            resume_recommendation = await self._generate_resume_recommendation(
                db, solution, challenge
            )
            db.commit()

        # Update challenge success rate
        evaluated_solutions = db.query(ChallengeSolution).filter(
            ChallengeSolution.challenge_id == challenge.id,
            ChallengeSolution.status == SolutionStatus.EVALUATED,
        ).all()
        
        if evaluated_solutions:
            passing_count = sum(1 for s in evaluated_solutions if s.overall_score >= 70)
            challenge.success_rate = (passing_count / len(evaluated_solutions)) * 100
            db.commit()

        return SolutionEvaluationResponse(
            solution_id=solution.id,
            status=solution.status,
            innovation_score=solution.innovation_score,
            practicality_score=solution.practicality_score,
            completeness_score=solution.completeness_score,
            overall_score=solution.overall_score,
            ai_feedback=solution.ai_feedback,
            strengths=solution.strengths,
            areas_for_improvement=solution.areas_for_improvement,
            is_resume_worthy=solution.is_resume_worthy,
            resume_recommendation=resume_recommendation,
            xp_earned=solution.xp_earned,
        )

    async def _generate_resume_recommendation(
        self,
        db: Session,
        solution: ChallengeSolution,
        challenge: IndustryChallenge,
    ) -> ResumeRecommendation:
        """Generate resume bullet points for an innovative solution"""
        
        prompt = RESUME_RECOMMENDATION_PROMPT.format(
            challenge_title=challenge.title,
            challenge_category=challenge.category.value,
            industry=challenge.industry or "Technology",
            innovation_score=solution.innovation_score,
            practicality_score=solution.practicality_score,
            overall_score=solution.overall_score,
            strengths=json.dumps(solution.strengths, indent=2),
            technologies=json.dumps(solution.technologies_proposed or [], indent=2),
        )

        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.4,
                max_output_tokens=2048,
            ),
        )

        try:
            response_text = response.text
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text
            
            resume_data = json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError) as e:
            # Fallback if parsing fails
            resume_data = {
                "headline": f"Designed innovative solution for {challenge.title}",
                "bullet_points": [
                    f"Architected {challenge.category.value.replace('_', ' ')} solution demonstrating advanced technical skills",
                    "Demonstrated strong problem-solving and system design capabilities",
                ],
                "skills_demonstrated": solution.technologies_proposed or ["Problem Solving"],
                "impact_statement": "Demonstrated production-ready engineering skills",
                "recommendation_reason": "Solution showed innovation and practical thinking",
            }

        # Save to solution
        solution.resume_bullet_points = resume_data["bullet_points"]
        solution.resume_recommendation_reason = resume_data["recommendation_reason"]

        # Create resume highlight record
        highlight = ResumeHighlight(
            user_id=solution.user_id,
            solution_id=solution.id,
            headline=resume_data["headline"],
            bullet_points=resume_data["bullet_points"],
            skills_demonstrated=resume_data["skills_demonstrated"],
            impact_statement=resume_data["impact_statement"],
        )
        db.add(highlight)

        return ResumeRecommendation(
            headline=resume_data["headline"],
            bullet_points=resume_data["bullet_points"],
            skills_demonstrated=resume_data["skills_demonstrated"],
            impact_statement=resume_data["impact_statement"],
            recommendation_reason=resume_data["recommendation_reason"],
        )

    async def get_hint(
        self,
        db: Session,
        challenge_id: int,
        current_attempt: str,
        struggle_area: str,
    ) -> Dict[str, str]:
        """Generate a Socratic hint for a stuck learner"""
        
        challenge = db.query(IndustryChallenge).filter(
            IndustryChallenge.id == challenge_id
        ).first()
        
        if not challenge:
            raise ValueError("Challenge not found")

        prompt = CHALLENGE_HINT_PROMPT.format(
            challenge_title=challenge.title,
            problem_statement=challenge.problem_statement,
            current_attempt=current_attempt,
            struggle_area=struggle_area,
        )

        response = await self.model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024,
            ),
        )

        try:
            response_text = response.text
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text
            
            return json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError):
            return {
                "guiding_question": "What's the first thing that happens when a user interacts with this system?",
                "concept_hint": "Think about the flow of data through the system",
                "analogy": "Like water flowing through pipes, data needs to know where to go",
                "encouragement": "You're asking the right questions - that's the first step to a great solution!",
            }


class ResumeHighlightService:
    """Service for managing resume highlights"""

    async def get_user_highlights(
        self,
        db: Session,
        user_id: int,
    ) -> List[ResumeHighlight]:
        """Get all resume highlights for a user"""
        return db.query(ResumeHighlight).filter(
            ResumeHighlight.user_id == user_id
        ).order_by(ResumeHighlight.created_at.desc()).all()

    async def mark_added_to_resume(
        self,
        db: Session,
        highlight_id: int,
        user_id: int,
    ) -> ResumeHighlight:
        """Mark a highlight as added to resume"""
        highlight = db.query(ResumeHighlight).filter(
            ResumeHighlight.id == highlight_id,
            ResumeHighlight.user_id == user_id,
        ).first()
        
        if not highlight:
            raise ValueError("Highlight not found")

        highlight.added_to_resume = True
        highlight.exported_at = datetime.utcnow()
        db.commit()
        db.refresh(highlight)

        return highlight

    async def export_highlights(
        self,
        db: Session,
        user_id: int,
    ) -> str:
        """Export all highlights as formatted text for resume"""
        highlights = await self.get_user_highlights(db, user_id)
        
        if not highlights:
            return "No resume highlights available yet. Complete some challenges!"

        export_text = "# Resume Highlights from VidyaGuru Challenges\n\n"
        
        for h in highlights:
            export_text += f"## {h.headline}\n\n"
            for bullet in h.bullet_points:
                export_text += f"• {bullet}\n"
            export_text += f"\n**Skills:** {', '.join(h.skills_demonstrated)}\n"
            export_text += f"**Impact:** {h.impact_statement}\n\n"
            export_text += "---\n\n"

        return export_text


# Service instances
challenge_service = IndustryChallengeService()
evaluation_service = SolutionEvaluationService()
resume_service = ResumeHighlightService()
