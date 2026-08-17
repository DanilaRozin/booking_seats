import re

import phonenumbers
from phonenumbers import NumberParseException

CYRILLIC_PATTERN = re.compile(r'[а-яёА-ЯЁ]')
LATIN_PATTERN = re.compile(r'[a-zA-Z]')


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


def validate_username(value: str) -> str:
    """Запрещает одновременное использвоание кириллицы и латиницы в username."""
    is_cyrilic = bool(CYRILLIC_PATTERN.search(value))
    is_latin = bool(LATIN_PATTERN.search(value))
    if is_cyrilic and is_latin:
        raise ValueError('username не может одновременно содержать кириллицу и латиницу.')
    return value
