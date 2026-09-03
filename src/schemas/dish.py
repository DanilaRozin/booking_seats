from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from schemas.base_schema import BaseSchema
from schemas.cafe import CafeShortInfo


class DishBase(BaseModel):
    """Базовая схема для модели 'Блюд'."""

    name: str | None = Field(
        default=None,
        title='Name',
        max_length=40,
    )
    description: str | None = Field(
        default=None,
        title='Description',
        max_length=300,
    )
    photo_id: UUID | None = Field(
        default=None,
        title='Photo Id',
    )
    price: float = Field(
        title='Price',
    )


class DishCreate(DishBase):
    """Схема тела запроса на создание объекта 'Блюд'."""

    name: str = Field(title='Name', max_length=40)
    price: float = Field(title='Price')


class DishInfo(DishBase, BaseSchema):
    """Схема представления из базы данных объектов модели 'Блюда'."""

    id: int | None = Field(
        default=None,
        title='Id',
    )
    cafes: list[CafeShortInfo] | None = Field(
        default=None,
        title='Cafes',
    )
    is_active: bool | None = Field(
        default=None,
        title='Is Active',
    )
    price: float | None = Field(
        default=None,
        title='Price',
    )
    created_at: datetime | None = Field(
        default=None,
        title='Created At',
    )
    updated_at: datetime | None = Field(
        default=None,
        title='Updated At',
    )
    model_config = ConfigDict(from_attributes=True)


class DishUpdate(DishBase):
    """Схема тела запроса на изменение объекта 'Блюд'."""

    price: float | None = Field(
        default=None,
        title='Price',
    )
    is_active: bool | None = Field(
        default=None,
        title='Is Active',
    )
