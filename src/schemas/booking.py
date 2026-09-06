from datetime import date

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator

from schemas.base_schema import BaseSchema
from schemas.cafe import CafeShortInfo
from schemas.slots import BaseSchemasData
from schemas.table import TableBase
from schemas.user import UserShortInfo

from .validators import validate_booking_date
from core.constants import BookingStatus


class BookingTableSlot(BaseModel):
    """Схема пары стол-временной слот."""

    table_id: PositiveInt
    slot_id: PositiveInt

    model_config = ConfigDict(extra='forbid')


class BookingTableSlotShortInfo(BaseModel):
    """Краткая информация о столе и временном слоте."""

    table: TableBase
    slot: BaseSchemasData

    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    """Схема создания бронирования."""

    cafe_id: PositiveInt
    tables_slots: list[BookingTableSlot] = Field(min_length=1)
    guest_number: PositiveInt
    note: str | None = None
    booking_date: date

    _validate_booking_date = field_validator('booking_date')(validate_booking_date)
    model_config = ConfigDict(extra='forbid')


class BookingUpdate(BaseModel):
    """Схема изменения бронирования."""

    tables_slots: list[BookingTableSlot] | None = None
    guest_number: PositiveInt | None = None
    note: str | None = None
    status: BookingStatus | None = None
    booking_date: date | None = None
    is_active: bool | None = None

    model_config = ConfigDict(extra='forbid')


class BookingInfo(BaseSchema):
    """Схема информации о бронировании."""

    id: int
    user: UserShortInfo
    cafe: CafeShortInfo
    tables_slots: list[BookingTableSlotShortInfo]
    guest_number: int
    note: str | None
    status: BookingStatus
    booking_date: date

    model_config = ConfigDict(from_attributes=True)
