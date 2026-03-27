# VidyaGuru Learning Engine

## Overview

The Learning Engine is the core component that controls the flow of educational content through 8 sequential stages. It ensures genuine learning by enforcing strict progression requirements that prevent easy skipping.

## The 8 Learning Stages

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LEARNING JOURNEY STAGES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐     │
│   │  1. INTRODUCTION │───▶│  2. EXPLANATION  │───▶│  3. APPLICATION  │     │
│   │     (10 XP)      │    │     (25 XP)      │    │     (15 XP)      │     │
│   │  2 interactions  │    │  3 interactions  │    │  2 interactions  │     │
│   │  30 seconds      │    │  120 seconds     │    │  60 seconds      │     │
│   └──────────────────┘    │  + verification  │    └──────────────────┘     │
│                           └──────────────────┘                              │
│                                                              │              │
│   ┌──────────────────┐    ┌──────────────────┐              ▼              │
│   │ 6. COMMUNICATION │◀───│  5. PRACTICAL    │◀──┌──────────────────┐     │
│   │     (30 XP)      │    │     (50 XP)      │   │ 4. ANCIENT       │     │
│   │  3 interactions  │    │  4 interactions  │   │     (10 XP)      │     │
│   │  180 seconds     │    │  300 seconds     │   │  2 interactions  │     │
│   │  + explanation   │    │  + submission    │   │  60 seconds      │     │
│   │  + verification  │    │  + explanation   │   └──────────────────┘     │
│   └──────────────────┘    │  + verification  │                             │
│           │               └──────────────────┘                              │
│           ▼                                                                 │
│   ┌──────────────────┐    ┌──────────────────┐                             │
│   │  7. INDUSTRY     │───▶│  8. REFLECTION   │                             │
│   │     (75 XP)      │    │     (20 XP)      │                             │
│   │  4 interactions  │    │  2 interactions  │                             │
│   │  600 seconds     │    │  120 seconds     │                             │
│   │  + submission    │    │  + explanation   │                             │
│   │  + explanation   │    └──────────────────┘                             │
│   │  + verification  │                                                      │
│   └──────────────────┘                                      TOTAL: 235 XP  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Stage Details

### Stage 1: Concept Introduction (10 XP)
**Purpose**: Initial exposure to the topic, building curiosity

| Requirement | Value |
|-------------|-------|
| Minimum Interactions | 2 |
| Minimum Time | 30 seconds |
| Minimum Word Count | 20 words |
| Requires Submission | No |
| Requires Verification | No |

**Mentor Prompt Focus**:
- Welcome learner to the topic
- Gauge current understanding
- Create curiosity and engagement
- Provide high-level overview

---

### Stage 2: Detailed Explanation (25 XP)
**Purpose**: Deep dive into concepts with comprehension verification

| Requirement | Value |
|-------------|-------|
| Minimum Interactions | 3 |
| Minimum Time | 120 seconds |
| Minimum Word Count | 50 words |
| Requires Submission | No |
| Requires Verification | ✅ Yes |

**Verification Questions**: 2-3 questions to confirm understanding

---

### Stage 3: Real-World Application (15 XP)
**Purpose**: Connect theory to practical, real-world contexts

| Requirement | Value |
|-------------|-------|
| Minimum Interactions | 2 |
| Minimum Time | 60 seconds |
| Minimum Word Count | 30 words |
| Requires Submission | No |
| Requires Verification | No |

---

### Stage 4: Ancient Knowledge (10 XP)
**Purpose**: Historical and cultural insights from Indian heritage

| Requirement | Value |
|-------------|-------|
| Minimum Interactions | 2 |
| Minimum Time | 60 seconds |
| Minimum Word Count | 30 words |
| Requires Submission | No |
| Requires Verification | No |

**Cultural Integration**:
- Sanskrit terms and meanings
- Relevant Vedic/classical references
- Historical applications of concepts

---

### Stage 5: Practical Task (50 XP) ⭐ Major Milestone
**Purpose**: Hands-on implementation with guided assistance

| Requirement | Value |
|-------------|-------|
| Minimum Interactions | 4 |
| Minimum Time | 300 seconds (5 min) |
| Minimum Word Count | 100 words |
| Requires Submission | ✅ Yes |
| Requires Explanation | ✅ Yes |
| Requires Verification | ✅ Yes |

**Task Flow**:
1. Present a coding challenge
2. Guide without giving answers
3. Review submission
4. Require explanation of approach
5. Verify understanding

---

### Stage 6: Communication Task (30 XP)
**Purpose**: Teach-back to solidify understanding

| Requirement | Value |
|-------------|-------|
| Minimum Interactions | 3 |
| Minimum Time | 180 seconds (3 min) |
| Minimum Word Count | 75 words |
| Requires Submission | No |
| Requires Explanation | ✅ Yes |
| Requires Verification | ✅ Yes |

**Approach**: "Explain like I'm a beginner" or "Explain to a colleague"

---

### Stage 7: Industry Challenge (75 XP) ⭐ Major Milestone
**Purpose**: Real-world problem from actual industry scenarios

| Requirement | Value |
|-------------|-------|
| Minimum Interactions | 4 |
| Minimum Time | 600 seconds (10 min) |
| Minimum Word Count | 150 words |
| Requires Submission | ✅ Yes |
| Requires Explanation | ✅ Yes |
| Requires Verification | ✅ Yes |

**Focus Areas**:
- Scalability considerations
- Edge cases and error handling
- Best practices implementation
- Real production constraints

---

### Stage 8: Reflection Summary (20 XP)
**Purpose**: Consolidate learning and plan next steps

| Requirement | Value |
|-------------|-------|
| Minimum Interactions | 2 |
| Minimum Time | 120 seconds |
| Minimum Word Count | 50 words |
| Requires Submission | No |
| Requires Explanation | ✅ Yes |
| Requires Verification | No |

**Outcome**:
- Summary of key learnings
- Identification of gaps
- Next topic recommendations

---

## Anti-Skip Mechanism

### How It Works

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         ADVANCEMENT VALIDATION                              │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   User requests → ┌─────────────────────────────────────────┐              │
│   advancement     │         Check Requirements              │              │
│                   │  ┌───────────────────────────────────┐  │              │
│                   │  │ ✓ Minimum interactions met?       │  │              │
│                   │  │ ✓ Minimum time spent?             │  │              │
│                   │  │ ✓ Minimum word count?             │  │              │
│                   │  │ ✓ Submission provided? (if req)   │  │              │
│                   │  │ ✓ Explanation given? (if req)     │  │              │
│                   │  │ ✓ Verification passed? (if req)   │  │              │
│                   │  └───────────────────────────────────┘  │              │
│                   └─────────────┬───────────┬───────────────┘              │
│                                 │           │                               │
│                          All met?     Not all met?                         │
│                                 │           │                               │
│                                 ▼           ▼                               │
│                           ┌─────────┐  ┌───────────────┐                   │
│                           │ ADVANCE │  │ BLOCK + Show  │                   │
│                           │ TO NEXT │  │ missing reqs  │                   │
│                           │  STAGE  │  └───────────────┘                   │
│                           └─────────┘                                       │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Example: Trying to Skip Stage 5 (Practical Task)

```python
# User has: 2 interactions, 60 seconds time

can_advance, unmet = learning_engine.can_advance_stage(session)

# Result:
#   can_advance = False
#   unmet = [
#       "Need 2 more interactions (have 2, need 4)",
#       "Need to spend 240 more seconds (spent 60, need 300)",
#       "Need to provide more text (wrote 45 words, need 100)",
#       "Submission required for this stage",
#       "Explanation of your approach required",
#       "Must pass verification questions"
#   ]
```

### Admin Override (Emergency Use Only)

Admins can force advancement with a **50% XP penalty**:

```python
# Force advancement (admin only)
result = learning_engine.advance_to_next_stage(session, force=True)

# Result:
#   - Stage advanced
#   - XP for skipped stage = max_xp * 0.5 (penalty)
#   - Warning logged
```

---

## XP System

### XP Rewards by Stage

| Stage | Normal XP | Forced Skip XP (50% penalty) |
|-------|-----------|------------------------------|
| Introduction | 10 | 5 |
| Explanation | 25 | 12 |
| Application | 15 | 7 |
| Ancient Knowledge | 10 | 5 |
| Practical Task | 50 | 25 |
| Communication | 30 | 15 |
| Industry Challenge | 75 | 37 |
| Reflection | 20 | 10 |
| **TOTAL** | **235** | **116 (minimum)** |

### Bonus XP Opportunities

- **Speed Bonus**: Complete stage 20% faster than average → +10% XP
- **First Try**: Pass verification on first attempt → +5% XP
- **Streak Bonus**: Complete 3+ sessions in a week → +15% XP

---

## API Endpoints

### Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/learning/sessions` | Create new session |
| GET | `/learning/sessions` | List user's sessions |
| GET | `/learning/sessions/{id}` | Get session details |
| DELETE | `/learning/sessions/{id}` | Delete session |

### Stage Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/learning/sessions/{id}/current-stage` | Get current stage content |
| GET | `/learning/sessions/{id}/progress` | Get detailed progress |
| POST | `/learning/sessions/{id}/interact` | Record interaction |
| POST | `/learning/sessions/{id}/submit` | Submit task solution |
| POST | `/learning/sessions/{id}/verify` | Answer verification |
| POST | `/learning/sessions/{id}/advance` | Advance to next stage |
| POST | `/learning/sessions/{id}/hint` | Request hint (-5 XP) |
| POST | `/learning/sessions/{id}/complete` | Complete session |

---

## Integration with Mentor System

The Learning Engine works with the AI Mentor:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Learning Engine │────▶│   AI Mentor     │────▶│    User         │
│                 │     │                 │     │                 │
│ - Stage control │     │ - Socratic mode │     │ - Receives      │
│ - Requirements  │     │ - Hints only    │     │   guidance      │
│ - XP tracking   │     │ - Verification  │     │ - Must engage   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

Each stage provides the mentor with:
- Stage-specific prompt template
- Current requirements
- User's progress
- Cheating detection context

---

## Usage Example

```python
from app.learning_engine import learning_engine, LearningStage

# 1. Create a learning session
session = learning_engine.create_session(
    user_id="user_123",
    topic="Python",
    concept="Decorators",
    difficulty="intermediate"
)

# 2. User interacts (repeats until requirements met)
learning_engine.record_interaction(
    session,
    user_message="What are decorators?",
    mentor_response="Decorators are a design pattern..."
)

# 3. Check if can advance
can_advance, unmet = learning_engine.can_advance_stage(session)
print(f"Can advance: {can_advance}")
print(f"Missing: {unmet}")

# 4. Advance when ready
if can_advance:
    success, message, new_stage = learning_engine.advance_to_next_stage(session)
    print(f"Now at: {new_stage.value}")

# 5. Complete session after all stages
result = learning_engine.complete_session(session)
print(f"Total XP: {result['summary']['total_xp']}")
```

---

## Database Schema Reference

The Learning Engine uses these tables:

```sql
-- Learning Sessions
CREATE TABLE learning_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    topic VARCHAR(255) NOT NULL,
    concept VARCHAR(255),
    difficulty difficulty_level DEFAULT 'intermediate',
    current_stage VARCHAR(50) NOT NULL,
    total_xp INTEGER DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    is_complete BOOLEAN DEFAULT FALSE,
    is_paused BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Stage Progress
CREATE TABLE stage_progress (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES learning_sessions(id),
    stage VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    interactions INTEGER DEFAULT 0,
    time_spent_seconds INTEGER DEFAULT 0,
    total_words INTEGER DEFAULT 0,
    submissions JSONB DEFAULT '[]',
    xp_earned INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);
```

---

## Configuration

Environment variables:

```env
# Learning Engine
LEARNING_ENGINE_MIN_INTERACTION_LENGTH=10
LEARNING_ENGINE_MAX_SESSIONS_PER_USER=50
LEARNING_ENGINE_SESSION_TIMEOUT_HOURS=24
LEARNING_ENGINE_FORCE_ADVANCE_PENALTY=0.5
LEARNING_ENGINE_HINT_PENALTY=5
```

---

## Best Practices

### For Learners
1. **Engage genuinely** - The system rewards actual learning
2. **Take your time** - Rushing triggers more requirements
3. **Ask questions** - Interactions count toward progress
4. **Explain your thinking** - Verification is easier when you understand

### For Administrators
1. **Avoid force-advancing** - Use only for genuine edge cases
2. **Monitor completion rates** - Low rates may indicate too-strict requirements
3. **Adjust by difficulty** - Beginners may need looser requirements
4. **Review flagged sessions** - Cheating detection may need human review

---

## Troubleshooting

### "Cannot advance to next stage"

Check which requirements are unmet:
```python
can_advance, unmet = learning_engine.can_advance_stage(session)
for requirement in unmet:
    print(f"- {requirement}")
```

### Session Stuck

Verify the session state:
```python
progress = learning_engine.get_session_progress(session)
print(json.dumps(progress, indent=2))
```

### Force Reset (Admin)

```python
# Reset stage progress (admin only)
session.stage_progress[stage.value] = StageProgress(status=StageStatus.IN_PROGRESS)
learning_engine.save_session(session)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01 | Initial release with 8 stages |
| 1.1.0 | TBD | Adaptive requirements based on learner level |
| 1.2.0 | TBD | Multi-language support |
