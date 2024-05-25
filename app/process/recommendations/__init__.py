from fastapi import APIRouter
from .routes import internal_router
from .main import *
recommendations_router = APIRouter()
recommendations_router.include_router(internal_router,tags=["recommendations"])

__all__ = ["recommendations_router", "say_hello"]