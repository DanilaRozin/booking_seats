import re
from typing import Annotated, Optional
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.base_schema import BaseSchema
from schemas.user import UserBase
from schemas.validators import validate_phone_number

CAFE_NAME_PATTERN = r'^[a-zA-Z0-9а-яА-ЯёЁ\s\-\,\.\'\"\(\)]+$'

NameBase = Annotated[
    str,
    Field(
        max_length=40,
        examples=['Новое кафе'],
        description='Название кафе. Обязательное поле. Не более 40 символов.',
    ),
]
AddressBase = Annotated[
    str,
    Field(
        max_length=150,
        description='Адрес кафе. Обязательное поле. Не более 150 символов.',
    ),
]
PhoneBase = Annotated[
    str,
    Field(
        description='Контактный телефон. Обязательное поле: +7XXXXXXXXXX или 8XXXXXXXXXX.',
    ),
]
DescriptionBase = Annotated[
    str,
    Field(
        max_length=300,
        description='О кафе. Не более 300 символов.',
    ),
]
PhotoId_Base = Annotated[
    UUID,
    Field(
        description='Уникальный идентификатор изображения кафе в формате UUID.',
    ),
]


class CafeBase(BaseModel):
    """Чистая схема кафе без привязки к менеджерам."""

    name: NameBase
    address: AddressBase
    phone: PhoneBase
    description: Optional[DescriptionBase] = None
    photo_id: Optional[PhotoId_Base] = None

    model_config = ConfigDict(from_attributes=True)

    _validate_phone = field_validator('phone')(validate_phone_number)

    @field_validator('name')
    @classmethod
    def check_cafe_name(cls, value: str) -> str:
        """Проверяет соответствие названия требованиям."""
        if not re.match(CAFE_NAME_PATTERN, value):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail='Недопустимые символы в названии кафе.',
            )
        return value


class CafeCreate(CafeBase):
    """Схема создания кафе с привязкой менеджеров."""

    managers_id: list[int] = Field(
        min_length=1,
        description='ID менеджеров проекта. Обязательное поле.',
    )


class CafeShortInfo(BaseModel):
    """Краткая схема кафе."""

    id: Optional[int] = None
    name: Optional[NameBase] = None
    address: Optional[AddressBase] = None
    phone: Optional[PhoneBase] = None
    description: Optional[DescriptionBase] = None
    photo_id: Optional[PhotoId_Base] = None

    model_config = ConfigDict(from_attributes=True)


class CafeManagersInfo(UserBase):
    """Вложенная схема для получения информации о менеджерах кафе."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class CafeInfo(BaseSchema, CafeShortInfo):
    """Полная схема кафе."""

    managers: list[CafeManagersInfo] = Field(
        default=None,
        description='Менеджеры кафе.',
    )


class CafeUpdate(CafeBase, BaseModel):
    """Схема редактирования кафе."""

    name: Optional[NameBase] = None
    address: Optional[AddressBase] = None
    phone: Optional[PhoneBase] = None
    description: Optional[DescriptionBase] = None
    photo_id: Optional[PhotoId_Base] = None
    managers_id: list[int] | None = Field(
        default=None,
        min_length=1,
        description='Новый список менеджеров кафе.',
    )
    is_active: bool | None = Field(
        default=None,
        description='Новое состояние кафе.',
    )
