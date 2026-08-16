from sqlalchemy import SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from core.base_model import Base


class Cafe(Base):
    """Модель Кафе."""

    last_table_number: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
    )
