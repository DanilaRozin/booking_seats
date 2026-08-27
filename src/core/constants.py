from enum import StrEnum
from pathlib import Path

TABLE_DESC_LENGTH = 256
"""Максимальное количество символов для поля "Описание" модели "Столов"."""

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 20

PASSWORD_MIN_LEN = 3

UPLOAD_DIR = Path('uploads')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/jpg', 'image/png'}


class RoleEnum(StrEnum):
    """enum ролей для схем и бд.

    USER - Активный пользвоатель
    MANAGER - Менеджер кафе
    ADMIN - Администратор
    """

    USER = 'USER'
    MANAGER = 'MANAGER'
    ADMIN = 'ADMIN'


class BookingStatus(StrEnum):
    """Статус бронирования.

    BOOKING - Забронировано
    CANCELED - Отменено
    ACTIVE - Клиент подошел
    COMPLETED - Обслуживание завершено
    """

    BOOKING = 'BOOKING'
    CANCELED = 'CANCELED'
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'
