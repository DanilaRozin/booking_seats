from datetime import time

from pydantic import BaseModel, ConfigDict, model_validator

from schemas.base_schema import BaseSchema
from schemas.cafe import CafeInfo
from schemas.validators import check_start_and_end_time


class BaseSchemasData(BaseModel):
    """Базовая модель Pydantic-схемы для Временных слотов."""

    start_time: time
    end_time: time
    description: str


class CreateTimeSlot(BaseSchemasData):
    """Pydantic - Схема создания временного слота."""

    @model_validator(mode='before')
    @classmethod
    def check_time_logic(cls, data: dict) -> dict:
        """Валидация."""
        return check_start_and_end_time(data)


class UpdateTimeSlot(BaseSchemasData):
    """Pydantic-Схема обновления временного слота."""

    start_time: time | None = None
    end_time: time | None = None
    description: str | None = None
    is_active: bool | None = None

    @model_validator(mode='before')
    @classmethod
    def check_time_logic(cls, data: dict) -> dict:
        """Валидация."""
        return check_start_and_end_time(data)


class FullTimeSlot(BaseSchema, BaseSchemasData):
    """Pydantic - схема полного представления временных слотов."""

    id: int
    cafe: CafeInfo | None = None

    model_config = ConfigDict(from_attributes=True)
