from fastapi import APIRouter
from .dress_description import clothes_description_router
process_router = APIRouter()
process_router.include_router(clothes_description_router,prefix="/dress_descriptions")