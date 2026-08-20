from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Схема с полями базового класса."""

    is_active: bool
    created_at: datetime = Field(examples=['2026-05-24T11:00'])
    updated_at: datetime = Field(examples=['2026-05-24T12:00'])

    model_config = ConfigDict(extra='forbid')
