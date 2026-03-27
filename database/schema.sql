-- ============================================================================
-- VidyaGuru AI Learning Platform - PostgreSQL Database Schema
-- ============================================================================
-- "विद्या ददाति विनयम्" - Knowledge gives humility
-- 
-- This schema implements a comprehensive database for personalized learning
-- with user tracking, progress monitoring, and AI-driven features.
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- For UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";       -- For encryption functions
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- For text similarity search

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

-- User account status
CREATE TYPE account_status AS ENUM (
    'active',
    'inactive',
    'suspended',
    'deleted',
    'pending_verification'
);

-- Learning style preferences
CREATE TYPE learning_style AS ENUM (
    'visual',
    'auditory',
    'reading_writing',
    'kinesthetic',
    'mixed'
);

-- Experience levels
CREATE TYPE experience_level AS ENUM (
    'beginner',
    'elementary',
    'intermediate',
    'advanced',
    'expert'
);

-- Task status
CREATE TYPE task_status AS ENUM (
    'pending',
    'in_progress',
    'submitted',
    'completed',
    'failed',
    'skipped'
);

-- Task types
CREATE TYPE task_type AS ENUM (
    'coding',
    'quiz',
    'project',
    'reading',
    'video',
    'practice',
    'daily',
    'challenge'
);

-- Task difficulty
CREATE TYPE task_difficulty AS ENUM (
    'beginner',
    'easy',
    'medium',
    'hard',
    'expert'
);

-- Communication task types
CREATE TYPE communication_type AS ENUM (
    'presentation',
    'explanation',
    'debate',
    'interview',
    'teaching',
    'storytelling',
    'pitch'
);

-- Solution verification status
CREATE TYPE verification_status AS ENUM (
    'pending',
    'verified',
    'rejected',
    'needs_review',
    'plagiarism_detected'
);

-- Journal entry types
CREATE TYPE journal_entry_type AS ENUM (
    'idea',
    'note',
    'reflection',
    'question',
    'breakthrough',
    'mistake_learned',
    'connection'
);

-- Reminder types
CREATE TYPE reminder_type AS ENUM (
    'study',
    'review',
    'deadline',
    'streak',
    'custom',
    'spaced_repetition'
);

-- Reminder repeat patterns
CREATE TYPE repeat_pattern AS ENUM (
    'none',
    'daily',
    'weekly',
    'monthly',
    'custom'
);

-- Industry sectors
CREATE TYPE industry_sector AS ENUM (
    'technology',
    'finance',
    'healthcare',
    'education',
    'ecommerce',
    'manufacturing',
    'energy',
    'transportation',
    'media',
    'agriculture',
    'government',
    'other'
);

-- Problem complexity
CREATE TYPE problem_complexity AS ENUM (
    'simple',
    'moderate',
    'complex',
    'enterprise'
);

-- ============================================================================
-- TABLE 1: USERS
-- Core user information and authentication
-- ============================================================================

CREATE TABLE users (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Authentication
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    
    -- Profile Information
    display_name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    bio TEXT,
    
    -- Learning Preferences
    learning_style learning_style DEFAULT 'mixed',
    experience_level experience_level DEFAULT 'beginner',
    weekly_time_commitment INTEGER DEFAULT 5,  -- hours per week
    primary_goal TEXT,
    interests TEXT[],  -- Array of interest topics
    preferred_language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Account Status
    account_status account_status DEFAULT 'pending_verification',
    email_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    
    -- OAuth (optional)
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    
    -- Gamification
    total_xp INTEGER DEFAULT 0,
    current_level INTEGER DEFAULT 1,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    
    -- Notification Preferences (JSONB for flexibility)
    notification_preferences JSONB DEFAULT '{
        "email_notifications": true,
        "push_notifications": true,
        "reminder_notifications": true,
        "weekly_digest": true
    }'::jsonb,
    
    -- Onboarding
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_step INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    last_active TIMESTAMP WITH TIME ZONE,
    
    -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_account_status ON users(account_status);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_last_active ON users(last_active);
CREATE INDEX idx_users_experience_level ON users(experience_level);
CREATE INDEX idx_users_interests ON users USING GIN(interests);

-- ============================================================================
-- TABLE 2: LEARNING_PROGRESS
-- Track user's learning journey and daily progress
-- ============================================================================

CREATE TABLE learning_progress (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Foreign Key
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Date tracking (one record per user per day)
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Daily Metrics
    xp_earned INTEGER DEFAULT 0,
    time_spent_minutes INTEGER DEFAULT 0,
    modules_completed INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    challenges_attempted INTEGER DEFAULT 0,
    challenges_passed INTEGER DEFAULT 0,
    
    -- Learning Activity
    concepts_learned TEXT[],  -- Array of concept IDs/names learned today
    skills_practiced TEXT[],  -- Array of skills practiced
    
    -- Communication Practice
    communication_sessions INTEGER DEFAULT 0,
    communication_minutes INTEGER DEFAULT 0,
    
    -- Journal Activity
    journal_entries_created INTEGER DEFAULT 0,
    
    -- AI Mentor Interactions
    mentor_messages_sent INTEGER DEFAULT 0,
    mentor_questions_asked INTEGER DEFAULT 0,
    
    -- Streak Information
    streak_maintained BOOLEAN DEFAULT FALSE,
    current_streak INTEGER DEFAULT 0,
    
    -- Performance Metrics
    average_score DECIMAL(5,2),
    accuracy_rate DECIMAL(5,2),
    
    -- Focus Areas (topics studied)
    focus_areas JSONB DEFAULT '[]'::jsonb,
    
    -- Session Data
    session_count INTEGER DEFAULT 1,
    longest_session_minutes INTEGER DEFAULT 0,
    
    -- Mood/Self-Assessment (optional)
    self_reported_mood VARCHAR(20),
    self_reported_difficulty VARCHAR(20),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint: one record per user per day
    CONSTRAINT unique_user_daily_progress UNIQUE(user_id, date)
);

-- Indexes for learning_progress table
CREATE INDEX idx_learning_progress_user_id ON learning_progress(user_id);
CREATE INDEX idx_learning_progress_date ON learning_progress(date);
CREATE INDEX idx_learning_progress_user_date ON learning_progress(user_id, date);
CREATE INDEX idx_learning_progress_xp ON learning_progress(xp_earned);
CREATE INDEX idx_learning_progress_streak ON learning_progress(current_streak);

-- ============================================================================
-- TABLE 3: TASKS
-- Learning tasks, exercises, and assignments
-- ============================================================================

CREATE TABLE tasks (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Foreign Key
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Task Identity
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    
    -- Task Classification
    task_type task_type NOT NULL DEFAULT 'practice',
    difficulty task_difficulty DEFAULT 'medium',
    category VARCHAR(100),
    tags TEXT[],
    
    -- Related Learning Path (optional)
    learning_path_id UUID,
    module_id UUID,
    
    -- Task Content
    content JSONB,  -- Flexible content storage (questions, code templates, etc.)
    template_code TEXT,  -- For coding tasks
    test_cases JSONB,  -- For automated testing
    hints TEXT[],  -- Progressive hints
    hints_used INTEGER DEFAULT 0,
    
    -- Requirements
    estimated_minutes INTEGER DEFAULT 30,
    max_attempts INTEGER DEFAULT 3,
    passing_score DECIMAL(5,2) DEFAULT 60.00,
    
    -- Rewards
    xp_reward INTEGER DEFAULT 10,
    bonus_xp INTEGER DEFAULT 0,
    
    -- Progress
    status task_status DEFAULT 'pending',
    current_attempts INTEGER DEFAULT 0,
    best_score DECIMAL(5,2),
    
    -- Timing
    deadline TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    time_spent_seconds INTEGER DEFAULT 0,
    
    -- AI Generated
    is_ai_generated BOOLEAN DEFAULT FALSE,
    generation_context JSONB,  -- Context used to generate task
    
    -- Daily Task Specific
    is_daily_task BOOLEAN DEFAULT FALSE,
    daily_date DATE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for tasks table
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_type ON tasks(task_type);
CREATE INDEX idx_tasks_difficulty ON tasks(difficulty);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_daily ON tasks(user_id, is_daily_task, daily_date);
CREATE INDEX idx_tasks_category ON tasks(category);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);

-- ============================================================================
-- TABLE 4: COMMUNICATION_TASKS
-- Tasks focused on improving communication skills
-- ============================================================================

CREATE TABLE communication_tasks (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Foreign Key
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Task Identity
    title VARCHAR(255) NOT NULL,
    description TEXT,
    scenario TEXT,  -- The communication scenario/context
    
    -- Communication Type
    communication_type communication_type NOT NULL,
    
    -- Target Skill
    target_skills TEXT[],  -- e.g., ['clarity', 'persuasion', 'empathy']
    difficulty task_difficulty DEFAULT 'medium',
    
    -- Task Content
    prompt TEXT NOT NULL,  -- Main prompt/question
    context_background TEXT,  -- Background information
    audience_description TEXT,  -- Who they're communicating to
    
    -- Sample/Reference
    sample_response TEXT,  -- Example good response
    evaluation_criteria JSONB,  -- Criteria for evaluation
    
    -- Requirements
    min_words INTEGER,
    max_words INTEGER,
    time_limit_minutes INTEGER,
    requires_audio BOOLEAN DEFAULT FALSE,
    requires_video BOOLEAN DEFAULT FALSE,
    
    -- Progress
    status task_status DEFAULT 'pending',
    
    -- User Response
    user_response TEXT,
    audio_url VARCHAR(500),
    video_url VARCHAR(500),
    response_word_count INTEGER,
    
    -- AI Evaluation
    ai_feedback TEXT,
    ai_score DECIMAL(5,2),
    clarity_score DECIMAL(5,2),
    structure_score DECIMAL(5,2),
    persuasiveness_score DECIMAL(5,2),
    engagement_score DECIMAL(5,2),
    
    -- Strengths and improvements identified
    strengths TEXT[],
    improvements TEXT[],
    
    -- Rewards
    xp_reward INTEGER DEFAULT 15,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    time_spent_seconds INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for communication_tasks table
CREATE INDEX idx_comm_tasks_user_id ON communication_tasks(user_id);
CREATE INDEX idx_comm_tasks_type ON communication_tasks(communication_type);
CREATE INDEX idx_comm_tasks_status ON communication_tasks(status);
CREATE INDEX idx_comm_tasks_user_status ON communication_tasks(user_id, status);
CREATE INDEX idx_comm_tasks_difficulty ON communication_tasks(difficulty);
CREATE INDEX idx_comm_tasks_target_skills ON communication_tasks USING GIN(target_skills);

-- ============================================================================
-- TABLE 5: INDUSTRY_PROBLEMS
-- Real-world industry problems for practical learning
-- ============================================================================

CREATE TABLE industry_problems (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Problem Identity (can be shared across users)
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    description TEXT NOT NULL,
    
    -- Industry Context
    industry_sector industry_sector NOT NULL,
    company_context TEXT,  -- Fictional or anonymized company scenario
    real_world_relevance TEXT,  -- Why this matters in the real world
    
    -- Problem Details
    problem_statement TEXT NOT NULL,
    background_info TEXT,
    constraints TEXT[],  -- Business/technical constraints
    success_criteria TEXT[],  -- How success is measured
    
    -- Technical Requirements
    required_skills TEXT[],
    technologies TEXT[],
    difficulty task_difficulty DEFAULT 'medium',
    complexity problem_complexity DEFAULT 'moderate',
    
    -- Resources
    resources JSONB,  -- Links, documentation, datasets
    sample_data JSONB,  -- Sample data for the problem
    starter_code TEXT,
    
    -- Evaluation
    evaluation_rubric JSONB,
    automated_tests JSONB,
    
    -- Metadata
    estimated_hours INTEGER DEFAULT 4,
    xp_reward INTEGER DEFAULT 50,
    
    -- Statistics (aggregated)
    times_attempted INTEGER DEFAULT 0,
    times_completed INTEGER DEFAULT 0,
    average_completion_hours DECIMAL(5,2),
    average_score DECIMAL(5,2),
    
    -- Tags and Categories
    tags TEXT[],
    learning_objectives TEXT[],
    
    -- Visibility
    is_published BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    -- AI Generated
    is_ai_generated BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for industry_problems table
CREATE INDEX idx_industry_problems_sector ON industry_problems(industry_sector);
CREATE INDEX idx_industry_problems_difficulty ON industry_problems(difficulty);
CREATE INDEX idx_industry_problems_complexity ON industry_problems(complexity);
CREATE INDEX idx_industry_problems_published ON industry_problems(is_published);
CREATE INDEX idx_industry_problems_featured ON industry_problems(is_featured);
CREATE INDEX idx_industry_problems_skills ON industry_problems USING GIN(required_skills);
CREATE INDEX idx_industry_problems_tags ON industry_problems USING GIN(tags);
CREATE INDEX idx_industry_problems_slug ON industry_problems(slug);

-- ============================================================================
-- TABLE 6: USER_SOLUTIONS
-- User submissions for tasks and industry problems
-- ============================================================================

CREATE TABLE user_solutions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Foreign Keys
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    industry_problem_id UUID REFERENCES industry_problems(id) ON DELETE SET NULL,
    communication_task_id UUID REFERENCES communication_tasks(id) ON DELETE SET NULL,
    
    -- Solution Content
    solution_type VARCHAR(50) NOT NULL,  -- 'code', 'text', 'file', 'mixed'
    content TEXT,  -- Main solution content
    code_content TEXT,  -- Code specific content
    file_urls TEXT[],  -- Uploaded files
    
    -- Code-specific fields
    language VARCHAR(50),  -- Programming language
    
    -- Submission Metadata
    attempt_number INTEGER DEFAULT 1,
    is_final_submission BOOLEAN DEFAULT FALSE,
    
    -- Time Tracking
    time_spent_seconds INTEGER DEFAULT 0,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Anti-Cheat / Verification
    typing_pattern_data JSONB,  -- Typing speed, patterns
    copy_paste_count INTEGER DEFAULT 0,
    tab_switch_count INTEGER DEFAULT 0,
    verification_status verification_status DEFAULT 'pending',
    plagiarism_score DECIMAL(5,2),
    plagiarism_sources JSONB,
    
    -- Automated Evaluation
    tests_passed INTEGER,
    tests_total INTEGER,
    test_results JSONB,
    automated_score DECIMAL(5,2),
    
    -- AI Evaluation
    ai_feedback TEXT,
    ai_score DECIMAL(5,2),
    ai_review_details JSONB,
    
    -- Final Score
    final_score DECIMAL(5,2),
    max_score DECIMAL(5,2) DEFAULT 100.00,
    passed BOOLEAN,
    
    -- Feedback
    strengths TEXT[],
    improvements TEXT[],
    detailed_feedback JSONB,
    
    -- XP Awarded
    xp_earned INTEGER DEFAULT 0,
    bonus_xp INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    evaluated_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraint: must have at least one task reference
    CONSTRAINT solution_task_reference CHECK (
        task_id IS NOT NULL OR 
        industry_problem_id IS NOT NULL OR 
        communication_task_id IS NOT NULL
    )
);

-- Indexes for user_solutions table
CREATE INDEX idx_user_solutions_user_id ON user_solutions(user_id);
CREATE INDEX idx_user_solutions_task_id ON user_solutions(task_id);
CREATE INDEX idx_user_solutions_problem_id ON user_solutions(industry_problem_id);
CREATE INDEX idx_user_solutions_comm_task_id ON user_solutions(communication_task_id);
CREATE INDEX idx_user_solutions_verification ON user_solutions(verification_status);
CREATE INDEX idx_user_solutions_submitted ON user_solutions(submitted_at);
CREATE INDEX idx_user_solutions_user_task ON user_solutions(user_id, task_id);
CREATE INDEX idx_user_solutions_score ON user_solutions(final_score);
CREATE INDEX idx_user_solutions_passed ON user_solutions(passed);

-- ============================================================================
-- TABLE 7: IDEA_JOURNAL
-- Personal learning journal for ideas, notes, and reflections
-- ============================================================================

CREATE TABLE idea_journal (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Foreign Key
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Entry Content
    title VARCHAR(255),
    content TEXT NOT NULL,
    entry_type journal_entry_type DEFAULT 'note',
    
    -- Rich Content
    rich_content JSONB,  -- For storing formatted content, images, etc.
    attachments TEXT[],  -- URLs to attached files
    
    -- Mood/Context
    mood VARCHAR(50),  -- 'focused', 'confused', 'excited', etc.
    energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    
    -- Learning Context
    related_topic VARCHAR(255),
    related_module_id UUID,
    related_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    
    -- Connections
    linked_entry_ids UUID[],  -- Links to other journal entries
    tags TEXT[],
    
    -- AI Features
    ai_insights JSONB,  -- AI-generated insights about the entry
    ai_summary TEXT,
    ai_suggested_actions TEXT[],
    ai_related_concepts TEXT[],
    
    -- Spaced Repetition
    review_scheduled BOOLEAN DEFAULT FALSE,
    next_review_date DATE,
    review_count INTEGER DEFAULT 0,
    last_reviewed_at TIMESTAMP WITH TIME ZONE,
    memory_strength DECIMAL(3,2) DEFAULT 0.5,  -- 0-1 scale
    
    -- Visibility
    is_private BOOLEAN DEFAULT TRUE,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for idea_journal table
CREATE INDEX idx_journal_user_id ON idea_journal(user_id);
CREATE INDEX idx_journal_entry_type ON idea_journal(entry_type);
CREATE INDEX idx_journal_created_at ON idea_journal(created_at);
CREATE INDEX idx_journal_user_created ON idea_journal(user_id, created_at DESC);
CREATE INDEX idx_journal_tags ON idea_journal USING GIN(tags);
CREATE INDEX idx_journal_review ON idea_journal(user_id, next_review_date) WHERE review_scheduled = TRUE;
CREATE INDEX idx_journal_pinned ON idea_journal(user_id, is_pinned) WHERE is_pinned = TRUE;
CREATE INDEX idx_journal_content_search ON idea_journal USING GIN(to_tsvector('english', content));

-- ============================================================================
-- TABLE 8: REMINDERS
-- Study reminders and notifications
-- ============================================================================

CREATE TABLE reminders (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Foreign Key
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Reminder Content
    title VARCHAR(255) NOT NULL,
    description TEXT,
    reminder_type reminder_type NOT NULL DEFAULT 'study',
    
    -- Scheduling
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    repeat_pattern repeat_pattern DEFAULT 'none',
    repeat_config JSONB,  -- Custom repeat configuration
    repeat_until TIMESTAMP WITH TIME ZONE,
    
    -- Notification Channels
    channels TEXT[] DEFAULT ARRAY['in_app'],  -- 'in_app', 'email', 'push', 'sms'
    
    -- Related Items (optional)
    related_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    related_module_id UUID,
    related_journal_id UUID REFERENCES idea_journal(id) ON DELETE SET NULL,
    
    -- Spaced Repetition Data
    is_spaced_repetition BOOLEAN DEFAULT FALSE,
    concept_to_review TEXT,
    repetition_number INTEGER DEFAULT 1,
    ease_factor DECIMAL(3,2) DEFAULT 2.5,  -- SM-2 algorithm
    interval_days INTEGER DEFAULT 1,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_completed BOOLEAN DEFAULT FALSE,
    is_snoozed BOOLEAN DEFAULT FALSE,
    snoozed_until TIMESTAMP WITH TIME ZONE,
    
    -- Tracking
    send_count INTEGER DEFAULT 0,
    last_sent TIMESTAMP WITH TIME ZONE,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- AI Features
    is_ai_suggested BOOLEAN DEFAULT FALSE,
    ai_suggestion_reason TEXT,
    
    -- Metadata
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    color VARCHAR(20),
    icon VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for reminders table
CREATE INDEX idx_reminders_user_id ON reminders(user_id);
CREATE INDEX idx_reminders_scheduled ON reminders(scheduled_at);
CREATE INDEX idx_reminders_type ON reminders(reminder_type);
CREATE INDEX idx_reminders_active ON reminders(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_reminders_upcoming ON reminders(user_id, scheduled_at) 
    WHERE is_active = TRUE AND is_completed = FALSE;
CREATE INDEX idx_reminders_spaced_rep ON reminders(user_id, is_spaced_repetition) 
    WHERE is_spaced_repetition = TRUE;
CREATE INDEX idx_reminders_priority ON reminders(priority);

-- ============================================================================
-- ADDITIONAL SUPPORTING TABLES
-- ============================================================================

-- Tags table for centralized tag management
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(20) DEFAULT '#6366f1',
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_tags_usage ON tags(usage_count DESC);

-- Achievements table
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(100),
    category VARCHAR(50),
    xp_reward INTEGER DEFAULT 0,
    criteria JSONB NOT NULL,  -- Conditions to earn
    is_hidden BOOLEAN DEFAULT FALSE,
    rarity VARCHAR(20) DEFAULT 'common',  -- common, rare, epic, legendary
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User achievements junction
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    progress_snapshot JSONB,
    CONSTRAINT unique_user_achievement UNIQUE(user_id, achievement_id)
);

CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_earned ON user_achievements(earned_at);

-- Skill levels tracking
CREATE TABLE skill_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    category VARCHAR(100),
    current_level INTEGER DEFAULT 0 CHECK (current_level BETWEEN 0 AND 100),
    confidence_score DECIMAL(5,2) DEFAULT 50.00,
    assessments_count INTEGER DEFAULT 0,
    last_assessed TIMESTAMP WITH TIME ZONE,
    level_history JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_skill UNIQUE(user_id, skill_name)
);

CREATE INDEX idx_skill_levels_user ON skill_levels(user_id);
CREATE INDEX idx_skill_levels_skill ON skill_levels(skill_name);
CREATE INDEX idx_skill_levels_level ON skill_levels(current_level);

-- AI Mentor Conversations
CREATE TABLE mentor_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    context_type VARCHAR(50) DEFAULT 'general',
    related_module_id UUID,
    related_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    model_used VARCHAR(50),
    total_tokens_used INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    summary TEXT,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user ON mentor_conversations(user_id);
CREATE INDEX idx_conversations_recent ON mentor_conversations(user_id, last_message_at DESC);

-- Conversation Messages
CREATE TABLE mentor_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES mentor_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    metadata JSONB,
    attachments JSONB,
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation ON mentor_messages(conversation_id);
CREATE INDEX idx_messages_created ON mentor_messages(created_at);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_progress_updated_at BEFORE UPDATE ON learning_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_communication_tasks_updated_at BEFORE UPDATE ON communication_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_industry_problems_updated_at BEFORE UPDATE ON industry_problems
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_solutions_updated_at BEFORE UPDATE ON user_solutions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_idea_journal_updated_at BEFORE UPDATE ON idea_journal
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reminders_updated_at BEFORE UPDATE ON reminders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skill_levels_updated_at BEFORE UPDATE ON skill_levels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update user XP and level
CREATE OR REPLACE FUNCTION update_user_xp_on_solution()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.xp_earned > 0 AND (OLD.xp_earned IS NULL OR OLD.xp_earned = 0) THEN
        UPDATE users 
        SET 
            total_xp = total_xp + NEW.xp_earned + COALESCE(NEW.bonus_xp, 0),
            current_level = GREATEST(1, FLOOR(SQRT((total_xp + NEW.xp_earned) / 100)) + 1)
        WHERE id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_xp_on_solution
    AFTER INSERT OR UPDATE OF xp_earned ON user_solutions
    FOR EACH ROW EXECUTE FUNCTION update_user_xp_on_solution();

-- Function to update industry problem statistics
CREATE OR REPLACE FUNCTION update_problem_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.industry_problem_id IS NOT NULL THEN
        UPDATE industry_problems 
        SET 
            times_attempted = times_attempted + 1,
            times_completed = times_completed + CASE WHEN NEW.passed = TRUE THEN 1 ELSE 0 END
        WHERE id = NEW.industry_problem_id;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_problem_stats
    AFTER INSERT ON user_solutions
    FOR EACH ROW EXECUTE FUNCTION update_problem_stats();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- User dashboard summary view
CREATE VIEW user_dashboard_summary AS
SELECT 
    u.id AS user_id,
    u.display_name,
    u.total_xp,
    u.current_level,
    u.current_streak,
    u.longest_streak,
    COALESCE(lp.xp_earned, 0) AS today_xp,
    COALESCE(lp.time_spent_minutes, 0) AS today_time_minutes,
    COALESCE(lp.tasks_completed, 0) AS today_tasks,
    (SELECT COUNT(*) FROM tasks t WHERE t.user_id = u.id AND t.status = 'pending') AS pending_tasks,
    (SELECT COUNT(*) FROM reminders r WHERE r.user_id = u.id AND r.is_active = TRUE 
        AND r.is_completed = FALSE AND r.scheduled_at <= CURRENT_TIMESTAMP + INTERVAL '24 hours') AS upcoming_reminders,
    (SELECT COUNT(*) FROM idea_journal j WHERE j.user_id = u.id AND j.review_scheduled = TRUE 
        AND j.next_review_date <= CURRENT_DATE) AS pending_reviews
FROM users u
LEFT JOIN learning_progress lp ON u.id = lp.user_id AND lp.date = CURRENT_DATE;

-- Weekly progress view
CREATE VIEW weekly_progress_summary AS
SELECT 
    user_id,
    DATE_TRUNC('week', date) AS week_start,
    SUM(xp_earned) AS total_xp,
    SUM(time_spent_minutes) AS total_minutes,
    SUM(tasks_completed) AS tasks_completed,
    SUM(modules_completed) AS modules_completed,
    AVG(average_score) AS avg_score,
    COUNT(DISTINCT date) AS active_days
FROM learning_progress
WHERE date >= CURRENT_DATE - INTERVAL '4 weeks'
GROUP BY user_id, DATE_TRUNC('week', date)
ORDER BY week_start DESC;

-- Skill radar view
CREATE VIEW user_skill_radar AS
SELECT 
    user_id,
    skill_name,
    category,
    current_level,
    confidence_score,
    assessments_count,
    last_assessed,
    CASE 
        WHEN current_level >= 80 THEN 'expert'
        WHEN current_level >= 60 THEN 'advanced'
        WHEN current_level >= 40 THEN 'intermediate'
        WHEN current_level >= 20 THEN 'beginner'
        ELSE 'novice'
    END AS proficiency_label
FROM skill_levels
ORDER BY user_id, current_level DESC;

-- ============================================================================
-- EXAMPLE QUERIES
-- ============================================================================

-- QUERY 1: Get user's complete dashboard data
-- SELECT * FROM user_dashboard_summary WHERE user_id = 'uuid-here';

-- QUERY 2: Get user's learning progress for the last 30 days
/*
SELECT 
    date,
    xp_earned,
    time_spent_minutes,
    tasks_completed,
    current_streak,
    average_score
FROM learning_progress
WHERE user_id = 'uuid-here'
    AND date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC;
*/

-- QUERY 3: Get pending tasks with deadlines
/*
SELECT 
    id,
    title,
    task_type,
    difficulty,
    deadline,
    xp_reward,
    EXTRACT(DAY FROM deadline - CURRENT_TIMESTAMP) AS days_until_deadline
FROM tasks
WHERE user_id = 'uuid-here'
    AND status IN ('pending', 'in_progress')
    AND deadline IS NOT NULL
ORDER BY deadline ASC;
*/

-- QUERY 4: Get daily tasks for today
/*
SELECT *
FROM tasks
WHERE user_id = 'uuid-here'
    AND is_daily_task = TRUE
    AND daily_date = CURRENT_DATE;
*/

-- QUERY 5: Get communication task history with scores
/*
SELECT 
    ct.id,
    ct.title,
    ct.communication_type,
    ct.status,
    ct.ai_score,
    ct.clarity_score,
    ct.completed_at,
    ct.strengths,
    ct.improvements
FROM communication_tasks ct
WHERE ct.user_id = 'uuid-here'
ORDER BY ct.created_at DESC
LIMIT 20;
*/

-- QUERY 6: Get industry problems by sector and difficulty
/*
SELECT 
    id,
    title,
    industry_sector,
    difficulty,
    complexity,
    xp_reward,
    times_attempted,
    times_completed,
    CASE WHEN times_attempted > 0 
        THEN ROUND((times_completed::DECIMAL / times_attempted) * 100, 2)
        ELSE 0 
    END AS completion_rate
FROM industry_problems
WHERE is_published = TRUE
    AND industry_sector = 'technology'
    AND difficulty IN ('medium', 'hard')
ORDER BY xp_reward DESC;
*/

-- QUERY 7: Get user's solution history with feedback
/*
SELECT 
    us.id,
    us.solution_type,
    us.final_score,
    us.passed,
    us.xp_earned,
    us.submitted_at,
    us.strengths,
    us.improvements,
    COALESCE(t.title, ip.title) AS task_title
FROM user_solutions us
LEFT JOIN tasks t ON us.task_id = t.id
LEFT JOIN industry_problems ip ON us.industry_problem_id = ip.id
WHERE us.user_id = 'uuid-here'
ORDER BY us.submitted_at DESC
LIMIT 20;
*/

-- QUERY 8: Search journal entries
/*
SELECT 
    id,
    title,
    entry_type,
    content,
    tags,
    created_at,
    ts_rank(to_tsvector('english', content), plainto_tsquery('english', 'search term')) AS relevance
FROM idea_journal
WHERE user_id = 'uuid-here'
    AND to_tsvector('english', content) @@ plainto_tsquery('english', 'search term')
ORDER BY relevance DESC
LIMIT 20;
*/

-- QUERY 9: Get journal entries due for spaced repetition review
/*
SELECT 
    id,
    title,
    content,
    entry_type,
    next_review_date,
    review_count,
    memory_strength
FROM idea_journal
WHERE user_id = 'uuid-here'
    AND review_scheduled = TRUE
    AND next_review_date <= CURRENT_DATE
ORDER BY next_review_date ASC, memory_strength ASC;
*/

-- QUERY 10: Get upcoming reminders
/*
SELECT 
    r.id,
    r.title,
    r.description,
    r.reminder_type,
    r.scheduled_at,
    r.priority,
    r.is_ai_suggested,
    t.title AS related_task_title
FROM reminders r
LEFT JOIN tasks t ON r.related_task_id = t.id
WHERE r.user_id = 'uuid-here'
    AND r.is_active = TRUE
    AND r.is_completed = FALSE
    AND r.scheduled_at BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '7 days'
ORDER BY r.scheduled_at ASC;
*/

-- QUERY 11: Get user's skill progression
/*
SELECT 
    skill_name,
    category,
    current_level,
    confidence_score,
    assessments_count,
    last_assessed,
    level_history
FROM skill_levels
WHERE user_id = 'uuid-here'
ORDER BY current_level DESC;
*/

-- QUERY 12: Get leaderboard (top users by XP)
/*
SELECT 
    u.id,
    u.display_name,
    u.avatar_url,
    u.total_xp,
    u.current_level,
    u.current_streak,
    RANK() OVER (ORDER BY u.total_xp DESC) AS rank
FROM users u
WHERE u.account_status = 'active'
ORDER BY u.total_xp DESC
LIMIT 100;
*/

-- QUERY 13: Get user's weekly activity heatmap
/*
SELECT 
    date,
    EXTRACT(DOW FROM date) AS day_of_week,
    xp_earned,
    time_spent_minutes,
    tasks_completed
FROM learning_progress
WHERE user_id = 'uuid-here'
    AND date >= CURRENT_DATE - INTERVAL '12 weeks'
ORDER BY date;
*/

-- QUERY 14: Get mentor conversation history
/*
SELECT 
    mc.id,
    mc.title,
    mc.context_type,
    mc.message_count,
    mc.last_message_at,
    (
        SELECT content 
        FROM mentor_messages mm 
        WHERE mm.conversation_id = mc.id 
        ORDER BY created_at DESC 
        LIMIT 1
    ) AS last_message
FROM mentor_conversations mc
WHERE mc.user_id = 'uuid-here'
    AND mc.is_archived = FALSE
ORDER BY mc.last_message_at DESC
LIMIT 20;
*/

-- QUERY 15: Calculate streak recovery (days since last activity)
/*
SELECT 
    u.id,
    u.display_name,
    u.current_streak,
    u.longest_streak,
    u.last_active,
    EXTRACT(DAY FROM CURRENT_TIMESTAMP - u.last_active) AS days_inactive,
    CASE 
        WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - u.last_active) <= 1 THEN 'active'
        WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - u.last_active) <= 3 THEN 'at_risk'
        ELSE 'inactive'
    END AS activity_status
FROM users u
WHERE u.account_status = 'active';
*/

-- ============================================================================
-- SEED DATA FOR TESTING
-- ============================================================================

-- Insert sample achievements
INSERT INTO achievements (name, description, icon, category, xp_reward, criteria, rarity) VALUES
('First Steps', 'Complete your first task', '🎯', 'milestones', 10, '{"type": "tasks_completed", "value": 1}', 'common'),
('Week Warrior', 'Maintain a 7-day streak', '🔥', 'streaks', 50, '{"type": "streak", "value": 7}', 'common'),
('Month Master', 'Maintain a 30-day streak', '🏆', 'streaks', 200, '{"type": "streak", "value": 30}', 'rare'),
('Century Club', 'Reach 100 total XP', '💯', 'xp', 25, '{"type": "xp", "value": 100}', 'common'),
('Knowledge Seeker', 'Complete 10 modules', '📚', 'learning', 100, '{"type": "modules", "value": 10}', 'common'),
('Problem Solver', 'Complete 5 industry problems', '🏭', 'industry', 150, '{"type": "industry_problems", "value": 5}', 'rare'),
('Communicator', 'Complete 10 communication tasks', '🎤', 'communication', 100, '{"type": "communication_tasks", "value": 10}', 'common'),
('Journaler', 'Write 20 journal entries', '📝', 'journal', 75, '{"type": "journal_entries", "value": 20}', 'common'),
('Night Owl', 'Study after midnight', '🦉', 'special', 15, '{"type": "time_based", "hour_range": [0, 4]}', 'rare'),
('Early Bird', 'Study before 6 AM', '🐦', 'special', 15, '{"type": "time_based", "hour_range": [4, 6]}', 'rare'),
('Perfectionist', 'Score 100% on any task', '⭐', 'performance', 50, '{"type": "perfect_score", "value": 100}', 'epic'),
('Guru', 'Reach level 50', '🧘', 'levels', 500, '{"type": "level", "value": 50}', 'legendary');

-- Insert sample tags
INSERT INTO tags (name, color) VALUES
('python', '#3776AB'),
('javascript', '#F7DF1E'),
('machine-learning', '#FF6F00'),
('web-development', '#61DAFB'),
('algorithms', '#00C853'),
('data-structures', '#7C4DFF'),
('database', '#336791'),
('api-design', '#FF5722'),
('system-design', '#795548'),
('communication', '#E91E63'),
('presentation', '#9C27B0'),
('problem-solving', '#2196F3');

-- Insert sample industry problems
INSERT INTO industry_problems (
    title, slug, description, industry_sector, problem_statement, 
    required_skills, difficulty, complexity, estimated_hours, xp_reward, is_published
) VALUES
(
    'E-commerce Recommendation Engine',
    'ecommerce-recommendation-engine',
    'Build a product recommendation system for an online retail platform',
    'ecommerce',
    'Design and implement a recommendation engine that suggests products based on user browsing history, purchase patterns, and similar user behavior.',
    ARRAY['python', 'machine-learning', 'data-analysis', 'api-design'],
    'hard',
    'complex',
    8,
    100,
    TRUE
),
(
    'Healthcare Appointment Scheduler',
    'healthcare-appointment-scheduler',
    'Create an intelligent appointment scheduling system for a multi-location clinic',
    'healthcare',
    'Build a scheduling system that optimizes doctor availability, patient preferences, and clinic resources while handling cancellations and emergencies.',
    ARRAY['python', 'algorithms', 'database', 'api-design'],
    'medium',
    'moderate',
    6,
    75,
    TRUE
),
(
    'Fintech Transaction Fraud Detection',
    'fintech-fraud-detection',
    'Develop a real-time fraud detection system for financial transactions',
    'finance',
    'Create a system that analyzes transaction patterns in real-time to detect and flag potentially fraudulent activities while minimizing false positives.',
    ARRAY['python', 'machine-learning', 'data-analysis', 'real-time-processing'],
    'expert',
    'enterprise',
    12,
    150,
    TRUE
);

-- ============================================================================
-- GRANTS AND PERMISSIONS (adjust for your setup)
-- ============================================================================

-- Create application role (uncomment and modify as needed)
-- CREATE ROLE vidyaguru_app WITH LOGIN PASSWORD 'secure_password';
-- GRANT CONNECT ON DATABASE vidyaguru TO vidyaguru_app;
-- GRANT USAGE ON SCHEMA public TO vidyaguru_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO vidyaguru_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO vidyaguru_app;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
