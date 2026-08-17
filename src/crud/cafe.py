from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models import Cafe


class CRUDCTable(CRUDBase[Cafe]):
    """Класс для CRUD-операций c ORM-моделью кафе."""

    @staticmethod
    async def get_new_table_number(
        cafe_id: int,
        session: AsyncSession,
    ) -> int | None:
        """Атомарно увеличивает и возвращает номер нового стола в кафе.

        Returns:
            Новый номер стола или None, если кафе с указанным идентификатором
            не найдено.

        """
        result = await session.execute(
            update(Cafe)
            .where(Cafe.id == cafe_id)
            .values(
                last_table_number=Cafe.last_table_number + 1,
            )
            .returning(Cafe.last_table_number),
        )
        return result.scalars().first()


cafe_crud = CRUDCTable(Cafe)
