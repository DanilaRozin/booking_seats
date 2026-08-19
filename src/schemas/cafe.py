from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from schemas.base_schema import BaseSchema
from schemas.user import UserBase


class CafeBase(BaseModel):
    """Чистая схема кафе без привязки к менеджерам."""

    name: Annotated[str, Field(description='Название кафе')]
    address: Annotated[str, Field(description='Адрес кафе')]
    phone: Annotated[str, Field(description='Контактный телефон')]
    description: str = Field(
        default_factory=str,
        description='О кафе',
    )
    photo_id: UUID = Field(
        default_factory=UUID,
        description='Уникальный идентификатор изображения кафе',
    )

    model_config = ConfigDict(from_attributes=True)


class CafeCreate(CafeBase):
    """Схема создания кафе с привязкой менеджеров."""

    managers_id: list[int] = Field(
        default_factory=list,
        description='Менеджеры проекта',
    )


class CafeShortInfo(BaseModel):
    """Краткая схема кафе."""

    id: int = Field(default_factory=int)
    name: str = Field(default_factory=str)
    address: str = Field(default_factory=str)
    phone: str = Field(default_factory=str)
    description: str = Field(default_factory=str)
    photo_id: UUID = Field(default_factory=UUID)

    model_config = ConfigDict(from_attributes=True)


class CafeManagersInfo(UserBase):
    """Вложенная схема для получения информации о менеджерах кафе."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class CafeInfo(CafeShortInfo):
    """Схема для работы кафе с БД."""

    is_active: bool = Field(default_factory=bool)  # delete?
    created_at: datetime = Field(default_factory=datetime.now)   # delete?
    updated_at: datetime | None   # delete?
    managers: list[CafeManagersInfo] = Field(
        default_factory=list, description='Менеджеры кафе')


class CafeUpdate(CafeCreate):
    """Схема редактирования кафе."""

    name: str | None  = Field(default=None)
    address: str | None = Field(default=None)
    phone: str | None = Field(default=None)
    managers_id: list[int] | None = Field(
        default=None,
        description='Новый список менеджеров проекта',
    )
    is_active: bool = Field(default=True)

    # model_config = ConfigDict(from_attributes=True) - это есть в базовой схеме


class CafeInfo(BaseSchema):
    """Схема представления из базы данных объетов модели "Кафе"."""
