"""
AI Mentor Service
LLM-powered mentor interactions
"""
from typing import Optional, List, AsyncGenerator
from uuid import UUID
from datetime import datetime
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.config import settings
from app.models.conversation import Conversation, Message, MessageRole, ConversationContext
from app.models.user import UserProfile
from app.schemas.mentor import (
    ChatRequest, ChatResponse, ChatMessageResponse,
    ConversationResponse, ConversationDetailResponse, ConversationListResponse,
    ConceptExplanationRequest, ConceptExplanationResponse,
    CodeReviewRequest, CodeReviewResponse,
    QuizGenerateRequest, QuizResponse, QuizQuestion,
    MentorSuggestion
)
from app.dependencies import PaginationParams


# System prompt for the AI mentor
MENTOR_SYSTEM_PROMPT = """You are VidyaGuru (विद्यागुरु), an AI learning mentor designed to promote genuine understanding over memorization.

CORE TEACHING PRINCIPLES:
1. Use the Socratic method - guide through questions rather than giving direct answers
2. Assess current understanding before explaining
3. Break complex topics into digestible chunks
4. Use analogies relevant to the student's interests
5. Celebrate effort and progress
6. Identify and address misconceptions gently
7. Encourage learners to verbalize their thinking

RESPONSE FRAMEWORK:
- Acknowledge: Recognize what the student understands
- Question: Ask probing questions to deepen thinking
- Guide: Provide hints and direction, not complete answers
- Connect: Link to previously learned concepts
- Challenge: Push for deeper exploration when ready

COMMUNICATION STYLE:
- Warm but intellectually challenging
- Patient with genuine struggles
- Encouraging of curiosity
- Use examples from Indian and global contexts when relevant
- Include wisdom from philosophical traditions when appropriate

When reviewing code:
- Point out issues without fixing them directly
- Ask "What do you think happens when...?"
- Suggest areas to research

For concept explanations:
- Start with what the student already knows
- Build understanding layer by layer
- Use visual analogies when helpful
- End with a reflection question

Remember: Your goal is to create independent thinkers, not dependent answer-seekers."""


WISDOM_QUOTES = [
    {"text": "विद्या ददाति विनयम्", "translation": "Knowledge gives humility", "source": "Sanskrit Proverb"},
    {"text": "अभ्यासेन तु कौन्तेय वैराग्येण च गृह्यते", "translation": "Through practice and detachment, it is attained", "source": "Bhagavad Gita 6.35"},
    {"text": "श्रद्धावान् लभते ज्ञानम्", "translation": "One who has faith attains knowledge", "source": "Bhagavad Gita 4.39"},
    {"text": "योगः कर्मसु कौशलम्", "translation": "Yoga is skill in action", "source": "Bhagavad Gita 2.50"},
    {"text": "उद्यमेन हि सिध्यन्ति कार्याणि न मनोरथैः", "translation": "Success comes through effort, not mere desire", "source": "Hitopadesha"},
]


class MentorService:
    """AI Mentor service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._llm_client = None
    
    async def _get_llm_client(self):
        """Get or create LLM client"""
        if self._llm_client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._llm_client = genai.GenerativeModel(settings.LLM_MODEL or "gemini-2.0-flash")
            except ImportError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="LLM service not available"
                )
        return self._llm_client
    
    async def chat(self, user_id: UUID, data: ChatRequest) -> ChatResponse:
        """Send message to AI mentor"""
        # Get or create conversation
        if data.conversation_id:
            conversation = await self._get_conversation(data.conversation_id, user_id)
        else:
            conversation = await self._create_conversation(
                user_id,
                data.context_type,
                data.related_module_id,
                data.related_task_id
            )
        
        # Get user profile for personalization
        profile = await self._get_user_profile(user_id)
        
        # Build context
        context = await self._build_context(conversation, profile, data)
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=data.message,
            attachments={"code": data.code_context} if data.code_context else None
        )
        self.db.add(user_message)
        await self.db.flush()
        
        # Generate AI response
        ai_response = await self._generate_response(context, data.message)
        
        # Save AI message
        ai_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=ai_response["content"],
            tokens_used=ai_response.get("tokens_used", 0)
        )
        self.db.add(ai_message)
        
        # Update conversation
        conversation.last_message_at = datetime.utcnow()
        conversation.total_tokens_used += ai_response.get("tokens_used", 0)
        
        # Auto-generate title if first message
        if not conversation.title:
            conversation.title = self._generate_title(data.message)
        
        await self.db.commit()
        await self.db.refresh(ai_message)
        
        # Get wisdom quote if requested
        wisdom_quote = None
        if data.include_wisdom:
            import random
            wisdom_quote = random.choice(WISDOM_QUOTES)
        
        return ChatResponse(
            conversation_id=conversation.id,
            message=ChatMessageResponse(
                id=ai_message.id,
                conversation_id=conversation.id,
                role=ai_message.role,
                content=ai_message.content,
                tokens_used=ai_message.tokens_used,
                metadata=ai_message.message_metadata,
                attachments=ai_message.attachments,
                user_rating=ai_message.user_rating,
                created_at=ai_message.created_at
            ),
            suggestions=ai_response.get("suggestions", []),
            related_resources=ai_response.get("resources", []),
            wisdom_quote=wisdom_quote,
            follow_up_questions=ai_response.get("follow_up", [])
        )
    
    async def _generate_response(self, context: List[dict], message: str) -> dict:
        """Generate AI response using LLM"""
        try:
            client = await self._get_llm_client()
            
            # Build message history for context
            conversation_history = []
            
            # Add system prompt as first message
            conversation_history.append(MENTOR_SYSTEM_PROMPT)
            
            # Add context messages
            for msg in context:
                if msg.get("role") != "system":
                    # Format messages for Gemini
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        conversation_history.append(f"User: {content}")
                    elif role == "assistant":
                        conversation_history.append(f"Mentor: {content}")
            
            # Add current user message
            conversation_history.append(f"User: {message}")
            
            # Join all history into a single prompt
            formatted_prompt = "\n\n".join(conversation_history)
            
            # Call Google Gemini API with correct interface
            response = client.generate_content(
                formatted_prompt,
                generation_config={
                    "max_output_tokens": settings.LLM_MAX_TOKENS,
                    "temperature": settings.LLM_TEMPERATURE,
                }
            )
            
            content = response.text if hasattr(response, 'text') else str(response)
            
            # Estimate tokens (Gemini API doesn't always return token counts)
            tokens_used = len(content.split()) * 1.3  # Rough estimation
            
            # Generate follow-up questions
            follow_up = self._generate_follow_up_questions(content)
            
            return {
                "content": content,
                "tokens_used": int(tokens_used),
                "suggestions": [],
                "resources": [],
                "follow_up": follow_up
            }
            
        except Exception as e:
            # Log error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"LLM generation failed: {str(e)}")
            
            # Fallback response
            return {
                "content": self._get_fallback_response(message),
                "tokens_used": 0,
                "suggestions": [],
                "resources": [],
                "follow_up": ["Can you tell me more about what you're trying to learn?"]
            }
    
    def _get_fallback_response(self, message: str) -> str:
        """Get fallback response when LLM is unavailable"""
        return f"""Thank you for your question! I'm currently experiencing some technical difficulties connecting to my knowledge base.

In the meantime, here are some suggestions:
1. Try breaking down your question into smaller parts
2. Review the related module content
3. Check the documentation or resources provided

I'll be back to full capacity soon. Your learning journey matters! 🙏

*"अभ्यासेन तु कौन्तेय वैराग्येण च गृह्यते" - Through practice and perseverance, mastery is achieved.*"""
    
    def _generate_follow_up_questions(self, response: str) -> List[str]:
        """Generate follow-up questions based on response"""
        return [
            "Can you explain your understanding in your own words?",
            "What aspects would you like to explore further?",
            "How does this connect to what you learned before?"
        ]
    
    def _generate_title(self, message: str) -> str:
        """Generate conversation title from first message"""
        # Take first 50 chars or first sentence
        title = message[:50]
        if "?" in title:
            title = title.split("?")[0] + "?"
        elif len(message) > 50:
            title += "..."
        return title
    
    async def _build_context(self, conversation: Conversation, profile: Optional[UserProfile], data: ChatRequest) -> List[dict]:
        """Build context from conversation history"""
        # Get recent messages
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(10)
        )
        messages = result.scalars().all()
        
        context = []
        
        # Add personalization context
        if profile:
            context.append({
                "role": "system",
                "content": f"Student profile: Learning style - {profile.learning_style}, Level - {profile.experience_level}, Interests - {', '.join(profile.interests or [])}"
            })
        
        # Add conversation history (reversed to chronological order)
        for msg in reversed(messages):
            context.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        return context
    
    async def _get_conversation(self, conversation_id: UUID, user_id: UUID) -> Conversation:
        """Get conversation by ID"""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return conversation
    
    async def _create_conversation(
        self,
        user_id: UUID,
        context_type: ConversationContext,
        module_id: Optional[UUID] = None,
        task_id: Optional[UUID] = None
    ) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            context_type=context_type,
            related_module_id=module_id,
            related_task_id=task_id,
            model_used=settings.LLM_MODEL
        )
        
        self.db.add(conversation)
        await self.db.flush()
        
        return conversation
    
    async def _get_user_profile(self, user_id: UUID) -> Optional[UserProfile]:
        """Get user profile"""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_conversations(self, user_id: UUID, pagination: PaginationParams) -> ConversationListResponse:
        """Get user's conversations"""
        query = select(Conversation).where(
            Conversation.user_id == user_id,
            Conversation.is_archived == False
        )
        
        # Count
        total = await self.db.scalar(select(func.count()).select_from(query.subquery()))
        
        # Paginate
        query = query.order_by(Conversation.last_message_at.desc())
        query = query.offset(pagination.offset).limit(pagination.size)
        
        result = await self.db.execute(query)
        conversations = result.scalars().all()
        
        return ConversationListResponse(
            items=[ConversationResponse.model_validate(c) for c in conversations],
            total=total,
            page=pagination.page,
            size=pagination.size
        )
    
    async def get_conversation_detail(self, conversation_id: UUID, user_id: UUID) -> ConversationDetailResponse:
        """Get conversation with messages"""
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return ConversationDetailResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            context_type=conversation.context_type,
            related_module_id=conversation.related_module_id,
            related_task_id=conversation.related_task_id,
            total_tokens_used=conversation.total_tokens_used,
            summary=conversation.summary,
            model_used=conversation.model_used,
            is_archived=conversation.is_archived,
            created_at=conversation.created_at,
            last_message_at=conversation.last_message_at,
            messages=[ChatMessageResponse.model_validate(m) for m in conversation.messages]
        )
    
    async def delete_conversation(self, conversation_id: UUID, user_id: UUID) -> dict:
        """Delete (archive) conversation"""
        conversation = await self._get_conversation(conversation_id, user_id)
        conversation.is_archived = True
        
        await self.db.commit()
        
        return {"message": "Conversation archived"}
    
    async def explain_concept(self, user_id: UUID, data: ConceptExplanationRequest) -> ConceptExplanationResponse:
        """Get detailed concept explanation"""
        profile = await self._get_user_profile(user_id)
        
        prompt = f"""Explain the concept: {data.concept}
        
Student's current understanding: {data.current_understanding or 'Not specified'}
Preferred explanation style: {data.preferred_style or 'step-by-step'}
Difficulty level: {data.difficulty_level}

Please provide:
1. A clear explanation appropriate for the level
2. 2-3 real-world examples
3. Helpful analogies
4. Related concepts to explore
5. 3 quiz questions to test understanding

Remember to use the Socratic method and encourage thinking."""

        try:
            client = await self._get_llm_client()
            
            response = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": MENTOR_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            return ConceptExplanationResponse(
                concept=data.concept,
                explanation=content,
                examples=["Example based on the explanation"],
                analogies=["Analogy from the explanation"],
                related_concepts=["Related topic 1", "Related topic 2"],
                quiz_questions=[
                    {"question": "Test question 1", "type": "short_answer"},
                    {"question": "Test question 2", "type": "multiple_choice"}
                ],
                wisdom_connection="विद्या ददाति विनयम् - Knowledge gives humility"
            )
            
        except Exception:
            return ConceptExplanationResponse(
                concept=data.concept,
                explanation=f"I'd be happy to explain {data.concept}. Let me break it down step by step...",
                examples=["Please ask for specific examples"],
                analogies=["Think of it like..."],
                related_concepts=["Explore related topics"],
                quiz_questions=[],
                wisdom_connection="श्रद्धावान् लभते ज्ञानम् - One who has faith attains knowledge"
            )
    
    async def review_code(self, user_id: UUID, data: CodeReviewRequest) -> CodeReviewResponse:
        """Review code and provide feedback"""
        prompt = f"""Review this {data.language} code:

```{data.language}
{data.code}
```

Context: {data.context or 'General code review'}
Focus areas: {', '.join(data.focus_areas) if data.focus_areas else 'All aspects'}

Please provide:
1. Overall rating (1-10)
2. Summary of code quality
3. List of issues found
4. Improvement suggestions
5. Key learning points

Remember: Guide the student to find issues themselves through questions."""

        try:
            client = await self._get_llm_client()
            
            response = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": MENTOR_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            
            return CodeReviewResponse(
                overall_rating=7.5,
                summary=content,
                issues=[{"type": "suggestion", "description": "See detailed review"}],
                suggestions=[{"area": "general", "suggestion": "Review the detailed feedback"}],
                improved_code=None,
                learning_points=["Focus on readability", "Consider edge cases"]
            )
            
        except Exception:
            return CodeReviewResponse(
                overall_rating=0,
                summary="I'll review your code. First, let me ask: What is this code trying to accomplish?",
                issues=[],
                suggestions=[{"area": "approach", "suggestion": "Walk me through your logic"}],
                improved_code=None,
                learning_points=["Understanding the problem is the first step"]
            )
    
    async def generate_quiz(self, user_id: UUID, data: QuizGenerateRequest) -> QuizResponse:
        """Generate a quiz on a topic"""
        import uuid
        
        # Generate quiz questions (simplified - would use LLM in production)
        questions = []
        for i in range(data.num_questions):
            q_type = data.question_types[i % len(data.question_types)]
            
            question = QuizQuestion(
                id=uuid.uuid4(),
                question=f"Question {i+1} about {data.topic}",
                question_type=q_type,
                options=["Option A", "Option B", "Option C", "Option D"] if q_type == "multiple_choice" else None,
                difficulty=data.difficulty,
                topic=data.topic
            )
            questions.append(question)
        
        return QuizResponse(
            quiz_id=uuid.uuid4(),
            topic=data.topic,
            questions=questions,
            time_limit_minutes=data.num_questions * 2
        )
    
    async def get_suggestions(self, user_id: UUID) -> List[MentorSuggestion]:
        """Get personalized suggestions"""
        suggestions = [
            MentorSuggestion(
                suggestion_type="continue_learning",
                title="Continue Your Learning Path",
                description="Pick up where you left off in your current module",
                priority=1
            ),
            MentorSuggestion(
                suggestion_type="daily_challenge",
                title="Today's Challenge",
                description="Test your skills with a daily coding challenge",
                priority=2
            ),
            MentorSuggestion(
                suggestion_type="review",
                title="Review Time",
                description="Revisit concepts from earlier this week for better retention",
                priority=3
            )
        ]
        
        return suggestions
    
    async def rate_message(self, message_id: UUID, user_id: UUID, rating: int, feedback: Optional[str] = None) -> dict:
        """Rate a message"""
        result = await self.db.execute(
            select(Message)
            .join(Conversation)
            .where(
                Message.id == message_id,
                Conversation.user_id == user_id
            )
        )
        message = result.scalar_one_or_none()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        message.user_rating = rating
        if feedback:
            message.message_metadata = message.message_metadata or {}
            message.message_metadata["user_feedback"] = feedback
        
        await self.db.commit()
        
        return {"message": "Thank you for your feedback!"}
