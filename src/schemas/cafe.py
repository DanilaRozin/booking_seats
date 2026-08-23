from pydantic import ConfigDict

from schemas.base_schema import BaseSchema


class CafeInfo(BaseSchema):
    """Схема представления из базы данных объетов модели "Кафе"."""

    model_config = ConfigDict(from_attributes=True)
