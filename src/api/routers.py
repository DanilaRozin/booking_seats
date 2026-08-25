from fastapi import APIRouter

from api.endpoints import (
    auth_router,
    cafe_router,
    slot_router,
    table_router,
    user_router,
)
from api.endpoints.media import router as media_router
from services.openapi_tags import OpenAPITags

tags = OpenAPITags()

# Сборка роутера Кафе и вложенного роутера Столов.
cafes = APIRouter(prefix='/cafes')
cafes.include_router(
    cafe_router,
    tags=[tags.add_tag('Кафе', 'Управление кафе')],
)
cafes.include_router(
    table_router,
    prefix='/{cafe_id}/tables',
    tags=[tags.add_tag('Столы', 'Управление столами в кафе')],
)

cafes.include_router(
    slot_router,
    prefix='/{cafe_id}/slots',
    tags=[tags.add_tag('Временные слоты', 'Управления временными слотами')],
)

main_router = APIRouter()
main_router.include_router(media_router, prefix='/media', tags=['Media'])
main_router.include_router(cafes)
main_router.include_router(
    auth_router,
    prefix='/auth',
    tags=[tags.add_tag('Аутентификация', 'Получение данных для последующей авторизации')],
)

main_router.include_router(
    media_router,
    prefix='/media',
    tags=[tags.add_tag('Медиа', 'Загрузка и получение медиафайлов')],
)

main_router.include_router(
    user_router,
    prefix='/users',
    tags=[tags.add_tag('Пользователи', 'Управление пользователями')],
)
