"""
VidyaGuru AI Mentor Engine
Core LLM integration and learning flow orchestration
"""
import json
import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import re

from pydantic import BaseModel, Field
import google.generativeai as genai

from app.config import settings
from app.mentor.prompts import (
    LearningPhase,
    MentorPersonality,
    LearnerContext,
    build_system_prompt,
    build_phase_prompt,
    get_wisdom_quote,
    get_motivation_message,
    ANTI_CHEATING_PROMPTS
)


# =============================================================================
# DATA MODELS
# =============================================================================

class LLMProvider(str, Enum):
    GEMINI = "gemini"


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """A single message in the conversation"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    phase: Optional[LearningPhase] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LearningSession(BaseModel):
    """A learning session with conversation history"""
    session_id: str
    user_id: str
    topic: str
    current_phase: LearningPhase = LearningPhase.TOPIC_INTRODUCTION
    personality: MentorPersonality = MentorPersonality.SOCRATIC
    messages: List[Message] = Field(default_factory=list)
    learner_context: Optional[LearnerContext] = None
    phase_progress: Dict[str, bool] = Field(default_factory=dict)
    xp_earned: int = 0
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MentorResponse(BaseModel):
    """Response from the mentor"""
    content: str
    phase: LearningPhase
    suggestions: List[str] = Field(default_factory=list)
    xp_awarded: int = 0
    phase_complete: bool = False
    next_phase: Optional[LearningPhase] = None
    requires_verification: bool = False
    wisdom_quote: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CheatingIndicator(BaseModel):
    """Indicators of potential cheating or copy-paste"""
    suspicion_level: float  # 0.0 to 1.0
    indicators: List[str]
    recommended_action: str
    verification_questions: List[str]


# =============================================================================
# MENTOR ENGINE
# =============================================================================

class MentorEngine:
    """
    Core AI Mentor Engine that orchestrates learning flow
    and manages LLM interactions
    """
    
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.GEMINI,
        model: Optional[str] = None
    ):
        self.provider = provider
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = model or settings.LLM_MODEL or "gemini-2.0-flash"
        self.client = genai.GenerativeModel(self.model)
        
        # Phase transition rules
        self.phase_order = [
            LearningPhase.TOPIC_INTRODUCTION,
            LearningPhase.CONCEPT_EXPLANATION,
            LearningPhase.REAL_WORLD_EXAMPLES,
            LearningPhase.ANCIENT_KNOWLEDGE,
            LearningPhase.PRACTICAL_TASK,
            LearningPhase.COMMUNICATION_EXERCISE,
            LearningPhase.INDUSTRY_CHALLENGE,
            LearningPhase.REFLECTION
        ]
        
        # XP values for each phase
        self.phase_xp = {
            LearningPhase.TOPIC_INTRODUCTION: 10,
            LearningPhase.CONCEPT_EXPLANATION: 25,
            LearningPhase.REAL_WORLD_EXAMPLES: 15,
            LearningPhase.ANCIENT_KNOWLEDGE: 10,
            LearningPhase.PRACTICAL_TASK: 50,
            LearningPhase.COMMUNICATION_EXERCISE: 30,
            LearningPhase.INDUSTRY_CHALLENGE: 75,
            LearningPhase.REFLECTION: 20
        }
    
    # -------------------------------------------------------------------------
    # CORE LLM INTERACTION
    # -------------------------------------------------------------------------
    
    async def generate_response(
        self,
        session: LearningSession,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> MentorResponse:
        """Generate a mentor response for the given user message"""
        
        # Build messages for LLM
        messages = self._build_llm_messages(session, user_message)
        
        # Check for cheating indicators
        cheating_check = await self._analyze_for_cheating(user_message, session)
        
        # If high suspicion, inject verification prompt
        if cheating_check.suspicion_level > 0.7:
            messages = self._inject_verification_prompt(messages, cheating_check)
        
        # Generate LLM response
        response_text = await self._call_gemini(messages, temperature, max_tokens)
        
        # Analyze response to determine phase progress
        phase_complete = await self._check_phase_completion(session, user_message, response_text)
        
        # Calculate XP
        xp_awarded = 0
        if phase_complete:
            xp_awarded = self.phase_xp.get(session.current_phase, 10)
        
        # Determine next phase
        next_phase = None
        if phase_complete:
            next_phase = self._get_next_phase(session.current_phase)
        
        # Add wisdom quote if transitioning phases or in reflection
        wisdom_quote = None
        if phase_complete or session.current_phase == LearningPhase.REFLECTION:
            wisdom_quote = get_wisdom_quote()
        
        return MentorResponse(
            content=response_text,
            phase=session.current_phase,
            suggestions=self._generate_suggestions(session, response_text),
            xp_awarded=xp_awarded,
            phase_complete=phase_complete,
            next_phase=next_phase,
            requires_verification=cheating_check.suspicion_level > 0.5,
            wisdom_quote=wisdom_quote,
            metadata={
                "cheating_suspicion": cheating_check.suspicion_level,
                "model_used": self.model,
                "tokens_used": len(response_text.split()) * 2  # Rough estimate
            }
        )
    
    async def generate_response_stream(
        self,
        session: LearningSession,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming mentor response"""
        
        messages = self._build_llm_messages(session, user_message)
        
        async for chunk in self._stream_gemini(messages, temperature, max_tokens):
            yield chunk
    
    # -------------------------------------------------------------------------
    # LLM PROVIDER IMPLEMENTATIONS
    # -------------------------------------------------------------------------
    
    async def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Call Google Gemini API"""
        # Convert messages to Gemini format
        system_instruction = ""
        chat_history = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                chat_history.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                chat_history.append({"role": "model", "parts": [msg["content"]]})
        
        # Create model with system instruction if provided
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        model = genai.GenerativeModel(
            self.model,
            system_instruction=system_instruction if system_instruction else None,
            generation_config=generation_config
        )
        
        # Start chat with history
        if chat_history:
            # If there's history, use chat mode
            chat = model.start_chat(history=chat_history[:-1] if len(chat_history) > 1 else [])
            last_message = chat_history[-1]["parts"][0] if chat_history else ""
            response = await asyncio.to_thread(chat.send_message, last_message)
        else:
            response = await asyncio.to_thread(model.generate_content, "Hello")
        
        return response.text
    
    async def _stream_gemini(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """Stream from Google Gemini API"""
        # Convert messages to Gemini format
        system_instruction = ""
        chat_history = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                chat_history.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                chat_history.append({"role": "model", "parts": [msg["content"]]})
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        model = genai.GenerativeModel(
            self.model,
            system_instruction=system_instruction if system_instruction else None,
            generation_config=generation_config
        )
        
        chat = model.start_chat(history=chat_history[:-1] if len(chat_history) > 1 else [])
        last_message = chat_history[-1]["parts"][0] if chat_history else ""
        
        # Stream response
        response = chat.send_message(last_message, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    # -------------------------------------------------------------------------
    # MESSAGE BUILDING
    # -------------------------------------------------------------------------
    
    def _build_llm_messages(
        self,
        session: LearningSession,
        user_message: str
    ) -> List[Dict[str, str]]:
        """Build the message list for LLM"""
        messages = []
        
        # System prompt
        system_prompt = build_system_prompt(
            personality=session.personality,
            learner_context=session.learner_context
        )
        
        # Add phase-specific instructions
        phase_prompt = build_phase_prompt(
            phase=session.current_phase,
            topic=session.topic,
            concept=session.metadata.get("current_concept", session.topic),
            difficulty=session.metadata.get("difficulty", "medium"),
            experience_level=session.learner_context.experience_level if session.learner_context else "intermediate",
            learning_style=session.learner_context.learning_style if session.learner_context else "mixed",
            interests=", ".join(session.learner_context.interests) if session.learner_context else "technology",
            learner_interests=", ".join(session.learner_context.interests) if session.learner_context else "technology",
            industry=session.metadata.get("industry", "technology"),
            xp_earned=session.xp_earned,
            current_streak=session.learner_context.current_streak if session.learner_context else 0
        )
        
        messages.append({
            "role": "system",
            "content": f"{system_prompt}\n\n---\n\n{phase_prompt}"
        })
        
        # Add conversation history (last 20 messages for context)
        for msg in session.messages[-20:]:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _inject_verification_prompt(
        self,
        messages: List[Dict[str, str]],
        cheating_check: CheatingIndicator
    ) -> List[Dict[str, str]]:
        """Inject anti-cheating verification into the prompt"""
        verification_instruction = f"""

## IMPORTANT: Verification Required

The learner's response shows potential indicators of copy-paste or lack of genuine understanding:
{', '.join(cheating_check.indicators)}

Before accepting this response, you MUST:
1. Ask the learner to explain their solution in their own words
2. Ask at least one of these verification questions:
   {chr(10).join(f'- {q}' for q in cheating_check.verification_questions)}
3. Be warm and non-accusatory - frame it as "deepening understanding"
4. Only proceed once genuine comprehension is demonstrated

Suspicion Level: {cheating_check.suspicion_level:.0%}
Recommended Action: {cheating_check.recommended_action}
"""
        
        # Append to system message
        messages[0]["content"] += verification_instruction
        return messages
    
    # -------------------------------------------------------------------------
    # CHEATING DETECTION
    # -------------------------------------------------------------------------
    
    async def _analyze_for_cheating(
        self,
        user_message: str,
        session: LearningSession
    ) -> CheatingIndicator:
        """Analyze user message for potential cheating indicators"""
        indicators = []
        suspicion_level = 0.0
        
        # Check for code in early phases (shouldn't have code yet)
        if session.current_phase in [
            LearningPhase.TOPIC_INTRODUCTION,
            LearningPhase.CONCEPT_EXPLANATION
        ] and self._contains_substantial_code(user_message):
            indicators.append("Code submitted before task phase")
            suspicion_level += 0.3
        
        # Check for overly perfect/complete solutions
        if len(user_message) > 500 and self._is_overly_polished(user_message):
            indicators.append("Response appears overly polished")
            suspicion_level += 0.2
        
        # Check response time (if available)
        if session.messages:
            last_assistant_msg = next(
                (m for m in reversed(session.messages) if m.role == MessageRole.ASSISTANT),
                None
            )
            if last_assistant_msg:
                time_diff = datetime.utcnow() - last_assistant_msg.timestamp
                # If complex question answered very quickly
                if time_diff < timedelta(seconds=30) and len(user_message) > 300:
                    indicators.append("Complex response submitted very quickly")
                    suspicion_level += 0.25
        
        # Check for format patterns suggesting copy-paste
        if self._has_copy_paste_patterns(user_message):
            indicators.append("Formatting suggests copy-paste")
            suspicion_level += 0.2
        
        # Check for sudden complexity jump
        if self._complexity_jump(user_message, session):
            indicators.append("Sudden complexity increase from previous responses")
            suspicion_level += 0.15
        
        # Check for common tutorial/documentation patterns
        if self._matches_tutorial_patterns(user_message):
            indicators.append("Matches common tutorial/documentation patterns")
            suspicion_level += 0.2
        
        # Cap suspicion level
        suspicion_level = min(suspicion_level, 1.0)
        
        # Generate verification questions
        verification_questions = self._generate_verification_questions(
            user_message,
            session.current_phase
        )
        
        # Determine recommended action
        if suspicion_level > 0.7:
            recommended_action = "Strong verification required before proceeding"
        elif suspicion_level > 0.5:
            recommended_action = "Ask clarifying questions to verify understanding"
        elif suspicion_level > 0.3:
            recommended_action = "Monitor for additional indicators"
        else:
            recommended_action = "Proceed normally"
        
        return CheatingIndicator(
            suspicion_level=suspicion_level,
            indicators=indicators,
            recommended_action=recommended_action,
            verification_questions=verification_questions
        )
    
    def _contains_substantial_code(self, text: str) -> bool:
        """Check if message contains substantial code"""
        code_patterns = [
            r'```[\s\S]{100,}```',  # Fenced code blocks with 100+ chars
            r'def \w+\([^)]*\):[\s\S]{50,}',  # Python functions
            r'function \w+\([^)]*\)\s*{[\s\S]{50,}}',  # JS functions
            r'class \w+[\s\S]{100,}',  # Class definitions
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _is_overly_polished(self, text: str) -> bool:
        """Check if response is suspiciously polished"""
        polish_indicators = [
            r'^\s*(Step \d+:|First,|Second,|Third,|Finally,)',  # Numbered steps
            r'(?:Here\'s|Below is|The following)',  # Tutorial language
            r'(?:comprehensive|complete|full) (?:solution|implementation|code)',
            r'(?:error handling|edge cases|corner cases)[\s\S]*included',
        ]
        
        matches = sum(1 for p in polish_indicators if re.search(p, text, re.MULTILINE))
        return matches >= 2
    
    def _has_copy_paste_patterns(self, text: str) -> bool:
        """Check for copy-paste formatting patterns"""
        patterns = [
            r'^\s+$',  # Lines with only whitespace (weird indentation)
            r'\t{3,}',  # Excessive tabs
            r'[^\x00-\x7F]{3,}',  # Non-ASCII characters (could be from rich text)
            r'(?:stackoverflow|github|medium|tutorial)\.com',  # Source URLs left in
        ]
        
        matches = sum(1 for p in patterns if re.search(p, text))
        return matches >= 1
    
    def _complexity_jump(self, message: str, session: LearningSession) -> bool:
        """Check if there's a sudden jump in response complexity"""
        if len(session.messages) < 3:
            return False
        
        # Get user's previous messages
        prev_user_msgs = [
            m for m in session.messages 
            if m.role == MessageRole.USER
        ][-3:]
        
        if not prev_user_msgs:
            return False
        
        # Compare average length
        avg_prev_len = sum(len(m.content) for m in prev_user_msgs) / len(prev_user_msgs)
        current_len = len(message)
        
        # If current is 3x longer than average, flag it
        return current_len > avg_prev_len * 3 and current_len > 200
    
    def _matches_tutorial_patterns(self, text: str) -> bool:
        """Check if text matches common tutorial/docs patterns"""
        tutorial_phrases = [
            "in this tutorial",
            "let's see how",
            "as shown below",
            "the output will be",
            "run the following",
            "you should see",
            "congratulations! you have",
            "copy and paste"
        ]
        
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in tutorial_phrases)
    
    def _generate_verification_questions(
        self,
        user_message: str,
        phase: LearningPhase
    ) -> List[str]:
        """Generate verification questions based on context"""
        questions = []
        
        # Generic questions
        questions.append("Can you explain your thinking process in your own words?")
        questions.append("What alternative approaches did you consider?")
        
        # Phase-specific questions
        if phase == LearningPhase.PRACTICAL_TASK:
            questions.extend([
                "What would happen if we changed one of the requirements?",
                "How would you modify this to handle edge case X?",
                "What's the time complexity of your solution?",
                "Can you trace through a specific example step by step?"
            ])
        elif phase == LearningPhase.CONCEPT_EXPLANATION:
            questions.extend([
                "Can you give me a real-world example of this concept?",
                "How would you explain this to someone with no technical background?",
                "What's the key insight that makes this concept work?"
            ])
        elif phase == LearningPhase.INDUSTRY_CHALLENGE:
            questions.extend([
                "What trade-offs did you make in this design?",
                "How would this scale to 10x the users?",
                "What's the biggest risk in this approach?"
            ])
        
        return questions[:4]  # Return top 4 questions
    
    # -------------------------------------------------------------------------
    # PHASE MANAGEMENT
    # -------------------------------------------------------------------------
    
    async def _check_phase_completion(
        self,
        session: LearningSession,
        user_message: str,
        assistant_response: str
    ) -> bool:
        """Check if the current phase is complete"""
        phase = session.current_phase
        
        # Phase-specific completion criteria
        if phase == LearningPhase.TOPIC_INTRODUCTION:
            # Complete when learner has engaged with intro questions
            return self._has_engaged_intro(session)
        
        elif phase == LearningPhase.CONCEPT_EXPLANATION:
            # Complete when learner demonstrates understanding
            return self._has_demonstrated_understanding(user_message, session)
        
        elif phase == LearningPhase.REAL_WORLD_EXAMPLES:
            # Complete after learner has provided own example
            return self._has_provided_example(user_message)
        
        elif phase == LearningPhase.ANCIENT_KNOWLEDGE:
            # Complete after acknowledgment and reflection
            return len(session.messages) >= 2 and "system" not in user_message.lower()
        
        elif phase == LearningPhase.PRACTICAL_TASK:
            # Complete when task is solved and verified
            return self._task_completed_and_verified(user_message, session)
        
        elif phase == LearningPhase.COMMUNICATION_EXERCISE:
            # Complete when communication exercise done
            return self._communication_exercise_done(session)
        
        elif phase == LearningPhase.INDUSTRY_CHALLENGE:
            # Complete when challenge solved with explanation
            return self._industry_challenge_solved(user_message, session)
        
        elif phase == LearningPhase.REFLECTION:
            # Complete after self-assessment
            return self._reflection_complete(session)
        
        return False
    
    def _has_engaged_intro(self, session: LearningSession) -> bool:
        """Check if learner has engaged with introduction"""
        user_msgs = [m for m in session.messages if m.role == MessageRole.USER]
        # At least 2 exchanges
        return len(user_msgs) >= 2
    
    def _has_demonstrated_understanding(self, message: str, session: LearningSession) -> bool:
        """Check if learner has demonstrated understanding"""
        # Look for explanation markers
        explanation_markers = [
            "because", "so that", "this means", "in other words",
            "for example", "specifically", "the reason is", "which is"
        ]
        
        message_lower = message.lower()
        has_explanation = any(marker in message_lower for marker in explanation_markers)
        has_length = len(message) > 100
        
        # Check exchanges count
        user_msgs = [m for m in session.messages if m.role == MessageRole.USER]
        enough_exchanges = len(user_msgs) >= 3
        
        return has_explanation and has_length and enough_exchanges
    
    def _has_provided_example(self, message: str) -> bool:
        """Check if learner has provided their own example"""
        example_markers = [
            "example", "instance", "like when", "such as",
            "reminds me of", "similar to", "just like"
        ]
        return any(marker in message.lower() for marker in example_markers) and len(message) > 50
    
    def _task_completed_and_verified(self, message: str, session: LearningSession) -> bool:
        """Check if practical task is completed and verified"""
        # Needs code submission
        has_code = self._contains_substantial_code(message)
        
        # Needs explanation
        has_explanation = len(message) > 200 and "because" in message.lower()
        
        # Needs multiple exchanges (verification)
        user_msgs = [m for m in session.messages if m.role == MessageRole.USER]
        enough_exchanges = len(user_msgs) >= 4
        
        return has_code and has_explanation and enough_exchanges
    
    def _communication_exercise_done(self, session: LearningSession) -> bool:
        """Check if communication exercise is complete"""
        user_msgs = [m for m in session.messages if m.role == MessageRole.USER]
        
        # Need at least 2 substantial messages
        substantial_msgs = [m for m in user_msgs if len(m.content) > 100]
        return len(substantial_msgs) >= 2
    
    def _industry_challenge_solved(self, message: str, session: LearningSession) -> bool:
        """Check if industry challenge is solved"""
        # Similar to task but needs more depth
        has_code = self._contains_substantial_code(message)
        
        # Needs trade-off discussion
        trade_off_markers = ["trade-off", "tradeoff", "pros and cons", "advantage", "disadvantage", "instead of"]
        has_trade_offs = any(m in message.lower() for m in trade_off_markers)
        
        user_msgs = [m for m in session.messages if m.role == MessageRole.USER]
        enough_exchanges = len(user_msgs) >= 3
        
        return (has_code or has_trade_offs) and len(message) > 300 and enough_exchanges
    
    def _reflection_complete(self, session: LearningSession) -> bool:
        """Check if reflection is complete"""
        user_msgs = [m for m in session.messages if m.role == MessageRole.USER]
        
        # Need self-assessment
        assessment_markers = ["confident", "learned", "understand", "challenging", "enjoyed", "struggle"]
        last_msgs = user_msgs[-2:] if len(user_msgs) >= 2 else user_msgs
        
        has_reflection = any(
            any(marker in m.content.lower() for marker in assessment_markers)
            for m in last_msgs
        )
        
        return has_reflection and len(user_msgs) >= 2
    
    def _get_next_phase(self, current_phase: LearningPhase) -> Optional[LearningPhase]:
        """Get the next phase in the learning flow"""
        try:
            current_index = self.phase_order.index(current_phase)
            if current_index < len(self.phase_order) - 1:
                return self.phase_order[current_index + 1]
        except ValueError:
            pass
        return None
    
    def _generate_suggestions(
        self,
        session: LearningSession,
        response: str
    ) -> List[str]:
        """Generate clickable suggestions for the learner"""
        phase = session.current_phase
        suggestions = []
        
        if phase == LearningPhase.TOPIC_INTRODUCTION:
            suggestions = [
                "I'd like to know more about this",
                "What are the prerequisites?",
                "How is this used in real projects?"
            ]
        elif phase == LearningPhase.CONCEPT_EXPLANATION:
            suggestions = [
                "Can you explain with an analogy?",
                "I don't understand this part",
                "Can you give me an example?",
                "What's the intuition behind this?"
            ]
        elif phase == LearningPhase.REAL_WORLD_EXAMPLES:
            suggestions = [
                "Show me another example",
                "How do big companies use this?",
                "I've seen something similar in..."
            ]
        elif phase == LearningPhase.ANCIENT_KNOWLEDGE:
            suggestions = [
                "That's fascinating!",
                "Tell me more about this history",
                "How does this relate to today?"
            ]
        elif phase == LearningPhase.PRACTICAL_TASK:
            suggestions = [
                "I need a hint",
                "Is my approach correct?",
                "I'm stuck on...",
                "Review my solution"
            ]
        elif phase == LearningPhase.COMMUNICATION_EXERCISE:
            suggestions = [
                "Let me try explaining",
                "How can I improve my explanation?",
                "Give me another scenario"
            ]
        elif phase == LearningPhase.INDUSTRY_CHALLENGE:
            suggestions = [
                "I need clarification on requirements",
                "What constraints should I consider?",
                "Review my design",
                "What are the edge cases?"
            ]
        elif phase == LearningPhase.REFLECTION:
            suggestions = [
                "I feel confident about...",
                "I'm still unclear about...",
                "What should I learn next?"
            ]
        
        return suggestions
    
    # -------------------------------------------------------------------------
    # PHASE TRANSITIONS
    # -------------------------------------------------------------------------
    
    async def transition_phase(
        self,
        session: LearningSession,
        target_phase: Optional[LearningPhase] = None
    ) -> MentorResponse:
        """Transition to a new learning phase"""
        if target_phase:
            new_phase = target_phase
        else:
            new_phase = self._get_next_phase(session.current_phase)
        
        if not new_phase:
            # Learning session complete
            return await self._generate_completion_message(session)
        
        # Generate transition message
        transition_prompt = f"""
The learner has completed the {session.current_phase.value} phase.
Now transition them to the {new_phase.value} phase.

Generate an appropriate transition message that:
1. Acknowledges completion of previous phase
2. Introduces the new phase
3. Gets them started on the new activity
4. Maintains motivation and momentum
"""
        
        messages = self._build_llm_messages(session, transition_prompt)
        
        response_text = await self._call_gemini(messages, 0.7, 1500)
        
        return MentorResponse(
            content=response_text,
            phase=new_phase,
            phase_complete=False,
            next_phase=None,
            xp_awarded=self.phase_xp.get(session.current_phase, 0),
            suggestions=self._generate_suggestions(session, response_text),
            wisdom_quote=get_wisdom_quote()
        )
    
    async def _generate_completion_message(
        self,
        session: LearningSession
    ) -> MentorResponse:
        """Generate a completion message for the entire session"""
        completion_prompt = f"""
The learner has completed ALL phases of learning about "{session.topic}".

Generate a celebratory completion message that:
1. Celebrates their achievement authentically
2. Summarizes what they learned
3. Highlights their growth through the session
4. Includes a wisdom quote (Sanskrit if appropriate)
5. Suggests next steps for continued learning
6. Awards final XP: {session.xp_earned + self.phase_xp.get(LearningPhase.REFLECTION, 20)}

Make it memorable and motivating!
"""
        
        messages = self._build_llm_messages(session, completion_prompt)
        
        response_text = await self._call_gemini(messages, 0.8, 2000)
        
        return MentorResponse(
            content=response_text,
            phase=LearningPhase.REFLECTION,
            phase_complete=True,
            next_phase=None,
            xp_awarded=self.phase_xp.get(LearningPhase.REFLECTION, 20),
            suggestions=["Start a new topic", "Review what I learned", "Take a challenge"],
            wisdom_quote=get_wisdom_quote("celebration"),
            metadata={"session_complete": True}
        )
    
    # -------------------------------------------------------------------------
    # UTILITY METHODS
    # -------------------------------------------------------------------------
    
    async def start_session(
        self,
        user_id: str,
        topic: str,
        learner_context: Optional[LearnerContext] = None,
        personality: MentorPersonality = MentorPersonality.SOCRATIC
    ) -> tuple[LearningSession, MentorResponse]:
        """Start a new learning session"""
        import uuid
        
        session = LearningSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            topic=topic,
            current_phase=LearningPhase.TOPIC_INTRODUCTION,
            personality=personality,
            learner_context=learner_context,
            metadata={"current_concept": topic}
        )
        
        # Generate introduction
        intro_prompt = f"Start a new learning session for topic: {topic}"
        response = await self.generate_response(session, intro_prompt)
        
        # Add messages to session
        session.messages.append(Message(
            role=MessageRole.USER,
            content=intro_prompt,
            phase=LearningPhase.TOPIC_INTRODUCTION
        ))
        session.messages.append(Message(
            role=MessageRole.ASSISTANT,
            content=response.content,
            phase=LearningPhase.TOPIC_INTRODUCTION
        ))
        
        return session, response
    
    def update_session(
        self,
        session: LearningSession,
        user_message: str,
        assistant_response: MentorResponse
    ) -> LearningSession:
        """Update session with new messages and state"""
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
        if assistant_response.phase_complete and assistant_response.next_phase:
            session.phase_progress[session.current_phase.value] = True
            session.current_phase = assistant_response.next_phase
        
        # Update last activity
        session.last_activity = datetime.utcnow()
        
        return session
