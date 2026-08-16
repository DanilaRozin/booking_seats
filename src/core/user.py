from collections.abc import AsyncGenerator, Callable, Coroutine
from typing import Annotated, Any, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin, InvalidPasswordException
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.authentication.transport.bearer import BearerTransport
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .constants import PASSWORD_MIN_LEN, RoleEnum
from .db import get_session
from .settings import settings
from .utils import is_email
from src.models import User
from src.schemas.user import UserCreate
from src.schemas.validators import validate_phone_number


class UserDatabase(SQLAlchemyUserDatabase):
    """Расширем возможности класса SQLAlchemyUserDatabase чтобы добавить поиск по номеру телефона."""

    async def get_by_phone(self, phone: str) -> User | None:
        """Получаем юзера по номеру телефона."""
        phone = validate_phone_number(phone)
        statement = select(self.user_table).where(self.user_table.phone == phone)
        return await self._get_user(statement)


async def get_user_db(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AsyncGenerator[UserDatabase, None]:
    """Отдаёт адаптер БД для fastapi-users, привязанный к текущей сессии."""
    yield UserDatabase(session, User)


# Меняем логику авторизации вдокументации,
# чтобы убраться стндартную форму авторизации
class _TokenOnlyHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> str | None:
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)
        if credentials is None:
            return None
        return credentials.credentials


class HTTPOnlyBearerTransport(BearerTransport):
    """Transport, показывающий в Swagger только поле для вставки токена."""

    def __init__(self) -> None:
        """Заменяет OAuth2PasswordBearer на HTTPBearer-схему."""
        self.scheme = _TokenOnlyHTTPBearer(auto_error=False)


bearer_transport = HTTPOnlyBearerTransport()


def get_jwt_strategy() -> JWTStrategy:
    """Создаёт стратегию для выпуска и проверки JWT."""
    return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """Логика создания/аутентификации/обновления пользователей."""

    async def authenticate(self, login: str, password: str) -> User | None:
        """Аутентифицирует пользователя по email или телефону."""
        user = (
            await self.user_db.get_by_email(login)
            if is_email(login)
            else await self.user_db.get_by_phone(login)
        )

        if user is None:
            self.password_helper.hash(password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            password,
            user.hashed_password,
        )
        if not verified:
            return None
        if updated_password_hash is not None:
            await self.user_db.update(user, {'hashed_password': updated_password_hash})

        return user

    async def validate_password(self, password: str, user: UserCreate | User) -> None:
        """Проверяет пароль на минимальную длину и совпадение с email."""
        if len(password) < PASSWORD_MIN_LEN:
            error = f'Пароль должен содержать не менее {PASSWORD_MIN_LEN} символов'
            raise InvalidPasswordException(reason=error)
        if user.email in password:
            error = 'Пароль не может содержать ваш email'
            raise InvalidPasswordException(reason=error)

    async def on_after_register(self, user: User, request: Optional[Request] = None) -> None:
        """Логирует успешную регистрацию пользователя."""
        print(f'Пользователь {user.email} зарегистрирован.')


async def get_user_manager(
    user_db: UserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Отдаёт UserManager, привязанный к текущей сессии."""
    yield UserManager(user_db)


# Настройка ролей


def require_role(*allowed_roles: RoleEnum) -> Callable[[User], Coroutine[Any, Any, User]]:
    """Проверяем доступ роли.

    Если пользователь суперюзер - неважно какая роль у него в поле role.
    """

    async def dependency(user: User = Depends(current_user)) -> User:
        if user.is_superuser:
            return user
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Недостаточно прав',
            )
        return user

    return dependency


fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_user = fastapi_users.current_user(active=True)
current_admin = require_role(RoleEnum.ADMIN)
current_manager = require_role(RoleEnum.MANAGER, RoleEnum.ADMIN)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
