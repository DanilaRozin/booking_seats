from typing import Annotated, List

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import selectinload

from api import SessionDep
from api.validators import check_object_exists
from crud import cafe_crud
from crud.slots import slot_crud
from models.slots import Slot
from models.user import User
from schemas.slots import CreateTimeSlot, FullTimeSlot, UpdateTimeSlot

from core.constants import RoleEnum
from core.user import current_manager, current_user

router = APIRouter()


@router.get(
    '',
    response_model=List[FullTimeSlot],
)
async def get_all_slots(
    cafe_id: Annotated[int, Path(description='ID кафе')],
    session: SessionDep,
    user: User = Depends(current_user),
    show_active: Annotated[
        bool | None,
        Query(
            description=('Показывать все слоты в кафе, только активные или только не активные.'),
        ),
    ] = None,
) -> List[FullTimeSlot]:
    """### Получение списка доступных для бронирования временных слотов в кафе.

    * Для **администраторов** и **менеджеров** - все столы (с возможностью выбора),
    * для **пользователей** - только активные.
    """
    await check_object_exists(cafe_crud, cafe_id, session=session)
    if user.role == RoleEnum.MANAGER and show_active is None or user.role == RoleEnum.USER:
        show_active = True
    conditions = [Slot.cafe_id == cafe_id]
    if show_active is not None:
        conditions.append(Slot.is_active.is_(show_active))

    return await slot_crud.get_multi(
        session,
        *conditions,
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
) -> Slot | None:
    """### Получение информации о временном слоте в кафе по его ID.

    * Для **администраторов** и **менеджеров** - все столы
    * Для **пользователей** - только активные.
    """
    conditions = [Slot.cafe_id == cafe_id]
    if user.role == RoleEnum.USER:
        conditions.append(Slot.is_active.is_(True))

    return await check_object_exists(
        slot_crud,
        slot_id,
        session,
        *conditions,
    )


@router.post(
    '',
    response_model=FullTimeSlot,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(current_manager)],
)
async def create_slot(
    cafe_id: Annotated[int, Path(description='ID кафе')],
    slot_in: CreateTimeSlot,
    session: SessionDep,
) -> FullTimeSlot:
    """### Создает нового временного слота в кафе.

    *Только для администраторов и менеджеров.*
    """
    cafe_obj = await check_object_exists(cafe_crud, cafe_id, session)
    new_slot = await slot_crud.create(
        obj_in=slot_in,
        session=session,
        cafe_id=cafe_obj.id,
    )
    return await slot_crud.get_with_relations(
        session,
        new_slot.id,
        selectinload(Slot.cafe),
    )


@router.patch(
    '/{slot_id}',
    response_model=FullTimeSlot,
    dependencies=[Depends(current_manager)],
)
async def update_slot(
    slot_id: Annotated[int, Path(description='ID слота')],
    cafe_id: Annotated[int, Path(description='ID кафе')],
    obj_in: UpdateTimeSlot,
    session: SessionDep,
) -> FullTimeSlot:
    """### Обновление информации о временом слоте в кафе по его ID.

    *Только для администраторов и менеджеров.*
    """
    slot = await check_object_exists(
        slot_crud,
        slot_id,
        session,
        Slot.cafe_id == cafe_id,
    )
    return await slot_crud.update(
        slot,
        obj_in,
        session,
    )
