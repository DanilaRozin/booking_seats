from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import UserLogin

from core.db import get_session
from core.user import UserManager, auth_backend, get_user_manager

SessionDep = Annotated[AsyncSession, Depends(get_session)]


router = APIRouter()


@dataclass
class _Credentials:
    username: str
    password: str


@router.post(
    '/login',
    summary='Получение токена авторизации',
)
async def login(
    credentials: UserLogin,
    user_manager: UserManager = Depends(get_user_manager),
) -> Response:
    """Аутентифицирует пользователя по email и паролю, возвращает JWT-токен.

    - **login**: Адрес электроной почти или номер телефона
    - **password**: пароль

    Если пользователь с указаными login/password существует, то вернётся JWT токен.
    """
    user = await user_manager.authenticate(
        login=credentials.login,
        password=credentials.password,
    )
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='LOGIN_BAD_CREDENTIALS',
        )

    strategy = auth_backend.get_strategy()
    response = await auth_backend.login(strategy, user)
    await user_manager.on_after_login(user)
    return response
