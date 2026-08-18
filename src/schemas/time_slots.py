from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.validators import check_start_and_end_time


class BaseSchemasSlots(BaseModel):
    """Базовая модель Pydantic-схемы для Временных слотов."""

    start_time: time
    end_time: time
    description: str = Field(...)

    model_config = ConfigDict(from_attributes=True)

    validate_time_range = check_start_and_end_time


class CreateTimeSlot(BaseSchemasSlots):
    """Pydantic - Схема создания временного слота."""


class UpdateTimeSlot(BaseSchemasSlots):
    """Pydantic-Схема обновления временного слота."""

    start_time: time | None = None
    end_time: time | None = None
    description: str | None = None
    is_active: bool | None = None


class FullTimeSlot(UpdateTimeSlot):
    """Pydantic - схема полного представления временных слотов."""

    # cafe: <Pydantic-Схема Кафе.>
    created_at: datetime
    updated_at: datetime | None
