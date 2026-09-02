from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from crud import action_crud, cafe_crud, dish_crud, slot_crud, table_crud
from crud.base import CRUDBase
from models import Booking, BookingTableSlot, Slot, Table, User
from schemas.booking import BookingCreate, BookingUpdate
from schemas.user import UserCreate
from services.media import MediaService

from core.base_model import Base
from core.constants import BookingStatus, RoleEnum
from core.user import UserManager


async def check_object_exists[
    ModelT: Base,
    CreateSchemaT: BaseModel,
    UpdateSchemaT: BaseModel,
](
    crud: CRUDBase[ModelT, CreateSchemaT, UpdateSchemaT],
    obj_id: int,
    session: AsyncSession,
    *conditions: ColumnElement[bool],
) -> ModelT:
    """Проверка существования объекта в БД."""
    obj = await crud.get(obj_id, session, *conditions)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Объект модели {crud.model.__name__} не найден.',
        )
    return obj


async def check_name_duplicate(
    cafe_name: str,
    session: AsyncSession,
) -> None:
    """Проверка уникальности названия кафе."""
    cafe_id = await cafe_crud.get_cafe_id_by_name(
        cafe_name,
        session,
    )
    if cafe_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Кафе с таким названием уже существует',
        )


async def existing_user(user_create: UserCreate, user_manager: UserManager) -> None:
    """Проверка заняты ли username, email или phone(номер телефона)."""
    if await user_manager.user_db.get_by_email(user_create.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Указанный email занят.',
        )

    if await user_manager.user_db.get_by_phone(user_create.phone) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Указанный номер телефона занят.',
        )
    if await user_manager.user_db.get_by_username(user_create.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Указанный username занят.',
        )


async def check_dish_or_action_exists(
    obj_id: int,
async def check_table_slot_booked(
    cafe_id: int,
    table_id: int,
    slot_id: int,
    booking_date: date,
    session: AsyncSession,
    booking_id: int | None = None,
) -> None:
    """Проверяет, не занят ли стол на выбранные дату и слот."""
    conditions = [
        Booking.cafe_id == cafe_id,
        Booking.booking_date == booking_date,
        BookingTableSlot.table_id == table_id,
        BookingTableSlot.slot_id == slot_id,
        Booking.status.in_(
            (
                BookingStatus.BOOKING,
                BookingStatus.ACTIVE,
            ),
        ),
        Booking.is_active.is_(True),
    ]

    if booking_id is not None:
        conditions.append(Booking.id != booking_id)

    booked = await session.execute(
        select(BookingTableSlot.id)
        .join(
            Booking,
            Booking.id == BookingTableSlot.booking_id,
        )
        .where(*conditions),
    )

    if booked.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Выбранный стол уже занят на указанные дату и слот',
        )


async def validate_booking_create(booking_create: BookingCreate, session: AsyncSession) -> None:
    """Проверяет данные для создания бронирования."""
    await check_object_exists(cafe_crud, booking_create.cafe_id, session)

    table_slot_pairs = [(item.table_id, item.slot_id) for item in booking_create.tables_slots]

    if len(table_slot_pairs) != len(set(table_slot_pairs)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='В бронировании указаны повторяющиеся пары стол-слот',
        )

    for table_slot in booking_create.tables_slots:
        await check_object_exists(
            table_crud,
            table_slot.table_id,
            session,
            Table.cafe_id == booking_create.cafe_id,
        )

        await check_object_exists(
            slot_crud,
            table_slot.slot_id,
            session,
            Slot.cafe_id == booking_create.cafe_id,
        )

        await check_table_slot_booked(
            cafe_id=booking_create.cafe_id,
            table_id=table_slot.table_id,
            slot_id=table_slot.slot_id,
            booking_date=booking_create.booking_date,
            session=session,
        )


async def validate_booking_update(
    booking: Booking,
    booking_update: BookingUpdate,
    session: AsyncSession,
) -> None:
    """Проверяет данные для обновления бронирования."""
    if booking_update.tables_slots is None and booking_update.booking_date is None:
        return

    booking_date = (
        booking_update.booking_date if booking_update.booking_date is not None else booking.booking_date
    )

    table_slots = (
        booking_update.tables_slots if booking_update.tables_slots is not None else booking.tables_slots
    )

    if booking_update.tables_slots is not None:
        table_slot_pairs = [(item.table_id, item.slot_id) for item in booking_update.tables_slots]

        if len(table_slot_pairs) != len(set(table_slot_pairs)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='В бронировании указаны повторяющиеся пары стол-слот',
            )

    for table_slot in table_slots:
        await check_object_exists(
            table_crud,
            table_slot.table_id,
            session,
            Table.cafe_id == booking.cafe_id,
        )

        await check_object_exists(
            slot_crud,
            table_slot.slot_id,
            session,
            Slot.cafe_id == booking.cafe_id,
        )

        await check_table_slot_booked(
            cafe_id=booking.cafe_id,
            table_id=table_slot.table_id,
            slot_id=table_slot.slot_id,
            booking_date=booking_date,
            session=session,
            booking_id=booking.id,
        )


def existing_image(photo_id: UUID) -> None:
    """Проверка существует ли файл картинки."""
    try:
        MediaService.get_image_path(photo_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Не найден файл изображения кафе.',
        )


async def validate_managers_id(
    managers_id: list[int],
    session: AsyncSession,
) -> list[int]:
    """Проверка на валидность списка менеджеров."""
    stmt = select(User).where(
        User.id.in_(managers_id),
        User.role == RoleEnum.MANAGER,
    )
    result = await session.execute(stmt)
    db_managers = result.scalars().all()
    if len(db_managers) != len(managers_id):
        bad_managers = set(managers_id) - set(user.id for user in db_managers)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f'Нельзя назначить несуществующих менеджеров {list(bad_managers)}',
        )
    is_not_free = [user.id for user in db_managers if user.cafe_id is not None]
    if is_not_free:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f'Нельзя назначить несвободных менеджеров: {is_not_free}',
        )

    return list(db_managers)
