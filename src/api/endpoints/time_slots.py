from typing import Annotated, List

from fastapi import APIRouter, Depends, Path, status

from src.api import SessionDep
from src.api.validators import check_cafes_exists, check_slots_exists
from src.core.constants import RoleEnum
from src.core.user import current_superuser, current_user
from src.crud.time_slots import slot_crud
from src.models.user import User
from src.schemas.time_slots import CreateTimeSlot, FullTimeSlot, UpdateTimeSlot

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
    if user.role == RoleEnum.ADMIN or user.role == RoleEnum.MANAGER:
        filter_active = None
    else:
        filter_active = True

    return await slot_crud.get_slots_for_cafe(
        db=session,
        cafe_id=cafe_id,
        is_active=filter_active,
    )


@router.get(
    '{slot_id}',
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
    await check_cafes_exists(cafe_id=cafe_id, session=session)
    await check_slots_exists(slot_id=slot_id, session=session)
    if user.role == RoleEnum.ADMIN or user.role == RoleEnum.MANAGER:
        filter_active = None
    else:
        filter_active = True

    return await slot_crud.get_slot_id(
        db=session,
        slot_id=slot_id,
        cafe_id=cafe_id,
        is_active=filter_active,
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
    return await slot_crud.create_slot(
        db=session,
        slot_data=final_slot_data,
        commit=True,
    )


@router.patch(
    '{slot_id}',
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
    await check_cafes_exists(cafe_id=cafe_id, session=session)
    await check_slots_exists(slot_id=slot_id, session=session)
    return await slot_crud.update_slot(
        db=session,
        slot_id=slot_id,
        cafe_id=cafe_id,
        slot_data=slot_in,
        commit=True,
    )
