import phonenumbers
from phonenumbers import NumberParseException


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
