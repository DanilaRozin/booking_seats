import json
from typing import AsyncIterator, Optional

from fastapi import Depends, Request, Response
from loguru import logger
from starlette.middleware.base import RequestResponseEndpoint

from models.user import User

from core.logging_config import contextualize_user
from core.user import current_user_optional

SENSITIVE_FIELDS = {'password'}


def mask_sensitive(data: dict) -> dict:
    """Заменяет значения чувствительных полей на '***' перед логированием."""
    return {key: ('***' if key.lower() in SENSITIVE_FIELDS else value) for key, value in data.items()}


async def logging_context_dependency(
    request: Request,
    user: Optional[User] = Depends(current_user_optional),
) -> AsyncIterator[None]:
    """Зависимость для подстановки пользователя в логи."""
    request.state.user = user

    with contextualize_user(
        user_id=user.id if user else None,
        username=user.username if user else None,
    ):
        yield


async def request_logging_middleware(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """Функционал логгирования, создание строк, шифрование секретов."""
    body_bytes = await request.body()
    body_log = None
    if body_bytes:
        try:
            # Специально шифруем чувствительные поля.
            # Пароли, токены и иные ключи из SENSITIVE_FIELDS
            body_log = mask_sensitive(json.loads(body_bytes))
        except (json.JSONDecodeError, UnicodeDecodeError):
            body_log = None

    response = await call_next(request)

    user = getattr(request.state, 'user', None)
    extra_message = getattr(request.state, 'log_message', None)

    line = f'{request.method} {request.url.path} -> {response.status_code}'
    if body_log:
        line = f'{line} | body={json.dumps(body_log, ensure_ascii=False)}'
    if extra_message:
        line = f'{line} | {extra_message}'

    with contextualize_user(
        user_id=user.id if user else None,
        username=user.username if user else None,
    ):
        logger.info(line)

    return response
