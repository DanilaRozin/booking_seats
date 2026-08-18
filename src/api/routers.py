from fastapi import APIRouter

from .endpoints import auth_router, user_router
from src.api.endpoints.time_slots import router as slots_router

main_router = APIRouter()
main_router.include_router(auth_router, prefix='/auth', tags=['Аутентификация'])
main_router.include_router(user_router, prefix='/users', tags=['Пользователи'])
main_router.include_router(slots_router, prefix='/cafes/{cafe_id}/slots', tags=['Временные слоты'])
