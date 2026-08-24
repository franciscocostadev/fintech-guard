from fastapi import APIRouter

from app.api.routes import auth, health, home, predict

api_router = APIRouter()
api_router.include_router(home.router)
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(predict.router)

__all__ = ["api_router"]
