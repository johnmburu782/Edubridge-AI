from fastapi import APIRouter

from app.api.v1.endpoints import auth, curriculum, dashboard, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(curriculum.router, tags=["curriculum"])
