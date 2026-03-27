-- ============================================================================
-- VidyaGuru Database Initialization Script
-- Run this to set up the database in Docker
-- ============================================================================

-- Create database if not exists (run as superuser)
-- Note: This is typically handled by Docker environment variables

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant permissions to application user
GRANT ALL PRIVILEGES ON DATABASE vidyaguru TO vidyaguru;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vidyaguru;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vidyaguru;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'VidyaGuru database initialized successfully at %', NOW();
END $$;
