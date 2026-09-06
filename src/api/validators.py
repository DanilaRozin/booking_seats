from datetime import date, datetime, time
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from crud import cafe_crud, slot_crud, table_crud
from crud.base import CRUDBase
from models import Booking, BookingTableSlot, Slot, Table, User
from schemas.booking import BookingCreate, BookingUpdate
from schemas.cafe import CafeUpdate
from schemas.user import UserCreate, UserUpdate
from services.media import MediaService

from core.base_model import Base
from core.constants import MOSCOW_TZ, BookingStatus, RoleEnum
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
    check_active: bool = True,
) -> ModelT:
    """Проверка существования объекта в БД."""
    obj = await crud.get(obj_id, session, *conditions)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Объект не найден.',
        )
    if check_active and not obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Объект неактивен.',
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


def check_slot_not_started(slot: Slot, booking_date: date) -> None:
    """Проверяет, что слот на указанную дату ещё не начался."""
    slot_datetime = datetime.combine(booking_date, slot.start_time)
    if slot_datetime <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Слот {slot.start_time.strftime("%H:%M")} на {booking_date} уже начался или прошёл.',
        )


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


async def check_booking_datetime(
    booking_date: date,
    slot: Slot,
) -> None:
    """Проверяет, что дата и временной слот бронирования ещё не начались."""
    now = datetime.now(MOSCOW_TZ)

    if booking_date < now.date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя создать бронирование на прошедшую дату',
        )

    if booking_date == now.date() and slot.start_time <= now.time():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя забронировать уже начавшийся временной слот',
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
        table = await check_object_exists(
            table_crud,
            table_slot.table_id,
            session,
            Table.cafe_id == booking_create.cafe_id,
            check_active=True,
        )
        if table.seat_number < booking_create.guest_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Количество гостей привышает количество мест за столом.',
            )
        slot = await check_object_exists(
            slot_crud,
            table_slot.slot_id,
            session,
            Slot.cafe_id == booking_create.cafe_id,
            check_active=True,
        )

        check_booking_datetime(
            booking_date=booking_create.booking_date,
            slot=slot,
        )

        check_slot_not_started(slot, booking_create.booking_date)
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
        table = await check_object_exists(
            table_crud,
            table_slot.table_id,
            session,
            Table.cafe_id == booking.cafe_id,
            check_active=True,
        )
        if table.seat_number < booking_update.guest_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Количество гостей привышает количество мест за столом.',
            )

        slot = await check_object_exists(
            slot_crud,
            table_slot.slot_id,
            session,
            Slot.cafe_id == booking.cafe_id,
            check_active=True,
        )

        check_slot_not_started(slot, booking_date)

        check_booking_datetime(
            booking_date=booking_date,
            slot=slot,
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
    cafe_id: int | None = None,
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
    is_not_free = [
        user.id
        for user in db_managers
        if ((user.cafe_id != cafe_id and user.cafe_id is not None) or not user.is_active)
    ]
    if is_not_free:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f'Нельзя назначить несвободных или неактивных менеджеров: {is_not_free}',
        )

    return list(db_managers)


def ensure_permissions(
    user: User,
    user_obj: User,
) -> None:
    """Запрещает менеджерам редактировать админов и других менеджеров."""
    if (user_obj.role in [RoleEnum.ADMIN, RoleEnum.MANAGER] or user_obj.is_superuser) and (
        not ((user.role == RoleEnum.ADMIN or user.is_superuser) or user.id == user_obj.id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='У вас недостаточно прав для изменения данной учетной записи',
        )


def ensure_can_deactivate(
    obj_in: UserUpdate | CafeUpdate,
    user: User,
    user_obj: User = None,
    user_id: int = None,
) -> None:
    """Запрещает деактивацию всем, кроме суперюзера.

    Предназначена для использования в patch запросах к юзерам и кафе.
    """
    if user_obj:
        ensure_permissions(user, user_obj)
    if obj_in.is_active is False and user.role != RoleEnum.ADMIN and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='У вас недостаточно прав для деактивации.',
        )
    if obj_in.is_active is False and user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя деактивировать самого себя.',
        )


def ensure_can_change_role(
    obj_in: UserUpdate,
    user: User,
    user_obj: User | None = None,
    user_id: int | None = None,
) -> None:
    """Запрещает менять роль всем, кроме суперюзера и админа."""
    if user_obj:
        ensure_permissions(user, user_obj)

    if (
        obj_in.role
        and obj_in.role in [RoleEnum.ADMIN, RoleEnum.MANAGER]
        and user.role != RoleEnum.ADMIN
        and not user.is_superuser
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='У вас недостаточно прав для изменения роли.',
        )

    if obj_in.role and user_id == user.id and obj_in.role != user_obj.role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя сменить роль самому себе.',
        )


async def validate_time_intersection(
    session: AsyncSession,
    cafe_id: int,
    start_time: time,
    end_time: time,
    exclude_id: Optional[int] = None,
) -> None:
    """Проверяет уникальность временного слота (отсутствие пересечений)."""
    conflicts = await slot_crud.check_time_slot(
        session=session,
        cafe_id=cafe_id,
        start_time=start_time,
        end_time=end_time,
        exclude_id=exclude_id,
    )
    if conflicts:
        conflict_details = [
            f'{c.id} ({c.start_time.strftime("%H:%M")}-{c.end_time.strftime("%H:%M")})' for c in conflicts
        ]
        error_message = (
            'Данное время пересекается со следующими слотами: '
            f'{", ".join(conflict_details)}. '
            'Пожалуйста, выберите другое время.'
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_message,
        )


async def validate_slot_update_rules(
    session: AsyncSession,
    slot: Slot,
    obj_in: Dict[str, Any],
    cafe_id: int,
) -> None:
    """Проверяет бизнес-правила при обновлении слота."""
    new_is_active = obj_in.is_active

    if not slot.is_active and new_is_active is True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                'Невозможно восстановить активность слота. '
                'Деактивированные слоты нельзя активировать повторно.'
            ),
        )

    will_be_active = new_is_active if new_is_active is not None else slot.is_active

    if will_be_active:
        new_start = obj_in.start_time if obj_in.start_time is not None else slot.start_time
        new_end = obj_in.end_time if obj_in.end_time is not None else slot.end_time

        await validate_time_intersection(
            session=session,
            cafe_id=cafe_id,
            start_time=new_start,
            end_time=new_end,
            exclude_id=slot.id,
        )
