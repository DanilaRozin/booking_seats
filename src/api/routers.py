from fastapi import APIRouter

from src.api.endpoints import auth_router, cafe_router, user_router

main_router = APIRouter()

main_router.include_router(auth_router)
main_router.include_router(user_router)

main_router.include_router(
    cafe_router,
    prefix='/cafes',
    tags=['cafes'],
)
