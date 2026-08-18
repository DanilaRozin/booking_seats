from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.time_slots import Slot
from src.schemas.time_slots import CreateTimeSlot, UpdateTimeSlot


class SlotCRUD(CRUDBase):
    """CRUD методы для временных слотов."""

    async def create_slot(
        self,
        db: AsyncSession,
        slot_data: CreateTimeSlot,
        commit: bool = True,
    ) -> Slot:
        """Асинхронный CRUD метод создания объекта."""
        slot = slot_data.model_dump()
        new_slot = Slot(**slot)
        db.add(new_slot)
        if commit:
            await db.commit()
            await db.refresh(new_slot)
        return new_slot

    async def get_slots_for_cafe(
        self,
        db: AsyncSession,
        cafe_id: int,
        is_active: bool | None = None,
    ) -> list[Slot]:
        """Возвращает слоты данного кафе фильтруя на активные и нет."""
        query = select(Slot).where(Slot.cafe_id == cafe_id)

        if is_active is not None:
            query = query.where(Slot.is_active == is_active)

        results = await db.execute(query)
        return results.scalars().all()

    async def get_slot_id(
        self,
        db: AsyncSession,
        cafe_id: int,
        slot_id: int,
        is_active: bool | None = None,
    ) -> Slot:
        """Возвращает Временной слот по его Id."""
        query = select(Slot).where(Slot.cafe_id == cafe_id, Slot.id == slot_id)

        if is_active is not None:
            query = query.where(Slot.is_active == is_active)
        results = await db.execute(query)
        return results.scalar_one_or_none()

    async def update_slot(
        self,
        db: AsyncSession,
        slot_id: int,
        cafe_id: int,
        slot_data: UpdateTimeSlot,
        commit: bool = True,
    ) -> Slot:
        """Асинхронный CRUD метод обновления конкретного слота."""
        slot = await self.get_slot_id(
            db=db,
            slot_id=slot_id,
            cafe_id=cafe_id,
            is_active=None,
        )

        if slot is None:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Слот с ID {slot_id} не найден в кафе {cafe_id}',
            )

        update_data = slot_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(slot, field, value)

        db.add(slot)

        await db.flush()

        if commit:
            await db.commit()
            await db.refresh(slot)

        return slot


slot_crud = SlotCRUD(Slot)
