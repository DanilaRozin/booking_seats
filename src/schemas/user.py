from datetime import datetime

from fastapi_users import schemas
from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr, field_validator

from .validators import validate_phone_number, validate_username
from core.constants import RoleEnum


class UserBase(BaseModel):
    """Базовая схема."""

    username: str
    email: EmailStr
    phone: str
    tg_id: str | None = None

    _validate_phone = field_validator('phone')(validate_phone_number)
    _validate_username = field_validator('username')(validate_username)


class UserInfo(UserBase):
    """Схема с полной информацией."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: RoleEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class UserCreate(UserBase, schemas.CreateUpdateDictModel):
    """Схема для регистрации."""

    password: SecretStr


class UserShortInfo(UserBase):
    """Схема с короткой информацией для бронирвоания."""

    id: int


class UserUpdate(schemas.CreateUpdateDictModel):
    """Схема для обновления."""

    # Продублировал, потому что необходимо
    # было выставить везде = None, для patch запросов
    username: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    tg_id: str | None = None
    password: SecretStr | None = None
    is_active: bool | None = None

    _validate_phone = field_validator('phone')(validate_phone_number)
    _validate_username = field_validator('username')(validate_username)


class UserAdminUpdate(UserUpdate):
    """Схема для обновления пользователя Администратором."""

    role: RoleEnum | None = None
    managed_id: int | None = None


class UserLogin(BaseModel):
    """Схема для логина."""

    login: EmailStr | str
    password: SecretStr


class TokenResponse(BaseModel):
    """Схема JWT-токена авторизации."""

    access_token: str
    token_type: str
