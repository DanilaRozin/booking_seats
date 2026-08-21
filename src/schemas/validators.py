import re
from typing import Any, Dict, Type

from fastapi import HTTPException, status
from pydantic import BaseModel, model_validator

from core.constants import NAME_MAX_LENGTH, NAME_MIN_LENGTH

USERNAME_PATTERN = rf'^[A-Za-z0-9]{{{NAME_MIN_LENGTH},{NAME_MAX_LENGTH}}}+(?:[ _-][A-Za-z0-9]+)*$'
PHONE_PATTERN = r'(?:7|8)\d{10}$'


def validate_phone_number(value: str | None) -> str | None:
    """Валидация введеного номера и приведение его в правильный формат."""
    if value is None:
        return None
    digits = re.sub(r'\D', '', value)
    if not re.match(PHONE_PATTERN, digits):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный формат номера. Ожидается 11 цифр(начиная с 7 или 8)',
        )
    return f'+7{digits[1:]}'


def validate_username(value: str) -> str:
    """Запрещает одновременное использвоание кириллицы и латиницы в username."""
    print(value)
    print(re.match(USERNAME_PATTERN, value))
    if not re.match(USERNAME_PATTERN, value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                'username может содержать только латиницу, цифры и знак '
                '_ (нельзя использовать в начале, конце или два раза подряд)'
            ),
        )
    return value


# -------------------------------------------------------------------------------------
#                               TIME SLOTS
# -------------------------------------------------------------------------------------


def check_start_and_end_time(cls: Type[BaseModel], data: Dict[str, Any]) -> Dict[str, Any]:
    """Валидация полей start_time и end_time."""
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    if start_time is not None and end_time is not None:
        if end_time <= start_time:
            raise ValueError('Поле "start_time должно быть строго меньше поля "end_time"')
    return data


check_start_and_end_time = model_validator(mode='after')(check_start_and_end_time)
# //////////////////////////////////////////////////////////////////////////////////////
