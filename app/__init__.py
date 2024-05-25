from fastapi import APIRouter

from .process import process_router

approuter = APIRouter()
approuter.include_router(process_router,prefix="/app")

__all__ = ["approuter"]