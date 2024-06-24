from fastapi import APIRouter
from .routes import internal_router
from .main import *
questions_products_router = APIRouter()
questions_products_router.include_router(internal_router,tags=["questions_products"])

__all__ = ["questions_products_router","get_questions_and_products"]