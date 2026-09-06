from datetime import time
from typing import Optional, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from schemas.base_schema import BaseSchema
from schemas.cafe import CafeShortInfo
from schemas.validators import validate_time_pair


class BaseSchemasData(BaseModel):
    """Базовая модель Pydantic-схемы для Временных слотов."""

    start_time: time
    end_time: time
    description: str

    model_config = ConfigDict(from_attributes=True)


class CreateTimeSlot(BaseSchemasData):
    """Pydantic - Схема создания временного слота."""

    @model_validator(mode='before')
    @classmethod
    def check_time_logic(cls, data: dict) -> dict:
        """Валидация."""
        validate_time_pair(
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            require_both=True,
        )
        return data


class UpdateTimeSlot(BaseModel):
    """Pydantic-Схема обновления временного слота."""

    start_time: Optional[time] | None = Field(
        default=None,
        description='Новое начальное время.',
    )
    end_time: Optional[time] | None = Field(
        default=None,
        description='Новое конечное время.',
    )
    description: Optional[str] | None = Field(
        default=None,
        description='Новое описание.',
    )
    is_active: Optional[bool] | None = Field(
        default=None,
        description='Активен ли слот.',
    )
    model_config = ConfigDict(extra='ignore')

    @model_validator(mode='after')
    def check_time_logic_for_update(self: Self) -> Self:
        """Валидация."""
        validate_time_pair(
            start_time=self.start_time,
            end_time=self.end_time,
            require_both=False,
        )
        return self


class FullTimeSlot(BaseSchema, BaseSchemasData):
    """Pydantic - схема полного представления временных слотов."""

    id: int
    cafe: CafeShortInfo | None = None

    model_config = ConfigDict(from_attributes=True)
