from fastapi import APIRouter

from .endpoints import auth_router, user_router

main_router = APIRouter()
main_router.include_router(auth_router, prefix='/auth', tags=['Аутентификация'])
main_router.include_router(user_router, prefix='/users', tags=['Пользователи'])
