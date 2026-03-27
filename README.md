# VidyaGuru (विद्यागुरु) - AI-Powered Learning Platform

> *"विद्या ददाति विनयम्" - Knowledge gives humility*

An intelligent, personalized learning platform designed to promote **genuine understanding** over memorization, combining modern AI with timeless educational wisdom.

## 🌟 Features

### Core Learning Features
- **🎯 Personalized Learning Paths** - AI-generated curriculum tailored to your goals and pace
- **🤖 AI Mentor (VidyaGuru)** - Socratic method-based conversational learning
- **📝 Task Management** - Coding exercises, quizzes, and projects with intelligent feedback
- **📓 Idea Journal** - Document insights with AI-powered reflection
- **📊 Progress Tracking** - XP, levels, streaks, and skill analytics

### Unique Elements
- **🏆 Gamification** - Achievements, streaks, and leaderboards
- **⏰ Smart Reminders** - AI-suggested study schedules
- **🛡️ Anti-Cheat Detection** - Typing pattern analysis to ensure genuine learning
- **🕉️ Ancient Wisdom** - Integration of Indian philosophical insights

## 🏗️ Architecture

```
vidyaguru/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Security, config
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry
│   ├── alembic/            # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── SYSTEM_BLUEPRINT.md     # Detailed architecture
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- Docker & Docker Compose (optional)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd vidyaguru

# Copy environment file and configure
cp .env.example .env
# Edit .env with your values

# Start services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Access API docs
open http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Clone and navigate
git clone <repo-url>
cd vidyaguru/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp ../.env.example .env
# Edit .env with your database URL and keys

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## 📚 API Documentation

Once running, access the interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key Endpoints

| Module | Endpoints |
|--------|-----------|
| **Auth** | `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/refresh` |
| **Learning** | `/api/v1/learning/paths`, `/api/v1/learning/modules` |
| **Tasks** | `/api/v1/tasks`, `/api/v1/tasks/submit` |
| **Mentor** | `/api/v1/mentor/chat`, `/api/v1/mentor/explain` |
| **Journal** | `/api/v1/journal/entries`, `/api/v1/journal/insights` |
| **Progress** | `/api/v1/progress/overview`, `/api/v1/progress/achievements` |

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `SECRET_KEY` | JWT signing key | ✅ |
| `GEMINI_API_KEY` | Google Gemini API key for AI mentor | ✅ |
| `CORS_ORIGINS` | Allowed CORS origins | ✅ |

See `.env.example` for full list.

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## 📦 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by ancient Indian educational philosophy (Guru-Shishya tradition)
- Built with modern AI and software engineering best practices
- Special thanks to the open-source community

---

*"श्रद्धावान् लभते ज्ञानम्" - One who has faith attains knowledge* 🙏
