from fastapi import APIRouter
from .dress_description import clothes_description_router
from .outfit_review import outfit_review_router
from .recommendations import recommendations_router
from .season_profiler import season_profiler_router
from .questions_and_products import questions_products_router
process_router = APIRouter()
process_router.include_router(clothes_description_router,prefix="/dress_description")
process_router.include_router(outfit_review_router,prefix="/outfit_review")
process_router.include_router(recommendations_router,prefix="/recommendations")
process_router.include_router(season_profiler_router,prefix="/season_profiler")
process_router.include_router(questions_products_router,prefix="/questions_products")
