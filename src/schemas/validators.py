import re
from datetime import time
from typing import Optional

from fastapi import HTTPException, status

from core.constants import NAME_MAX_LENGTH, NAME_MIN_LENGTH

USERNAME_PATTERN = rf'^[A-Za-z0-9]{{{NAME_MIN_LENGTH},{NAME_MAX_LENGTH}}}+(?:_[A-Za-z0-9]+)*$'
PHONE_PATTERN = r'(?:7|8)\d{10}$'


def validate_phone_number(value: str | None) -> str | None:
    """Валидация введеного номера и приведение его в правильный формат."""
    digits = re.sub(r'\D', '', value)
    if not re.match(PHONE_PATTERN, digits):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный формат номера. Ожидается 11 цифр(начиная с 7 или 8)',
        )
    return f'+7{digits[1:]}'


def validate_username(value: str) -> str:
    """Запрещает одновременное использвоание кириллицы и латиницы в username."""
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


def validate_time_pair(
    start_time: Optional[time],
    end_time: Optional[time],
    require_both: bool = False,
) -> None:
    """Универсальная функция проверки времени."""
    if require_both:
        if start_time is None or end_time is None:
            raise ValueError('Поля start_time и end_time обязательны для создания слота')

    if start_time is not None and end_time is not None:
        if end_time <= start_time:
            raise ValueError('end_time должен быть строго больше start_time')


# //////////////////////////////////////////////////////////////////////////////////////
