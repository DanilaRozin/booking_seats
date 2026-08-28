from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

from fastapi import HTTPException, status


def none_to_404(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:
    """Преобразует возвращаемое обработчиком значение "None" в HTTP-ответ 404."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = await func(*args, **kwargs)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Объект не найден в БД.',
            )
        return result

    return wrapper
