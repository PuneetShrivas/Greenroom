from fastapi import APIRouter
from .routes import internal_router
from .main import *
season_profiler_router = APIRouter()
season_profiler_router.include_router(internal_router,tags=["season_profiler"])

__all__ = ["season_profiler_router","detect_season_from_image", "detect_season_with_selections"]