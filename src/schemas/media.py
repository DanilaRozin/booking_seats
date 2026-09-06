from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class MediaResponse(BaseModel):
    """Схема ответа при успешной загрузке изображения."""

    id: Annotated[
        UUID,
        Field(description='Уникальный идентификатор изображения (UUID4)'),
    ]
    filename: Annotated[
        str,
        Field(description='Оригинальное или сгенерированное имя файла'),
    ]

    class Config:
        """Конфигурация Pydantic схемы."""

        from_attributes = True
