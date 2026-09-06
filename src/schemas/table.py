from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from schemas.base_schema import BaseSchema
from schemas.cafe import CafeShortInfo

from core.constants import TABLE_DESC_LENGTH


class TableBase(BaseModel):
    """Базовая схема для модели "Столов"."""

    description: Annotated[
        str | None,
        Field(max_length=TABLE_DESC_LENGTH),
    ] = None
    seat_number: Annotated[PositiveInt | None, Field(ge=1, examples=[1])] = None

    model_config = ConfigDict(extra='forbid', from_attributes=True)


class TableCreate(TableBase):
    """Схема тела запроса на создание объекта "Столов"."""

    seat_number: Annotated[PositiveInt, Field(ge=1, examples=[1])]


class TableUpdate(TableBase):
    """Схема тела запроса на изменение объекта "Столов"."""

    is_active: bool | None = None


class TableInfo(TableBase, BaseSchema):
    """Схема представления из базы данных объетов модели "Столы"."""

    id: int
    cafe: CafeShortInfo

    model_config = ConfigDict(from_attributes=True)
