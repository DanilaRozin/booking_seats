from enum import StrEnum

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 50

PASSWORD_MIN_LEN = 3


class RoleEnum(StrEnum):
    """enum для схем и бд."""

    USER = 'USER'
    MANAGER = 'MANAGER'
    ADMIN = 'ADMIN'
