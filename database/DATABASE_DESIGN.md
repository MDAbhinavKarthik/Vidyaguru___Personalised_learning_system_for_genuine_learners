# VidyaGuru Database Design Documentation

## Overview

This document describes the PostgreSQL database schema for the VidyaGuru AI Learning Platform. The database is designed to support personalized learning with comprehensive tracking, gamification, and AI-driven features.

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           VIDYAGURU DATABASE SCHEMA                          │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────┐
                                    │  USERS   │
                                    │──────────│
                                    │ id (PK)  │
                                    │ email    │
                                    │ ...      │
                                    └────┬─────┘
                                         │
          ┌──────────────────────────────┼──────────────────────────────┐
          │                              │                              │
          │              ┌───────────────┼───────────────┐              │
          │              │               │               │              │
          ▼              ▼               ▼               ▼              ▼
┌─────────────────┐ ┌─────────┐ ┌─────────────────┐ ┌──────────┐ ┌─────────────┐
│LEARNING_PROGRESS│ │  TASKS  │ │COMMUNICATION    │ │  IDEA    │ │  REMINDERS  │
│─────────────────│ │─────────│ │TASKS            │ │ JOURNAL  │ │─────────────│
│ id (PK)         │ │ id (PK) │ │─────────────────│ │──────────│ │ id (PK)     │
│ user_id (FK)    │ │user_id  │ │ id (PK)         │ │ id (PK)  │ │ user_id(FK) │
│ date            │ │(FK)     │ │ user_id (FK)    │ │user_id   │ │ ...         │
│ xp_earned       │ │ ...     │ │ ...             │ │(FK)      │ └─────────────┘
│ ...             │ └────┬────┘ └────────┬────────┘ │ ...      │
└─────────────────┘      │               │          └────┬─────┘
                         │               │               │
                         │               │               │
                         └───────────────┼───────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   USER_SOLUTIONS    │
                              │─────────────────────│
                              │ id (PK)             │
                              │ user_id (FK)        │
                              │ task_id (FK)        │◄──────────┐
                              │ industry_problem_id │           │
                              │ communication_task  │           │
                              │ _id (FK)            │           │
                              │ ...                 │           │
                              └─────────────────────┘           │
                                                                │
                              ┌─────────────────────┐           │
                              │ INDUSTRY_PROBLEMS   │───────────┘
                              │─────────────────────│
                              │ id (PK)             │
                              │ title               │
                              │ industry_sector     │
                              │ ...                 │
                              └─────────────────────┘

SUPPORTING TABLES:
┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐
│   TAGS   │  │ ACHIEVEMENTS │  │ SKILL_LEVELS │  │ MENTOR_CONVERSATIONS│
└──────────┘  └──────────────┘  └──────────────┘  └────────────────────┘
                    │                  │                    │
                    ▼                  │                    ▼
          ┌──────────────────┐         │          ┌──────────────────┐
          │ USER_ACHIEVEMENTS│         │          │ MENTOR_MESSAGES  │
          └──────────────────┘         │          └──────────────────┘
                                       │
                                       ▼
                              (tracks per-skill progress)
```

## Table Descriptions

### 1. USERS
**Purpose**: Core user information, authentication, and preferences.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| email | VARCHAR(255) | Unique email for authentication |
| password_hash | VARCHAR(255) | Bcrypt/Argon2 hashed password |
| display_name | VARCHAR(100) | Public display name |
| learning_style | ENUM | visual, auditory, reading_writing, kinesthetic, mixed |
| experience_level | ENUM | beginner to expert |
| total_xp | INTEGER | Accumulated experience points |
| current_level | INTEGER | Calculated from XP |
| current_streak | INTEGER | Current consecutive days active |
| notification_preferences | JSONB | Flexible notification settings |

**Indexes**: email, account_status, created_at, interests (GIN)

---

### 2. LEARNING_PROGRESS
**Purpose**: Daily learning activity tracking (one record per user per day).

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| date | DATE | Activity date (unique per user) |
| xp_earned | INTEGER | XP earned that day |
| time_spent_minutes | INTEGER | Total study time |
| tasks_completed | INTEGER | Count of completed tasks |
| current_streak | INTEGER | Streak count at that date |
| focus_areas | JSONB | Topics studied |

**Unique Constraint**: (user_id, date)
**Indexes**: user_id, date, user_date composite

---

### 3. TASKS
**Purpose**: Learning tasks, exercises, coding challenges, and daily assignments.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| title | VARCHAR(255) | Task title |
| task_type | ENUM | coding, quiz, project, daily, etc. |
| difficulty | ENUM | beginner to expert |
| status | ENUM | pending, in_progress, completed, etc. |
| xp_reward | INTEGER | XP awarded on completion |
| hints | TEXT[] | Progressive hints array |
| test_cases | JSONB | Automated test definitions |
| deadline | TIMESTAMP | Optional due date |

**Indexes**: user_id, status, task_type, deadline, tags (GIN)

---

### 4. COMMUNICATION_TASKS
**Purpose**: Tasks focused on improving verbal/written communication skills.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| communication_type | ENUM | presentation, explanation, debate, etc. |
| prompt | TEXT | Main task prompt |
| target_skills | TEXT[] | Skills being practiced |
| user_response | TEXT | User's written response |
| ai_feedback | TEXT | AI-generated feedback |
| clarity_score | DECIMAL | Score for clarity (0-100) |
| structure_score | DECIMAL | Score for structure |

**Indexes**: user_id, communication_type, status

---

### 5. INDUSTRY_PROBLEMS
**Purpose**: Real-world industry scenarios for practical learning (shared across users).

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| title | VARCHAR(255) | Problem title |
| slug | VARCHAR(255) | URL-friendly identifier |
| industry_sector | ENUM | technology, healthcare, finance, etc. |
| problem_statement | TEXT | Detailed problem description |
| required_skills | TEXT[] | Skills needed |
| difficulty | ENUM | Task difficulty level |
| complexity | ENUM | simple to enterprise |
| times_attempted | INTEGER | Global attempt count |
| times_completed | INTEGER | Global completion count |

**Indexes**: industry_sector, difficulty, required_skills (GIN), is_published

---

### 6. USER_SOLUTIONS
**Purpose**: User submissions for tasks and industry problems with evaluation.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| task_id | UUID | FK to tasks (optional) |
| industry_problem_id | UUID | FK to industry_problems (optional) |
| communication_task_id | UUID | FK to communication_tasks (optional) |
| content | TEXT | Solution content |
| verification_status | ENUM | pending, verified, plagiarism_detected |
| typing_pattern_data | JSONB | Anti-cheat data |
| final_score | DECIMAL | Final evaluated score |
| xp_earned | INTEGER | XP awarded |

**Constraint**: Must have at least one task reference
**Indexes**: user_id, task_id, verification_status, submitted_at

---

### 7. IDEA_JOURNAL
**Purpose**: Personal learning journal for notes, ideas, and reflections.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| title | VARCHAR(255) | Entry title |
| content | TEXT | Entry content |
| entry_type | ENUM | idea, note, reflection, question, etc. |
| tags | TEXT[] | Classification tags |
| ai_insights | JSONB | AI-generated insights |
| review_scheduled | BOOLEAN | For spaced repetition |
| next_review_date | DATE | When to review |
| memory_strength | DECIMAL | Retention score (0-1) |

**Indexes**: user_id, entry_type, tags (GIN), content full-text search

---

### 8. REMINDERS
**Purpose**: Study reminders, notifications, and spaced repetition scheduling.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| title | VARCHAR(255) | Reminder title |
| reminder_type | ENUM | study, review, deadline, streak, etc. |
| scheduled_at | TIMESTAMP | When to send |
| repeat_pattern | ENUM | none, daily, weekly, monthly |
| channels | TEXT[] | in_app, email, push |
| is_spaced_repetition | BOOLEAN | For memory reinforcement |
| priority | INTEGER | 1-10 priority level |

**Indexes**: user_id, scheduled_at, upcoming reminders composite

---

## Relationships Summary

```
users (1) ──────────< (M) learning_progress    [One user has many daily records]
users (1) ──────────< (M) tasks                [One user has many tasks]
users (1) ──────────< (M) communication_tasks  [One user has many comm tasks]
users (1) ──────────< (M) user_solutions       [One user has many solutions]
users (1) ──────────< (M) idea_journal         [One user has many entries]
users (1) ──────────< (M) reminders            [One user has many reminders]
users (1) ──────────< (M) skill_levels         [One user has many skills]
users (1) ──────────< (M) user_achievements    [One user has many achievements]
users (1) ──────────< (M) mentor_conversations [One user has many conversations]

tasks (1) ──────────< (M) user_solutions       [One task has many submissions]
industry_problems (1)< (M) user_solutions      [One problem has many solutions]
communication_tasks(1)< (M) user_solutions     [One comm task has many solutions]

achievements (1) ───< (M) user_achievements    [One achievement, many earners]

mentor_conversations (1) < (M) mentor_messages [One conversation, many messages]
```

---

## Indexing Strategy

### Primary Indexes (Automatic)
- All primary keys (UUID) are automatically indexed

### Foreign Key Indexes
- All `user_id` columns are indexed for efficient joins

### Query-Optimized Indexes
| Table | Index | Purpose |
|-------|-------|---------|
| users | idx_users_email | Fast email lookup (auth) |
| users | idx_users_interests | GIN index for array search |
| learning_progress | idx_learning_progress_user_date | Daily lookups |
| tasks | idx_tasks_user_status | Filtered task lists |
| tasks | idx_tasks_tags | GIN for tag-based search |
| idea_journal | idx_journal_content_search | Full-text search |
| reminders | idx_reminders_upcoming | Upcoming reminder queries |

### Partial Indexes (Performance Optimization)
```sql
-- Only index active reminders
CREATE INDEX idx_reminders_active ON reminders(user_id, is_active) 
    WHERE is_active = TRUE;

-- Only index scheduled reviews
CREATE INDEX idx_journal_review ON idea_journal(user_id, next_review_date) 
    WHERE review_scheduled = TRUE;
```

---

## Example Queries

### 1. Get User Dashboard Summary
```sql
SELECT * FROM user_dashboard_summary WHERE user_id = $1;
```

### 2. Get Weekly Progress
```sql
SELECT 
    DATE_TRUNC('week', date) AS week,
    SUM(xp_earned) AS total_xp,
    SUM(time_spent_minutes) AS total_minutes,
    COUNT(DISTINCT date) AS active_days
FROM learning_progress
WHERE user_id = $1 
    AND date >= CURRENT_DATE - INTERVAL '4 weeks'
GROUP BY DATE_TRUNC('week', date)
ORDER BY week DESC;
```

### 3. Get Pending Tasks with Deadlines
```sql
SELECT id, title, difficulty, deadline, xp_reward,
    EXTRACT(EPOCH FROM (deadline - NOW()))/3600 AS hours_remaining
FROM tasks
WHERE user_id = $1
    AND status IN ('pending', 'in_progress')
    AND deadline IS NOT NULL
ORDER BY deadline ASC;
```

### 4. Search Journal Entries
```sql
SELECT id, title, content, created_at,
    ts_rank(to_tsvector('english', content), query) AS rank
FROM idea_journal, plainto_tsquery('english', $2) query
WHERE user_id = $1
    AND to_tsvector('english', content) @@ query
ORDER BY rank DESC
LIMIT 20;
```

### 5. Get Due Spaced Repetition Reviews
```sql
SELECT id, title, content, memory_strength, review_count
FROM idea_journal
WHERE user_id = $1
    AND review_scheduled = TRUE
    AND next_review_date <= CURRENT_DATE
ORDER BY memory_strength ASC, next_review_date ASC;
```

### 6. Calculate User Streak
```sql
WITH consecutive_days AS (
    SELECT date,
        date - (ROW_NUMBER() OVER (ORDER BY date))::int AS grp
    FROM learning_progress
    WHERE user_id = $1 AND xp_earned > 0
)
SELECT COUNT(*) AS current_streak
FROM consecutive_days
WHERE grp = (
    SELECT grp FROM consecutive_days 
    WHERE date = CURRENT_DATE - 1 OR date = CURRENT_DATE
    LIMIT 1
);
```

### 7. Get Industry Problems by Skill Match
```sql
SELECT ip.*, 
    array_length(
        ARRAY(SELECT unnest(ip.required_skills) 
              INTERSECT 
              SELECT unnest($2::text[])), 1
    ) AS skill_match_count
FROM industry_problems ip
WHERE ip.is_published = TRUE
    AND ip.required_skills && $2::text[]  -- Array overlap
    AND ip.difficulty = $3
ORDER BY skill_match_count DESC, ip.times_completed DESC
LIMIT 10;
```

### 8. Leaderboard Query
```sql
SELECT 
    u.id, u.display_name, u.avatar_url,
    u.total_xp, u.current_level, u.current_streak,
    RANK() OVER (ORDER BY u.total_xp DESC) AS rank
FROM users u
WHERE u.account_status = 'active'
ORDER BY rank
LIMIT 100;
```

---

## Data Integrity

### Constraints
- **Foreign Keys**: CASCADE DELETE on user deletion
- **Unique**: email, user+date for progress, user+skill for levels
- **Check**: Scores between 0-100, priority 1-10

### Triggers
- `update_updated_at_column()`: Auto-update timestamps
- `update_user_xp_on_solution()`: Sync XP on solution submission
- `update_problem_stats()`: Track problem attempt/completion counts

---

## Performance Considerations

1. **Partitioning**: Consider partitioning `learning_progress` by month for large datasets
2. **Archiving**: Move old solutions to archive tables after 1 year
3. **Materialized Views**: Create for leaderboards, updated hourly
4. **Connection Pooling**: Use PgBouncer for high concurrency
5. **Read Replicas**: For analytics queries

---

## Migration Commands

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View migration history
alembic history
```
