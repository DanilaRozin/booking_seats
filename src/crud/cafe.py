from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models import Cafe, User
from schemas.cafe import CafeBase, CafeCreate, CafeUpdate


class CRUDCafe(CRUDBase[Cafe, CafeCreate, CafeUpdate]):
    """Класс для CRUD-операций c ORM-моделью кафе."""

    async def get_cafe_id_by_name(
        self,
        cafe_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        """Метод возвращает id кафе по названию."""
        db_cafe_id = await session.execute(
            select(Cafe.id).where(
                Cafe.name == cafe_name,
            ),
        )
        return db_cafe_id.scalars().first()

    async def create(
        self,
        obj_in: CafeBase,
        session: AsyncSession,
        user: User = None,
    ) -> Cafe:
        """Метод создает кафе без привязки менеджеров."""
        db_obj = self.model(**obj_in.model_dump())
        db_obj.managers = []
        session.add(db_obj)
        await session.commit()
        await session.flush()
        return db_obj

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


cafe_crud = CRUDCafe(Cafe)
