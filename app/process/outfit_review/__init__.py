from fastapi import APIRouter
from .routes import internal_router
from .main import *
outfit_review_router = APIRouter()
outfit_review_router.include_router(internal_router,tags=["outfit_review"])

__all__ = ["outfit_review_router","get_review"]