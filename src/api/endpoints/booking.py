from fastapi import APIRouter, status

from api import SessionDep, UserDep
from api.validators import validate_booking_create
from crud import booking_crud
from models import Booking
from schemas.booking import BookingCreate, BookingInfo

router = APIRouter()


@router.post(
    '/',
    response_model=BookingInfo,
    status_code=status.HTTP_201_CREATED,
    summary='Создание нового бронирования',
)
async def create_booking(
    booking_in: BookingCreate,
    user: UserDep,
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
