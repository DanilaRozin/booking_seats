from typing import Annotated, List

from fastapi import APIRouter, Depends, Path, status

from api import SessionDep
from api.validators import check_cafes_exists
from crud.slots import slot_crud
from models.slots import Slot
from models.user import User
from schemas.slots import CreateTimeSlot, FullTimeSlot, UpdateTimeSlot
from service.slot_helper import get_slot_filters_for_user, get_slot_for_user

from core.user import current_user, get_user_manager

router = APIRouter()


@router.get(
    '',
    response_model=List[FullTimeSlot],
)
async def get_all_slots(
    cafe_id: Annotated[int, Path(description='ID кафе')],
    session: SessionDep,
    user: User = Depends(current_user),
) -> List[FullTimeSlot]:
    """### Получение списка доступных для бронирования временных слотов в кафе.

    * Для **администраторов** и **менеджеров** - все столы (с возможностью выбора),
    * для **пользователей** - только активные.
    """
    await check_cafes_exists(cafe_id=cafe_id, session=session)

    base_conditions = [Slot.cafe_id == cafe_id]
    role_conditions = get_slot_filters_for_user(user)
    all_conditions = base_conditions + role_conditions

    return await slot_crud.get_multi(
        session,
        *all_conditions,
    )


@router.get(
    '/{slot_id}',
    response_model=FullTimeSlot,
)
async def get_slot_from_id(
    cafe_id: Annotated[int, Path(description='ID кафе')],
    slot_id: Annotated[int, Path(description='ID слота')],
    session: SessionDep,
    user: User = Depends(current_user),
) -> FullTimeSlot:
    """### Получение информации о временном слоте в кафе по его ID.

    * Для **администраторов** и **менеджеров** - все столы
    * Для **пользователей** - только активные.
    """
    return await get_slot_for_user(
        slot_id=slot_id,
        cafe_id=cafe_id,
        user=user,
        session=session,
    )


@router.post(
    '',
    response_model=FullTimeSlot,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_user_manager)],
)
async def create_slot(
    cafe_id: Annotated[int, Path(description='ID кафе')],
    slot_in: CreateTimeSlot,
    session: SessionDep,
) -> FullTimeSlot:
    """### Создает нового временного слота в кафе.

    *Только для администраторов и менеджеров.*
    """
    await check_cafes_exists(cafe_id=cafe_id, session=session)
    slot_data_dict = slot_in.model_dump()
    slot_data_dict['cafe_id'] = cafe_id
    final_slot_data = CreateTimeSlot(**slot_data_dict)
    return await slot_crud.create(
        db=session,
        slot_data=final_slot_data,
    )


@router.patch(
    '/{slot_id}',
    response_model=FullTimeSlot,
    dependencies=[Depends(get_user_manager)],
)
async def update_slot(
    slot_id: Annotated[int, Path(description='ID слота')],
    cafe_id: Annotated[int, Path(description='ID кафе')],
    slot_in: UpdateTimeSlot,
    session: SessionDep,
    user: User = Depends(current_user),
) -> FullTimeSlot:
    """### Обновление информации о временом слоте в кафе по его ID.

    *Только для администраторов и менеджеров.*
    """
    db_slot = await get_slot_for_user(
        slot_id,
        cafe_id,
        user,
        session,
    )
    return await slot_crud.update(
        db_obj=db_slot,
        obj_in=slot_in,
        session=session,
    )
