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
        )
    description: str | None = Field(
        default=None,
        title='Description',
    )
    photo_id: UUID | None = Field(
        default=None,
        title='Photo Id',
    )
    price: float | None = Field(
        default=None,
        title='Price',
    )


class DishCreate(DishBase):
    """Схема тела запроса на создание объекта 'Блюд'."""

    name: str = Field(title='Name')
    price: float = Field(title='Price')
    cafes_id: list[int] = Field(title='Cafes Id')


class DishInfo(DishBase, BaseSchema):
    """Схема представления из базы данных объектов модели 'Блюда'."""

    id: int = Field(title='Id')
    cafes: list[CafeShortInfo] = Field(title='Cafes')
    is_active: bool = Field(title='Is Active')
    created_at: datetime = Field(title='Created At')
    updated_at: datetime = Field(title='Updated At')

    model_config = ConfigDict(from_attributes=True)


class DishUpdate(DishBase):
    """Схема тела запроса на изменение объекта 'Блюд'."""

    cafes_id: list[int] | None = Field(
        default=None,
        title='Cafes Id',
    )
    is_active: bool | None = Field(
        default=None,
        title='Is Active',
    )
