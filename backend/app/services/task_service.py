"""
Task Service
Task management and submission handling
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.task import Task, Submission, TaskStatus, TaskType, VerificationStatus
from app.schemas.task import (
    TaskCreate, TaskUpdate, SubmissionCreate,
    TaskResponse, TaskDetailResponse, SubmissionResponse,
    TaskEvaluationResult, HintResponse,
    TaskListResponse, DailyTasksResponse
)
from app.dependencies import PaginationParams


class TaskService:
    """Task management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_tasks(
        self,
        user_id: UUID,
        pagination: PaginationParams,
        status_filter: Optional[TaskStatus] = None,
        type_filter: Optional[TaskType] = None
    ) -> TaskListResponse:
        """Get user's tasks with pagination"""
        query = select(Task).where(Task.user_id == user_id)
        
        if status_filter:
            query = query.where(Task.status == status_filter)
        if type_filter:
            query = query.where(Task.task_type == type_filter)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)
        
        # Get paginated results
        query = query.order_by(Task.created_at.desc())
        query = query.offset(pagination.offset).limit(pagination.size)
        
        result = await self.db.execute(query)
        tasks = result.scalars().all()
        
        return TaskListResponse(
            items=[TaskResponse.model_validate(t) for t in tasks],
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
    
    async def get_task(self, task_id: UUID, user_id: UUID) -> Task:
        """Get task by ID"""
        result = await self.db.execute(
            select(Task)
            .options(selectinload(Task.submissions))
            .where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return task
    
    async def create_task(self, user_id: UUID, data: TaskCreate) -> Task:
        """Create a new task"""
        task = Task(
            user_id=user_id,
            module_id=data.module_id,
            title=data.title,
            description=data.description,
            instructions=data.instructions,
            task_type=data.task_type,
            difficulty=data.difficulty,
            deadline=data.deadline,
            max_attempts=data.max_attempts,
            xp_reward=data.xp_reward,
            hints=data.hints or [],
            template_code=data.template_code,
            test_cases=data.test_cases
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def update_task(self, task_id: UUID, user_id: UUID, data: TaskUpdate) -> Task:
        """Update task"""
        task = await self.get_task(task_id, user_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def delete_task(self, task_id: UUID, user_id: UUID) -> dict:
        """Delete task"""
        task = await self.get_task(task_id, user_id)
        
        await self.db.delete(task)
        await self.db.commit()
        
        return {"message": "Task deleted successfully"}
    
    async def start_task(self, task_id: UUID, user_id: UUID) -> Task:
        """Start working on a task"""
        task = await self.get_task(task_id, user_id)
        
        if task.status not in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task cannot be started"
            )
        
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def submit_task(self, user_id: UUID, data: SubmissionCreate) -> TaskEvaluationResult:
        """Submit solution for a task"""
        task = await self.get_task(data.task_id, user_id)
        
        # Check attempts
        if task.current_attempts >= task.max_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum attempts exceeded"
            )
        
        # Create submission
        submission = Submission(
            task_id=task.id,
            user_id=user_id,
            content=data.content,
            language=data.language,
            time_spent_seconds=data.time_spent_seconds,
            typing_pattern_data=data.typing_pattern_data,
            attempt_number=task.current_attempts + 1
        )
        
        # Evaluate submission
        evaluation = await self._evaluate_submission(task, submission)
        
        submission.score = evaluation["score"]
        submission.feedback = evaluation["feedback"]
        submission.ai_feedback = evaluation["ai_feedback"]
        submission.plagiarism_score = evaluation.get("plagiarism_score")
        submission.verification_status = evaluation["verification_status"]
        submission.tests_passed = evaluation.get("tests_passed")
        submission.tests_total = evaluation.get("tests_total")
        submission.evaluated_at = datetime.utcnow()
        
        self.db.add(submission)
        
        # Update task
        task.current_attempts += 1
        
        if evaluation["passed"]:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
        else:
            task.status = TaskStatus.SUBMITTED
        
        await self.db.commit()
        await self.db.refresh(submission)
        
        return TaskEvaluationResult(
            task_id=task.id,
            submission_id=submission.id,
            score=submission.score,
            max_score=submission.max_score,
            passed=evaluation["passed"],
            feedback=submission.feedback,
            ai_feedback=submission.ai_feedback,
            verification_status=submission.verification_status,
            xp_earned=task.xp_reward if evaluation["passed"] else 0,
            tests_passed=submission.tests_passed,
            tests_total=submission.tests_total
        )
    
    async def _evaluate_submission(self, task: Task, submission: Submission) -> dict:
        """Evaluate a submission (simplified)"""
        # In production, this would run tests, check for plagiarism, etc.
        
        score = 75.0  # Simplified scoring
        passed = True
        tests_passed = None
        tests_total = None
        
        # If task has test cases, run them
        if task.test_cases:
            tests_total = len(task.test_cases.get("cases", []))
            tests_passed = int(tests_total * 0.8)  # Simplified
            score = (tests_passed / tests_total) * 100 if tests_total > 0 else 100
            passed = tests_passed >= tests_total * 0.6  # 60% to pass
        
        # Generate AI feedback
        ai_feedback = self._generate_feedback(task, submission.content)
        
        return {
            "score": score,
            "passed": passed,
            "feedback": {
                "general": "Good attempt!" if passed else "Keep trying!",
                "improvements": ["Consider edge cases", "Add comments to your code"]
            },
            "ai_feedback": ai_feedback,
            "verification_status": VerificationStatus.VERIFIED if passed else VerificationStatus.PENDING,
            "tests_passed": tests_passed,
            "tests_total": tests_total,
            "plagiarism_score": 0.0
        }
    
    def _generate_feedback(self, task: Task, content: str) -> str:
        """Generate AI feedback (simplified)"""
        return f"""
## Feedback for: {task.title}

Your submission has been reviewed. Here are some observations:

1. **Code Structure**: Your code follows good practices.
2. **Logic**: The approach is sound.
3. **Suggestions**: Consider adding more comments and handling edge cases.

Keep learning and improving! 🚀
"""
    
    async def get_hint(self, task_id: UUID, user_id: UUID, hint_index: Optional[int] = None) -> HintResponse:
        """Get hint for a task"""
        task = await self.get_task(task_id, user_id)
        
        if not task.hints:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hints available for this task"
            )
        
        # Determine which hint to show
        if hint_index is not None:
            if hint_index >= len(task.hints):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid hint index"
                )
            idx = hint_index
        else:
            idx = min(task.hints_used, len(task.hints) - 1)
        
        # Update hints used
        if idx >= task.hints_used:
            task.hints_used = idx + 1
        
        await self.db.commit()
        
        # XP penalty for using hints
        xp_penalty = (idx + 1) * 2
        
        return HintResponse(
            hint=task.hints[idx],
            hint_index=idx,
            total_hints=len(task.hints),
            xp_penalty=xp_penalty
        )
    
    async def get_daily_tasks(self, user_id: UUID) -> DailyTasksResponse:
        """Get today's tasks"""
        today = datetime.utcnow().date()
        
        result = await self.db.execute(
            select(Task)
            .where(
                Task.user_id == user_id,
                Task.task_type == TaskType.DAILY,
                func.date(Task.created_at) == today
            )
        )
        tasks = result.scalars().all()
        
        # If no daily tasks, generate some
        if not tasks:
            tasks = await self._generate_daily_tasks(user_id)
        
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        total_xp = sum(t.xp_reward for t in tasks)
        
        return DailyTasksResponse(
            date=datetime.utcnow(),
            tasks=[TaskResponse.model_validate(t) for t in tasks],
            completed_count=completed,
            total_count=len(tasks),
            xp_available=total_xp
        )
    
    async def _generate_daily_tasks(self, user_id: UUID) -> List[Task]:
        """Generate daily tasks for user"""
        from app.models.task import TaskDifficulty
        
        daily_tasks = [
            {
                "title": "Review Yesterday's Learning",
                "description": "Spend time reviewing what you learned yesterday",
                "task_type": TaskType.DAILY,
                "difficulty": TaskDifficulty.EASY,
                "xp_reward": 10
            },
            {
                "title": "Complete One Module",
                "description": "Complete at least one module from your learning path",
                "task_type": TaskType.DAILY,
                "difficulty": TaskDifficulty.MEDIUM,
                "xp_reward": 20
            },
            {
                "title": "Practice Problem",
                "description": "Solve at least one practice problem",
                "task_type": TaskType.DAILY,
                "difficulty": TaskDifficulty.MEDIUM,
                "xp_reward": 15
            }
        ]
        
        created_tasks = []
        for task_data in daily_tasks:
            task = Task(
                user_id=user_id,
                **task_data
            )
            self.db.add(task)
            created_tasks.append(task)
        
        await self.db.commit()
        
        for task in created_tasks:
            await self.db.refresh(task)
        
        return created_tasks
