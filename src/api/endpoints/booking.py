from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api import SessionDep, UserDep
from api.validators import check_object_exists, validate_booking_create, validate_booking_update
from crud import booking_crud
from models import Booking, User
from schemas.booking import BookingCreate, BookingInfo, BookingUpdate

from core.constants import RoleEnum
from core.user import current_user

router = APIRouter()


@router.get(
    '/',
    summary='Получение списка бронирований',
    response_model=list[BookingInfo],
)
async def get_all_bookings(
    user: UserDep,
    session: SessionDep,
    show_active: Annotated[bool | None, Query(description='Показывает все бронирования')] = None,
    cafe_id: int | None = None,
    user_id: int | None = None,
) -> Sequence[Booking]:
    """Получение списка бронирований.

    Для администраторов и менеджеров - все бронирования (с возможностью выбора),
    для пользователей - только свои (параметры игнорируются, кроме ID кафе).
    """
    conditions = []

    if user.role == RoleEnum.USER:
        conditions.append(user.id == Booking.user_id)
        conditions.append(Booking.is_active.is_(True))
    else:
        if user.role == RoleEnum.MANAGER and show_active is None:
            show_active = True

        if show_active is not None:
            conditions.append(Booking.is_active.is_(show_active))

        if user_id is not None:
            conditions.append(Booking.user_id == user_id)
    if cafe_id is not None:
        conditions.append(Booking.cafe_id == cafe_id)

    return await booking_crud.get_multi(session, *conditions)


@router.post(
    '/',
    response_model=BookingInfo,
    status_code=status.HTTP_201_CREATED,
    summary='Создание нового бронирования',
)
async def create_booking(
    booking_in: BookingCreate,
    user: Annotated[User, Depends(current_user)],
    session: SessionDep,
) -> Booking:
    """Создает новоe бронированиe.

    *Только для авторизованных пользователей.*
    """
    await validate_booking_create(booking_in, session)
    return await booking_crud.create(
        obj_in=booking_in,
        session=session,
        user_id=user.id,
    )


@router.get(
    '/{booking_id}',
    summary='Получение информации о бронировании по его ID',
    response_model=BookingInfo,
)
async def get_booking_by_id(
    booking_id: int,
    user: UserDep,
    session: SessionDep,
) -> Booking:
    """Получение информации о бронировании по его ID.

    Для администраторов - все бронирования,
    для менеджеров - только связанные с их кафе,
    для пользователей - только свои.
    """
    booking = await check_object_exists(booking_crud, booking_id, session)

    if user.role == RoleEnum.USER and booking.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ к бронированию запрещен',
        )

    if user.role == RoleEnum.MANAGER and booking.cafe_id != user.cafe_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ к бронированию другого кафе запрещен',
        )

    return booking


@router.patch(
    '/{booking_id}',
    summary='Обновление информации о бронировании по его ID.',
    response_model=BookingInfo,
)
async def update_booking(
    booking_id: int,
    booking_in: BookingUpdate,
    user: UserDep,
    session: SessionDep,
) -> Booking:
    """Обновление информации о бронировании по его ID.

    Для администраторов - все бронирования,
    для менеджеров - только связанные с их кафе,
    для пользователей - только свои.
    """
    booking = await check_object_exists(booking_crud, booking_id, session)

    if user.role == RoleEnum.USER and booking.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ к бронированию запрещен',
        )
    if user.role == RoleEnum.MANAGER and booking.cafe_id != user.cafe_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ к бронированию другого кафе запрещен',
        )

    await validate_booking_update(booking, booking_in, session)
    return await booking_crud.update(booking, booking_in, session)
