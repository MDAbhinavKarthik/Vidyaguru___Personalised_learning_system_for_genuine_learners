"""Initial migration - All models

Revision ID: 001_initial
Revises: 
Create Date: 2026-03-08

This migration creates all tables for the VidyaGuru platform:
- Users and authentication
- Learning paths and stages
- Tasks and submissions
- Idea journal
- Industry challenges
- Anti-cheat system
- Resume highlights
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # USERS TABLE
    # ==========================================================================
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('role', sa.String(50), default='learner'),
        sa.Column('xp_points', sa.Integer(), default=0),
        sa.Column('level', sa.Integer(), default=1),
        sa.Column('streak_days', sa.Integer(), default=0),
        sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('preferences', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # ==========================================================================
    # LEARNING PATHS TABLE
    # ==========================================================================
    op.create_table(
        'learning_paths',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('difficulty_level', sa.String(50), nullable=True),
        sa.Column('estimated_duration_hours', sa.Float(), nullable=True),
        sa.Column('current_stage', sa.Integer(), default=1),
        sa.Column('total_stages', sa.Integer(), default=8),
        sa.Column('progress_percentage', sa.Float(), default=0.0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_completed', sa.Boolean(), default=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_learning_paths_user_id', 'learning_paths', ['user_id'])
    
    # ==========================================================================
    # LEARNING STAGES TABLE
    # ==========================================================================
    op.create_table(
        'learning_stages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('path_id', sa.Integer(), nullable=False),
        sa.Column('stage_number', sa.Integer(), nullable=False),
        sa.Column('stage_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('objectives', postgresql.JSON(), nullable=True),
        sa.Column('resources', postgresql.JSON(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), default=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('xp_reward', sa.Integer(), default=100),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['path_id'], ['learning_paths.id'], ondelete='CASCADE')
    )
    op.create_index('ix_learning_stages_path_id', 'learning_stages', ['path_id'])
    
    # ==========================================================================
    # TASKS TABLE
    # ==========================================================================
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('path_id', sa.Integer(), nullable=True),
        sa.Column('stage_id', sa.Integer(), nullable=True),
        sa.Column('task_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('difficulty', sa.String(50), default='medium'),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('xp_reward', sa.Integer(), default=50),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['path_id'], ['learning_paths.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['stage_id'], ['learning_stages.id'], ondelete='SET NULL')
    )
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    
    # ==========================================================================
    # TASK SUBMISSIONS TABLE
    # ==========================================================================
    op.create_table(
        'task_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('submission_text', sa.Text(), nullable=True),
        sa.Column('submission_code', sa.Text(), nullable=True),
        sa.Column('attachments', postgresql.JSON(), nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('skill_scores', postgresql.JSON(), nullable=True),
        sa.Column('is_passed', sa.Boolean(), nullable=True),
        sa.Column('xp_earned', sa.Integer(), default=0),
        sa.Column('attempt_number', sa.Integer(), default=1),
        sa.Column('time_spent_minutes', sa.Integer(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('evaluated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_task_submissions_task_id', 'task_submissions', ['task_id'])
    
    # ==========================================================================
    # IDEAS (JOURNAL) TABLE
    # ==========================================================================
    op.create_table(
        'ideas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('related_topic', sa.String(255), nullable=True),
        sa.Column('path_id', sa.Integer(), nullable=True),
        sa.Column('is_starred', sa.Boolean(), default=False),
        sa.Column('ai_insights', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['path_id'], ['learning_paths.id'], ondelete='SET NULL')
    )
    op.create_index('ix_ideas_user_id', 'ideas', ['user_id'])
    
    # ==========================================================================
    # INDUSTRY CHALLENGES TABLE
    # ==========================================================================
    op.create_table(
        'industry_challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('difficulty', sa.String(50), nullable=False),
        sa.Column('problem_statement', sa.Text(), nullable=False),
        sa.Column('context', sa.Text(), nullable=False),
        sa.Column('constraints', postgresql.JSON(), nullable=False),
        sa.Column('requirements', postgresql.JSON(), nullable=False),
        sa.Column('evaluation_criteria', postgresql.JSON(), nullable=False),
        sa.Column('expected_concepts', postgresql.JSON(), nullable=False),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('company_type', sa.String(100), nullable=True),
        sa.Column('tech_stack_hints', postgresql.JSON(), nullable=True),
        sa.Column('estimated_time_hours', sa.Float(), default=2.0),
        sa.Column('xp_reward', sa.Integer(), default=500),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('times_attempted', sa.Integer(), default=0),
        sa.Column('success_rate', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_industry_challenges_category', 'industry_challenges', ['category'])
    op.create_index('ix_industry_challenges_difficulty', 'industry_challenges', ['difficulty'])
    
    # ==========================================================================
    # CHALLENGE SOLUTIONS TABLE
    # ==========================================================================
    op.create_table(
        'challenge_solutions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('solution_text', sa.Text(), nullable=False),
        sa.Column('architecture_diagram', sa.Text(), nullable=True),
        sa.Column('trade_offs_discussed', postgresql.JSON(), nullable=True),
        sa.Column('technologies_proposed', postgresql.JSON(), nullable=True),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('strengths', postgresql.JSON(), nullable=True),
        sa.Column('areas_for_improvement', postgresql.JSON(), nullable=True),
        sa.Column('innovation_score', sa.Float(), nullable=True),
        sa.Column('practicality_score', sa.Float(), nullable=True),
        sa.Column('completeness_score', sa.Float(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('is_resume_worthy', sa.Boolean(), default=False),
        sa.Column('resume_bullet_points', postgresql.JSON(), nullable=True),
        sa.Column('resume_recommendation_reason', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('evaluated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('xp_earned', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['challenge_id'], ['industry_challenges.id'], ondelete='CASCADE')
    )
    op.create_index('ix_challenge_solutions_user_id', 'challenge_solutions', ['user_id'])
    op.create_index('ix_challenge_solutions_challenge_id', 'challenge_solutions', ['challenge_id'])
    
    # ==========================================================================
    # RESUME HIGHLIGHTS TABLE
    # ==========================================================================
    op.create_table(
        'resume_highlights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('solution_id', sa.Integer(), nullable=False),
        sa.Column('headline', sa.String(255), nullable=False),
        sa.Column('bullet_points', postgresql.JSON(), nullable=False),
        sa.Column('skills_demonstrated', postgresql.JSON(), nullable=False),
        sa.Column('impact_statement', sa.Text(), nullable=True),
        sa.Column('added_to_resume', sa.Boolean(), default=False),
        sa.Column('exported_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['solution_id'], ['challenge_solutions.id'], ondelete='CASCADE')
    )
    op.create_index('ix_resume_highlights_user_id', 'resume_highlights', ['user_id'])
    
    # ==========================================================================
    # ANTI-CHEAT EVENTS TABLE
    # ==========================================================================
    op.create_table(
        'anti_cheat_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), default='low'),
        sa.Column('details', postgresql.JSON(), nullable=True),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('submission_id', sa.Integer(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), default=False),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['submission_id'], ['task_submissions.id'], ondelete='SET NULL')
    )
    op.create_index('ix_anti_cheat_events_user_id', 'anti_cheat_events', ['user_id'])
    op.create_index('ix_anti_cheat_events_event_type', 'anti_cheat_events', ['event_type'])
    
    # ==========================================================================
    # USER TRUST SCORES TABLE
    # ==========================================================================
    op.create_table(
        'user_trust_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('trust_score', sa.Float(), default=100.0),
        sa.Column('consistency_score', sa.Float(), default=100.0),
        sa.Column('total_submissions', sa.Integer(), default=0),
        sa.Column('flagged_submissions', sa.Integer(), default=0),
        sa.Column('verified_skills', postgresql.JSON(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    
    # ==========================================================================
    # REFRESH TOKENS TABLE
    # ==========================================================================
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'])
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('refresh_tokens')
    op.drop_table('user_trust_scores')
    op.drop_table('anti_cheat_events')
    op.drop_table('resume_highlights')
    op.drop_table('challenge_solutions')
    op.drop_table('industry_challenges')
    op.drop_table('ideas')
    op.drop_table('task_submissions')
    op.drop_table('tasks')
    op.drop_table('learning_stages')
    op.drop_table('learning_paths')
    op.drop_table('users')
