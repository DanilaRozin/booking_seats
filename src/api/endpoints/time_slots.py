from typing import Annotated, List

from fastapi import APIRouter, Depends, Path, status

from src.api import SessionDep
from src.api.validators import check_cafes_exists, check_slots_exists
from src.core.user import current_superuser, current_user
from src.crud.time_slots import slot_crud
from src.models.time_slots import Slot
from src.models.user import User
from src.schemas.time_slots import CreateTimeSlot, FullTimeSlot, UpdateTimeSlot
from src.service.time_slot_helper import get_slot_filters_for_user, get_slot_for_user

router = APIRouter()


@router.get(
    '',
    response_model=List[FullTimeSlot],
)
async def get_all_slots(
    cafe_id: Annotated[int, Path],
    session: SessionDep,
    user: User = Depends(current_user),
) -> List[FullTimeSlot]:
    """Возвращаем слоты данного кафе.

    - Для администратора и менеджера: все слоты.
    - Для пользователя: только активные слоты.
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
    cafe_id: Annotated[int, Path],
    slot_id: Annotated[int, Path],
    session: SessionDep,
    user: User = Depends(current_user),
) -> FullTimeSlot:
    """Получение информации о слоте по его ID.

    - Для Администратора и Менеджера - все слоты.
    - Для пользователя - Только активные.
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
    dependencies=[Depends(current_superuser)],
)
async def create_slot(
    cafe_id: Annotated[int, Path],
    slot_in: CreateTimeSlot,
    session: SessionDep,
) -> FullTimeSlot:
    """Создание Временного слота.

    **Доступно только Администратору и Менеджеру данного кафе.**
    Дописать ограничение доступа для Менеджера и его принадлежность.
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
    dependencies=[Depends(current_superuser)],
)
async def update_slot(
    slot_id: Annotated[int, Path],
    cafe_id: Annotated[int, Path],
    slot_in: UpdateTimeSlot,
    session: SessionDep,
) -> FullTimeSlot:
    """Обновление Временного слота.

    Доступно только: Администратору и Менеджеру данного кафе.
    Дописать ограничение доступа для Менеджера и его принадлежность.
    """
    db_slot = await check_slots_exists(
        slot_id,
        session,
        cafe_id,
    )
    return await slot_crud.update(
        db_obj=db_slot,
        obj_in=slot_in,
        session=session,
    )
