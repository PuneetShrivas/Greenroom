from fastapi import APIRouter
from .routes import internal_router
from .main import *
clothes_description_router = APIRouter()
clothes_description_router.include_router(internal_router,tags=["clothes_description"])

__all__ = ["clothes_description_router","get_dress_description", "say_hello"]