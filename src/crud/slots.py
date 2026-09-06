from datetime import time
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models.slots import Slot
from schemas.slots import CreateTimeSlot, UpdateTimeSlot


class SlotCRUD(CRUDBase[Slot, CreateTimeSlot, UpdateTimeSlot]):
    """CRUD методы для временных слотов."""

    async def get_with_relations(
        self,
        session: AsyncSession,
        obj_id: int,
        *load_options: Any,
    ) -> Optional[Any]:
        """Получает объект по ID и сразу загружает указанные связи."""
        stmt = select(self.model).where(self.model.id == obj_id)

        if load_options:
            stmt = stmt.options(*load_options)

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def check_time_slot(
        self,
        session: AsyncSession,
        cafe_id: int,
        start_time: time,
        end_time: time,
        exclude_id: Optional[int] = None,
    ) -> List[Slot]:
        """Проверка наличия пересечения временных слотов.

        exclude_id - ID слота который нужно игнорировать.
        """
        db = select(Slot).where(
            Slot.cafe_id == cafe_id,
            Slot.start_time < end_time,
            Slot.end_time > start_time,
        )
        if exclude_id is not None:
            db = db.where(Slot.id != exclude_id)
        db = db.with_for_update()
        result = await session.execute(db)
        return result.scalars().all()


slot_crud = SlotCRUD(Slot)
