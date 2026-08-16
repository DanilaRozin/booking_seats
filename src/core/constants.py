from enum import StrEnum

TABLE_DESC_LENGTH = 256
"""Максимальное количество символов для поля "Описание" модели "Столов"."""

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 50

PASSWORD_MIN_LEN = 3


class RoleEnum(StrEnum):
    """enum для схем и бд."""

    USER = 'USER'
    MANAGER = 'MANAGER'
    ADMIN = 'ADMIN'
