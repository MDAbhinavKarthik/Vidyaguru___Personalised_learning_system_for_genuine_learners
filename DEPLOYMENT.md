# VidyaGuru AI Learning Platform - Deployment Guide

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Development)](#quick-start-development)
3. [Production Deployment](#production-deployment)
4. [Database Migrations](#database-migrations)
5. [Environment Configuration](#environment-configuration)
6. [Security Checklist](#security-checklist)
7. [Testing Workflow](#testing-workflow)
8. [Monitoring & Logs](#monitoring--logs)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Docker | 24.0+ | Containerization |
| Docker Compose | 2.20+ | Container orchestration |
| Node.js | 20.x | Frontend build (optional for local dev) |
| Python | 3.11+ | Backend (optional for local dev) |
| Git | 2.40+ | Version control |

### Required Accounts/Keys

- **Google Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## Quick Start (Development)

### 1. Clone and Configure

```powershell
# Clone repository
git clone https://github.com/your-repo/vidyaguru.git
cd vidyaguru

# Copy environment file
Copy-Item .env.example .env

# Edit .env with your values (especially GEMINI_API_KEY)
notepad .env
```

### 2. Generate Secrets

```powershell
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Or using OpenSSL
openssl rand -hex 32
```

### 3. Start Development Environment

```powershell
# Start all services
docker-compose up -d

# Start with dev tools (pgAdmin, Redis Commander)
docker-compose --profile dev up -d

# View logs
docker-compose logs -f
```

### 4. Run Database Migrations

```powershell
# Run migrations
docker-compose --profile migrate up migrations

# Or manually
docker-compose exec backend alembic upgrade head
```

### 5. Access Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js application |
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| PgAdmin | http://localhost:5050 | Database admin (dev profile) |
| Redis Commander | http://localhost:8081 | Redis admin (dev profile) |

---

## Production Deployment

### 1. Server Requirements

- **Minimum**: 2 vCPU, 4GB RAM, 50GB SSD
- **Recommended**: 4 vCPU, 8GB RAM, 100GB SSD
- **OS**: Ubuntu 22.04 LTS or similar

### 2. Production Environment Setup

```bash
# Copy production env template
cp .env.production.example .env

# Generate strong passwords
DB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -hex 32)

# Update .env with generated values
sed -i "s/<GENERATE_STRONG_PASSWORD>/$DB_PASSWORD/g" .env
sed -i "s/<GENERATE_WITH_openssl_rand_hex_32>/$SECRET_KEY/g" .env
```

### 3. SSL Certificate Setup

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Option A: Self-signed (testing only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/CN=yourdomain.com"

# Option B: Let's Encrypt (production)
# Install certbot and generate certificates
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
```

### 4. Deploy with Production Profile

```bash
# Build and start all services including nginx
docker-compose --profile production up -d --build

# Run migrations
docker-compose --profile migrate up migrations

# Verify deployment
curl -f http://localhost/health
```

### 5. Update NGINX Configuration

Edit `nginx/nginx.conf`:
- Replace `yourdomain.com` with your actual domain
- Update SSL certificate paths if needed
- Adjust rate limiting based on your needs

---

## Database Migrations

### Creating New Migrations

```powershell
# Generate migration from model changes
docker-compose exec backend alembic revision --autogenerate -m "description"

# Create empty migration
docker-compose exec backend alembic revision -m "description"
```

### Running Migrations

```powershell
# Upgrade to latest
docker-compose exec backend alembic upgrade head

# Upgrade to specific revision
docker-compose exec backend alembic upgrade <revision_id>

# Downgrade one revision
docker-compose exec backend alembic downgrade -1

# Downgrade to specific revision
docker-compose exec backend alembic downgrade <revision_id>

# View migration history
docker-compose exec backend alembic history
```

### Migration Best Practices

1. **Always backup before migrating production**
   ```bash
   docker-compose exec postgres pg_dump -U vidyaguru vidyaguru > backup_$(date +%Y%m%d).sql
   ```

2. **Test migrations on staging first**

3. **Review auto-generated migrations** - They may need manual adjustments

---

## Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (32+ chars) | `openssl rand -hex 32` |
| `DB_PASSWORD` | PostgreSQL password | Strong random password |
| `GEMINI_API_KEY` | Google AI API key | From Google AI Studio |
| `CORS_ORIGINS` | Allowed origins | `["https://yourdomain.com"]` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | development | development/staging/production |
| `LOG_LEVEL` | INFO | DEBUG/INFO/WARNING/ERROR |
| `REDIS_PASSWORD` | vidyaguru_redis | Redis auth password |
| `RATE_LIMIT_PER_MINUTE` | 60 | API rate limit |

---

## Security Checklist

### Before Production Deployment

- [ ] **Generate unique SECRET_KEY** - Never reuse development keys
- [ ] **Set strong DB_PASSWORD** - Use `openssl rand -base64 32`
- [ ] **Set strong REDIS_PASSWORD** - Use `openssl rand -base64 32`
- [ ] **Configure CORS_ORIGINS** - List only your domains
- [ ] **Enable HTTPS** - Set up SSL certificates
- [ ] **Set ENVIRONMENT=production** - Disables debug features
- [ ] **Review rate limits** - Adjust based on expected traffic
- [ ] **Enable firewall** - Only expose ports 80, 443
- [ ] **Set up monitoring** - Log aggregation and alerting

### API Security Features

The platform includes:

1. **Rate Limiting**
   - 60 requests/minute general
   - 5 requests/minute for login
   - 3 requests/minute for registration

2. **Security Headers**
   - X-Content-Type-Options
   - X-Frame-Options
   - X-XSS-Protection
   - Referrer-Policy
   - Content-Security-Policy

3. **Input Validation**
   - Pydantic schema validation
   - SQL injection protection (SQLAlchemy ORM)
   - Request size limits

---

## Testing Workflow

### Backend Testing

```powershell
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py -v

# Run tests matching pattern
docker-compose exec backend pytest -k "test_login" -v
```

### API Testing

```powershell
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'

# Authenticated request (replace TOKEN)
curl http://localhost:8000/api/v1/learning/paths \
  -H "Authorization: Bearer TOKEN"
```

### Frontend Testing

```powershell
# Navigate to frontend
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage

# E2E tests (if configured)
npm run test:e2e
```

### Load Testing

```bash
# Using Apache Benchmark
ab -n 1000 -c 10 http://localhost:8000/health

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/health
```

---

## Monitoring & Logs

### Viewing Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Last N lines
docker-compose logs --tail=100 backend
```

### Log Locations (in containers)

| Service | Log Location |
|---------|--------------|
| Backend | /app/logs/, stdout |
| Frontend | stdout |
| Nginx | /var/log/nginx/ |
| PostgreSQL | stdout |

### Health Checks

```powershell
# Check all service health
docker-compose ps

# Detailed health check
curl http://localhost:8000/health/detailed
```

---

## Troubleshooting

### Common Issues

#### Database Connection Failed

```powershell
# Check if postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Verify connection
docker-compose exec postgres pg_isready -U vidyaguru
```

#### Migration Errors

```powershell
# Check current migration state
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history

# Reset to clean state (CAUTION: destroys data)
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head
```

#### Container Won't Start

```powershell
# Check logs
docker-compose logs <service-name>

# Force rebuild
docker-compose up -d --build --force-recreate <service-name>

# Check resource usage
docker stats
```

#### CORS Errors

1. Check `CORS_ORIGINS` in `.env`
2. Ensure frontend URL is included
3. Restart backend after changes

#### Rate Limit Hit

```powershell
# Check rate limit headers in response
# X-RateLimit-Remaining, X-RateLimit-Reset

# For testing, you can temporarily increase limits in:
# backend/app/core/security_middleware.py
```

### Useful Commands

```powershell
# Restart all services
docker-compose restart

# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: destroys data)
docker-compose down -v

# View running containers
docker-compose ps

# Execute command in container
docker-compose exec <service> <command>

# View container resource usage
docker stats

# Prune unused resources
docker system prune -a
```

---

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review logs for error messages
3. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Docker version)

---

*विद्या ददाति विनयम् - Knowledge gives humility*
