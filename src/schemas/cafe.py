from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from schemas.user import UserBase


class CafeBase(BaseModel):
    """Чистая схема кафе без привязки к менеджерам."""

    name: str = Field(description='Название кафе')
    address: str = Field(description='Адрес кафе')
    phone: str = Field(description='Контактный телефон')
    description: str = Field(description='О кафе')
    photo_id: UUID = Field(
        description='Уникальный идентификатор изображения кафе',
    )

    model_config = ConfigDict(from_attributes=True)


class CafeCreate(CafeBase):
    """Схема создания кафе с привязкой менеджеров."""

    managers_id: list[int] = Field(
        description='Менеджеры проекта',
    )


class CafeShortInfo(BaseModel):
    """Краткая схема кафе."""

    id: int = Field()
    name: str = Field()
    address: str = Field()
    phone: str = Field()
    description: str = Field()
    photo_id: UUID = Field()

    model_config = ConfigDict(from_attributes=True)


class CafeManagersInfo(UserBase):
    """Вложенная схема для получения информации о менеджерах кафе."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class CafeInfo(CafeShortInfo):
    """Схема для работы кафе с БД."""

    is_active: bool = Field()  # delete?
    created_at: datetime = Field()  # delete?
    updated_at: datetime | None  # delete?
    managers: list[CafeManagersInfo] = Field(description='Менеджеры кафе')


class CafeUpdate(CafeCreate):
    """Схема редактирования кафе."""

    name: str | None = Field(default=None)
    address: str | None = Field(default=None)
    phone: str | None = Field(default=None)
    managers_id: list[int] | None = Field(
        default=None,
        description='Новый список менеджеров проекта',
    )
    is_active: bool = Field(default=True)

    # model_config = ConfigDict(from_attributes=True) - это есть в базовой схеме
