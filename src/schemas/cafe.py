from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CafeCreate(BaseModel):
    """Схема создания кафе."""

    name: str = Field(
        description='Название кафе',
    )
    address: str = Field(
        description='Адрес кафе',
    )
    phone: str = Field(
        description='Контактный телефон',
    )
    description: str = Field(
        default_factory=str,
        description='О кафе',
    )
    photo_id: UUID = Field(
        default_factory=UUID,
        description='Уникальный идентификатор изображения кафе',
    )
    managers_id: list[int] = Field(
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


class CafeInfo(CafeShortInfo):
    """Схема для работы кафе с БД."""

    managers: List[object] = Field()
    is_active: bool = Field()
    created_at: datetime = Field()
    updated_at: datetime | None = Field(default=None)
    managers: List[object] = Field(default_factory=List[object])
    is_active: bool = Field(default_factory=bool)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class CafeUpdate(CafeCreate):
    """Схема редактирования кафе."""

    name: str = Field(
        default_factory=str,
    )
    address: str = Field(
        default_factory=str,
    )
    phone: str = Field(
        default_factory=str,
    )
    managers_id: list[int] = Field(
        default_factory=list[int],
    )
    is_active: bool = Field(
        default_factory=bool,
    )
