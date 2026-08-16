from uuid import UUID
from pydantic import BaseModel, Field


class MediaResponse(BaseModel):
    """Схема ответа при успешной загрузке изображения."""

    id: UUID = Field(
        ...,
        description="Уникальный идентификатор изображения (UUID4)",
    )
    filename: str = Field(
        ...,
        description="Оригинальное или сгенерированное имя файла",
    )
    content_type: str = Field(
        ...,
        description="MIME-тип изображения",
    )

    class Config:
        from_attributes = True
