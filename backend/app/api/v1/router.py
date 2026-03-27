"""
API v1 Router
Aggregates all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    learning,
    tasks,
    journal,
    progress,
    reminders,
    mentor
)


api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(learning.router)
api_router.include_router(tasks.router)
api_router.include_router(journal.router)
api_router.include_router(progress.router)
api_router.include_router(reminders.router)
api_router.include_router(mentor.router)
