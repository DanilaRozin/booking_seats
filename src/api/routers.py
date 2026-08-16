from fastapi import APIRouter

from api.endpoints import cafe_router, table_router
from service.openapi_tags import OpenAPITags

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

main_router = APIRouter()
main_router.include_router(cafes)
