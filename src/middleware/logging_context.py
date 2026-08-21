
from typing import Awaitable, Callable

from fastapi import Request, Response

from core.logging_config import contextualize_user
from core.user import fastapi_users  # проверь, что путь верный под твой проект


async def logging_context_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Middleware для логирования: добавляет контекст пользователя в логи и сохраняет user в request.state.

    Пользователь определяется через fastapi_users.current_user(optional=True).
    Контекст логирования устанавливается через contextualize_user.
    """
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
        return await call_next(request)
