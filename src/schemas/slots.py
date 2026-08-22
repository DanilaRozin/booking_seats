from datetime import time

from pydantic import BaseModel, ConfigDict, model_validator

from schemas.base_schema import BaseSchema
from schemas.cafe import CafeInfo
from schemas.validators import check_start_and_end_time


class BaseSchemasSlots(BaseModel):
    """Базовая модель Pydantic-схемы для Временных слотов."""

    start_time: time
    end_time: time
    description: str

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def check_time_logic(cls, data: dict) -> dict:
        """Валидация."""
        return check_start_and_end_time(data)


class CreateTimeSlot(BaseSchemasSlots):
    """Pydantic - Схема создания временного слота."""


class UpdateTimeSlot(BaseSchemasSlots):
    """Pydantic-Схема обновления временного слота."""

    start_time: time | None = None
    end_time: time | None = None
    description: str | None = None
    is_active: bool | None = None


class FullTimeSlot(BaseSchema):
    """Pydantic - схема полного представления временных слотов."""

    cafe: CafeInfo
