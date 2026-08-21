from enum import StrEnum

TABLE_DESC_LENGTH = 256
"""Максимальное количество символов для поля "Описание" модели "Столов"."""

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 20

PASSWORD_MIN_LEN = 3


class RoleEnum(StrEnum):
    """enum ролей для схем и бд.

    USER - Активный пользвоатель
    MANAGER - Менеджер кафе
    ADMIN - Администратор
    """

    USER = 'USER'
    MANAGER = 'MANAGER'
    ADMIN = 'ADMIN'
