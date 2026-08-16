from fastapi import APIRouter

from api.endpoints import cafe_router

main_router = APIRouter()

main_router.include_router(
    cafe_router,
    prefix='/cafes',
    tags=['cafes'],
)
