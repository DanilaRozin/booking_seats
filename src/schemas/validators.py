from typing import Any, Dict, Type

import phonenumbers
from phonenumbers import NumberParseException
from pydantic import BaseModel, model_validator


def validate_phone_number(value: str | None) -> str | None:
    """Валидация введеного номера и приведение его в правильный формат."""
    if value is None:
        return None
    try:
        # Парсим номер и проверяем, возможно ли его существование
        phone_number = phonenumbers.parse(value, 'RU')
        if not phonenumbers.is_possible_number(phone_number):
            raise ValueError('Неверный формат номера')
        return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException:
        raise ValueError('Неверный формат номера')


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
