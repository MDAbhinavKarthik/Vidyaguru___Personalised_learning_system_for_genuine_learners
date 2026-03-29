"""
VidyaGuru AI Learning Platform
Main Application Entry Point
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db, close_db
from app.api.v1.router import api_router
from app.api.v1.endpoints.mentor import router as mentor_router

# Import module routers
from app.tasks import router as tasks_router
from app.anti_cheat import router as anti_cheat_router
from app.challenges import challenges_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting VidyaGuru AI Learning Platform...")
    try:
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
        print("   Application will continue, but database may not be ready")
    
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🔗 OpenAPI Schema: http://localhost:8000/openapi.json")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down...")
    try:
        await close_db()
        print("✅ Database connections closed")
    except Exception as e:
        print(f"⚠️  Error closing database: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
## VidyaGuru (विद्यागुरु) - AI-Powered Learning Platform

A personalized learning platform designed to promote **genuine understanding** over memorization.

### Core Features:
- 🎯 **Personalized Learning Paths** - AI-generated curriculum tailored to your goals
- 🤖 **AI Mentor (VidyaGuru)** - Socratic method-based learning assistant
- 📝 **Task Management** - Practice problems with intelligent feedback
- 📓 **Idea Journal** - Document your learning journey with AI insights
- 📊 **Progress Tracking** - XP, streaks, achievements, and analytics
- ⏰ **Smart Reminders** - AI-suggested study schedules
- 🏆 **Gamification** - Levels, badges, and streaks to keep you motivated

### Philosophy:
*"विद्या ददाति विनयम्" - Knowledge gives humility*

Built with wisdom from ancient Indian educational philosophy combined with modern AI technology.

### Authentication:
All endpoints (except auth) require a valid JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```
    """,
    version=settings.VERSION,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation Error",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors"""
    # Log the error (in production, use proper logging)
    print(f"❌ Unexpected error: {exc}")
    
    if settings.ENVIRONMENT == "development":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal Server Error",
                "error": str(exc)
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"}
    )


# Include API Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Include module routers
app.include_router(mentor_router, prefix=settings.API_V1_PREFIX)
app.include_router(tasks_router, prefix=settings.API_V1_PREFIX)
app.include_router(anti_cheat_router, prefix=settings.API_V1_PREFIX)
app.include_router(challenges_router, prefix=settings.API_V1_PREFIX)


# Health Check Endpoints
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API info"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.ENVIRONMENT != "production" else None,
        "wisdom": "विद्या ददाति विनयम् - Knowledge gives humility"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with component status"""
    from app.database import engine
    
    db_status = "connected"
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "components": {
            "api": "healthy",
            "database": db_status,
            "cache": "not_configured"
        },
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        workers=1 if settings.ENVIRONMENT == "development" else 4
    )
