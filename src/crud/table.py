from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models import Table
from schemas.table import TableCreate, TableUpdate


class CRUDCTable(CRUDBase[Table, TableCreate, TableUpdate]):
    """Класс для CRUD-операций c ORM-моделью cтолов."""

    async def create(
        self,
        obj_in: TableCreate,
        session: AsyncSession,
        **additional_attrs: object,
    ) -> Table:
        """Создаёт объект модели Столов.

        Args:
            obj_in: Схема с данными для создания объекта Столов.
            session: Асинхронная сессия SQLAlchemy.
            **additional_attrs: Дополнительные атрибуты модели, непереданные в схеме.

        Returns:
            Созданный объект модели Столов.

        """
        table = await super().create(obj_in, session, **additional_attrs)
        await session.refresh(table, attribute_names=['cafe'])
        return table


table_crud = CRUDCTable(Table)
