from typing import Any, Optional

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


slot_crud = SlotCRUD(Slot)
