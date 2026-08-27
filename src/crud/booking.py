from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models import Booking, BookingTableSlot
from schemas.booking import BookingCreate, BookingUpdate


class CRUDBooking(CRUDBase[Booking, BookingCreate, BookingUpdate]):
    """Класс для CRUD-операций c ORM-моделью бронирования."""

    async def create(
        self,
        obj_in: BookingCreate,
        session: AsyncSession,
        user_id: int,
    ) -> Booking:
        """Создаёт объект модели Бронирования.

        Args:
            obj_in: Схема с данными для создания объекта Бронирования.
            session: Асинхронная сессия SQLAlchemy.
            user_id: Идентификатор пользователя, создающего бронирование.

        Returns:
            Созданный объект модели Бронирования.

        """
        booking_data = obj_in.model_dump(exclude={'tables_slots'})
        booking = Booking(**booking_data, user_id=user_id)
        session.add(booking)
        await session.flush()

        for table_slot in obj_in.tables_slots:
            booking_table_slot = BookingTableSlot(
                booking_id=booking.id,
                cafe_id=booking.cafe_id,
                table_id=table_slot.table_id,
                slot_id=table_slot.slot_id,
            )
            session.add(booking_table_slot)

        await session.commit()
        await session.refresh(booking)

        return booking


booking_crud = CRUDBooking(Booking)
