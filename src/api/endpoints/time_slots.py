from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.api import SessionDep
from src.core.constants import RoleEnum
from src.core.user import current_user
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

    - Для администратора: все слоты.
    - Для пользователя и менеджера: только активные слоты.
    """
    if user.role == RoleEnum.ADMIN:
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
    В будущем дописать валидацию на существование: Кафе, Слота.
    """
    if user.role == RoleEnum.ADMIN or user.role == RoleEnum.MANAGER:
        filter_active = None
    else:
        filter_active = True

    slot = await slot_crud.get_slot_id(
        db=session,
        slot_id=slot_id,
        cafe_id=cafe_id,
        is_active=filter_active,
    )

    if slot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Слот с ID {slot_id} не найден для кафе {cafe_id}',
        )

    return slot


@router.post(
    '',
    response_model=FullTimeSlot,
    status_code=status.HTTP_201_CREATED,
)
async def create_slot(
    cafe_id: Annotated[int, Path],
    slot_in: CreateTimeSlot,
    session: SessionDep,
    user: dict = Depends(current_user),
) -> FullTimeSlot:
    """Создание Временного слота.

    **Доступно только Администратору и Менеджеру данного кафе.**
    В будущем: Дописать валидацию на существование Кафе, Слота.
    Дописать валидацию на SuperUser, Manager и приндажлежность его к данному кафе.
    """
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
)
async def update_slot(
    slot_id: Annotated[int, Path],
    cafe_id: Annotated[int, Path],
    slot_in: UpdateTimeSlot,
    session: SessionDep,
    user: dict = Depends(current_user),
) -> FullTimeSlot:
    """Обновление Временного слота.

    Доступно только: Администратору и Менеджеру данного кафе.
    В Будущем дописать валидацию на SuperUser, Manager и его приндлежность к данному кафе.
    """
    return await slot_crud.update_slot(
        db=session,
        slot_id=slot_id,
        cafe_id=cafe_id,
        slot_data=slot_in,
        commit=True,
    )
