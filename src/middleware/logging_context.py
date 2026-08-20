from fastapi import Request

from core.logging_config import contextualize_user
from core.user import fastapi_users


async def logging_context_middleware(request: Request, call_next):
    user = None
    try:
        user = await fastapi_users.current_user(optional=True)()
    except Exception:
        user = None

    with contextualize_user(
        user_id=user.id if user else None,
        username=user.username if user else None,
    ):
        request.state.user = user
        response = await call_next(request)
        return response
