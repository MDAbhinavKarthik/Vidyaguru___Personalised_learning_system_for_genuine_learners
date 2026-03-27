# VidyaGuru AI Mentor System

> **"विद्या ददाति विनयम्"** - Knowledge gives humility

## Overview

The VidyaGuru AI Mentor is an LLM-powered learning companion that guides learners through a structured 8-phase learning journey while preventing cheating and ensuring genuine understanding.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI MENTOR SYSTEM                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────────┐       │
│  │   Prompts   │───▶│    Engine    │───▶│  Session Manager  │       │
│  │  Templates  │    │   (LLM API)  │    │   (State + Cache) │       │
│  └─────────────┘    └──────────────┘    └───────────────────┘       │
│         │                  │                      │                  │
│         ▼                  ▼                      ▼                  │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────────┐       │
│  │  Cheating   │    │     API      │    │    Database +     │       │
│  │  Detection  │◀──▶│   Endpoints  │◀──▶│      Redis        │       │
│  └─────────────┘    └──────────────┘    └───────────────────┘       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Learning Flow (8 Phases)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   1. TOPIC INTRODUCTION                                              │
│      ↓ Spark curiosity, assess current knowledge                     │
│   2. CONCEPT EXPLANATION                                             │
│      ↓ Socratic method, build understanding                          │
│   3. REAL-WORLD EXAMPLES                                             │
│      ↓ Make abstract concrete, relate to interests                   │
│   4. ANCIENT KNOWLEDGE                                               │
│      ↓ Connect to timeless wisdom (Sanskrit/historical)              │
│   5. PRACTICAL TASK                                                  │
│      ↓ Hands-on coding with verification questions                   │
│   6. COMMUNICATION EXERCISE                                          │
│      ↓ Explain to different audiences                                │
│   7. INDUSTRY CHALLENGE                                              │
│      ↓ Real-world problem with constraints                           │
│   8. REFLECTION                                                      │
│         Consolidate learning, plan next steps                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Capabilities

### 1. Explain Concepts
- Uses Socratic method (questions before answers)
- Adapts to learner's level (beginner → expert)
- Personalizes analogies based on interests
- Builds understanding incrementally

### 2. Ask Questions
- Verification questions to ensure understanding
- "Why" questions over "what" questions
- Progressive hinting system
- Follow-up questions on submissions

### 3. Provide Tasks
- Progressive difficulty
- Anti-cheating elements built-in
- Multiple verification points
- Code review with explanation requirements

### 4. Communication Practice
- Explain to different audiences
- Technical presentation practice
- Interview scenario preparation
- Teaching role exercises

### 5. Motivate Learners
- Streak tracking and XP rewards
- Wisdom quotes integration
- Growth mindset language
- Personalized encouragement

### 6. Prevent Cheating
- Copy-paste detection
- AI-generated content detection
- Response timing analysis
- Pattern deviation detection
- Mandatory explanation requirements

## File Structure

```
backend/app/mentor/
├── __init__.py           # Package exports
├── prompts.py            # Prompt templates and configurations
├── engine.py             # Core LLM integration engine
├── session_manager.py    # Session state management
├── cheating_detection.py # Anti-cheating system
├── schemas.py            # API request/response schemas
└── api.py                # FastAPI endpoints
```

## Prompt Templates

### System Prompt Components

```python
# Master system prompt structure
MASTER_SYSTEM_PROMPT = """
You are VidyaGuru (विद्यागुरु), an AI learning mentor...

## CORE IDENTITY
## TEACHING PRINCIPLES
## COMMUNICATION STYLE (ACRE Framework)
## ANTI-CHEATING AWARENESS

{personality_modifier}  # Socratic, Encouraging, Challenging, etc.
{context_modifier}      # Learner-specific context
"""
```

### Phase Prompts

Each phase has a detailed prompt template:

```python
PHASE_PROMPTS = {
    LearningPhase.TOPIC_INTRODUCTION: """
        ## Your Goals:
        1. Spark curiosity
        2. Assess current knowledge
        3. Connect to interests
        
        ## Response Structure:
        - Hook (intriguing question)
        - Context Setting
        - Knowledge Check (2-3 questions)
        - Journey Preview
        - Engagement Question
    """,
    
    LearningPhase.PRACTICAL_TASK: """
        ## Task Design Principles:
        - Start simple
        - Require understanding (not Googleable)
        - Progressive complexity
        - Anti-cheating elements
        
        ## Task Structure:
        - Context
        - Requirements
        - Part 1: Foundation (Easy)
        - Part 2: Extension (Medium)
        - Part 3: Challenge (Hard)
        - Verification Questions
        - Progressive Hints
    """,
    # ... other phases
}
```

## API Reference

### Session Management

```http
POST /api/v1/mentor/sessions
```
Create or resume a learning session.

**Request:**
```json
{
  "topic": "Python Decorators",
  "personality": "socratic",
  "learner_context": {
    "experience_level": "intermediate",
    "learning_style": "visual",
    "interests": ["web development"]
  },
  "resume_existing": true
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "topic": "Python Decorators",
  "current_phase": "topic_introduction",
  "progress_percentage": 12,
  "mentor_response": {
    "content": "Welcome! Let's explore decorators...",
    "suggestions": ["What are they?", "Show example"],
    "phase": "topic_introduction"
  }
}
```

### Send Message

```http
POST /api/v1/mentor/sessions/{session_id}/messages
```

**Request:**
```json
{
  "message": "I think decorators wrap functions?",
  "request_hint": false
}
```

**Response:**
```json
{
  "content": "You're on the right track! Can you explain what 'wrapping' means in this context?",
  "phase": "concept_explanation",
  "suggestions": ["It modifies behavior", "It adds functionality"],
  "xp_awarded": 5,
  "phase_complete": false,
  "requires_verification": false
}
```

### Submit Task

```http
POST /api/v1/mentor/sessions/{session_id}/submit-task
```

**Request:**
```json
{
  "code": "def my_decorator(func):\n    ...",
  "explanation": "I created a decorator that...",
  "language": "python",
  "alternative_approaches": ["Could also use functools.wraps"]
}
```

### Request Hint

```http
POST /api/v1/mentor/sessions/{session_id}/hint
```

**Request:**
```json
{
  "context": "I'm stuck on the return value",
  "hint_level": 1
}
```

## Cheating Detection

### Detection Methods

| Method | Description | Suspicion Score |
|--------|-------------|-----------------|
| **Timing Analysis** | Fast response + long message | 0.0-0.5 |
| **Content Analysis** | Tutorial patterns, URLs, formatting | 0.0-0.3 |
| **Code Analysis** | Pro-level patterns, docstrings | 0.0-0.35 |
| **Pattern Deviation** | Sudden complexity/length jump | 0.0-0.4 |
| **Plagiarism Check** | Hash matching against submissions | 0.0-1.0 |
| **AI Detection** | AI writing patterns | 0.0-0.6 |

### Suspicion Levels

```python
class SuspicionLevel(Enum):
    NONE = "none"       # < 0.15 - Proceed normally
    LOW = "low"         # < 0.30 - Monitor
    MEDIUM = "medium"   # < 0.50 - Ask clarifying questions
    HIGH = "high"       # < 0.70 - Require verbal explanation
    CRITICAL = "critical" # >= 0.70 - Flag for review
```

### Verification Strategies

When cheating is suspected, the system employs:

1. **Socratic Verification** - "Why" questions about the approach
2. **Modification Challenge** - Request code changes to verify understanding
3. **Audience Explanation** - Explain to non-technical person
4. **Trace Execution** - Walk through code step-by-step

## Integration Example

### Initialize Mentor Engine

```python
from app.mentor import MentorEngine, LLMProvider, LearnerContext, MentorPersonality

# Create engine with OpenAI
engine = MentorEngine(
    provider=LLMProvider.OPENAI,
    model="gpt-4o"
)

# Or with Anthropic
engine = MentorEngine(
    provider=LLMProvider.ANTHROPIC,
    model="claude-3-5-sonnet-20241022"
)
```

### Create Learning Session

```python
from app.mentor import SessionManager, MentorPersonality, LearnerContext

# Initialize session manager
session_manager = SessionManager(db=db_session, redis=redis_client)

# Create learner context
learner = LearnerContext(
    name="Arjun",
    experience_level="intermediate",
    learning_style="visual",
    interests=["web development", "AI"],
    current_streak=5,
    total_xp=1500,
    strengths=["problem solving"],
    areas_to_improve=["system design"]
)

# Create session
session = await session_manager.create_session(
    user_id="user-123",
    topic="Python Decorators",
    personality=MentorPersonality.SOCRATIC,
    learner_context=learner
)
```

### Generate Response

```python
# Generate mentor response
response = await engine.generate_response(
    session=session,
    user_message="I think decorators modify function behavior"
)

print(response.content)            # Mentor's response
print(response.phase)              # Current phase
print(response.suggestions)        # Suggested follow-ups
print(response.xp_awarded)         # XP earned
print(response.requires_verification)  # Cheating suspicion
```

### Handle Task Submission

```python
# Check for cheating
from app.mentor import cheating_detector

analysis = await cheating_detector.analyze_response(
    user_id="user-123",
    message=submission.code + submission.explanation,
    context={
        "phase": "practical_task",
        "experience_level": "intermediate",
        "last_message_time": last_msg_time
    }
)

if analysis.suspicion_level in [SuspicionLevel.HIGH, SuspicionLevel.CRITICAL]:
    # Inject verification
    verification_questions = analysis.verification_questions
    # Ask learner to explain before accepting
```

## Wisdom Quotes Integration

The system includes Sanskrit wisdom quotes for motivational moments:

```python
from app.mentor import get_wisdom_quote

quote = get_wisdom_quote("celebration")
# {
#   "text": "विद्या ददाति विनयम्",
#   "transliteration": "Vidya dadati vinayam",
#   "translation": "Knowledge gives humility",
#   "source": "Sanskrit Proverb"
# }
```

## XP and Progress System

| Phase | XP Reward |
|-------|-----------|
| Topic Introduction | 10 XP |
| Concept Explanation | 25 XP |
| Real-World Examples | 15 XP |
| Ancient Knowledge | 10 XP |
| Practical Task | 50 XP |
| Communication Exercise | 30 XP |
| Industry Challenge | 75 XP |
| Reflection | 20 XP |

**Total per topic: 235 XP**

## Configuration

### Environment Variables

```env
# LLM Providers
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Default Settings
DEFAULT_MENTOR_PERSONALITY=socratic
DEFAULT_LLM_PROVIDER=openai

# Session Settings
SESSION_CACHE_TTL=3600
MAX_HINTS_PER_TASK=3
```

## Testing the Mentor

```python
import asyncio
from app.mentor import MentorEngine, LLMProvider

async def test_mentor():
    engine = MentorEngine(provider=LLMProvider.OPENAI)
    
    session, response = await engine.start_session(
        user_id="test-user",
        topic="Recursion in Python"
    )
    
    print(f"Session started: {session.session_id}")
    print(f"Mentor says: {response.content[:200]}...")
    print(f"Current phase: {response.phase}")
    print(f"Suggestions: {response.suggestions}")

asyncio.run(test_mentor())
```

## Best Practices

1. **Always provide learner context** - Better personalization
2. **Use streaming for long responses** - Better UX
3. **Honor cheating detection** - Don't skip verification
4. **Track session progress** - Resume interrupted sessions
5. **Use appropriate personalities**:
   - Socratic: For conceptual learning
   - Encouraging: For struggling learners
   - Challenging: For advanced learners
   - Analytical: For technical deep-dives
   - Storyteller: For engagement

## License

MIT License - Built with ❤️ for genuine learners
