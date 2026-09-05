from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from schemas.base_schema import BaseSchema
from schemas.cafe import CafeShortInfo


class ActionBase(BaseModel):
    """Базовая схема для модели 'Акции'."""

    description: str | None = Field(
        default=None,
        title='Description',
        max_length=300,
    )
    photo_id: UUID | None = Field(
        default=None,
        title='Photo Id',
    )


class ActionCreate(ActionBase):
    """Схема тела запроса на создание объекта 'Акции'."""

    cafes_id: list[int] = Field(title='Cafes Id')
    description: str = Field(title='Description', max_length=300)
    photo_id: UUID | None = Field(
        default=None,
        title='Photo Id',
    )


class ActionInfo(ActionBase, BaseSchema):
    """Схема представления из базы данных объектов модели 'Акции'."""

    id: int = Field(default=None, title='Id')
    cafes: list[CafeShortInfo] | None = Field(default=None, title='Cafes')
    is_active: bool | None = Field(default=None, title='Is Active')
    created_at: datetime | None = Field(default=None, title='Created At')
    updated_at: datetime | None = Field(default=None, title='Updated At')
    model_config = ConfigDict(from_attributes=True)


class ActionUpdate(ActionBase):
    """Схема тела запроса на изменение объекта 'Акции'."""

    cafes_id: list[int] = Field(title='Cafes Id')
    is_active: bool | None = Field(
        default=None,
        title='Is Active',
    )
