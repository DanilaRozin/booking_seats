from api.endpoints.auth import router as auth_router
from api.endpoints.cafe import router as cafe_router
from api.endpoints.slots import router as slot_router
from api.endpoints.table import router as table_router
from api.endpoints.user import router as user_router

__all__ = [
    'user_router',
    'auth_router',
    'cafe_router',
    'table_router',
    'slot_router',
]
