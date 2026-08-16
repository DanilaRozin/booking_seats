def is_email(value: str) -> bool:
    """Проверяется является ли строка Эмайлом или нет."""
    if '@' in value:
        return True
    return False
