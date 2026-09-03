from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from api import SessionDep, UserDep
from api.validators import check_object_exists
from crud import action_crud, cafe_crud
from models import Action
from schemas.action import ActionCreate, ActionInfo, ActionUpdate

from core.constants import RoleEnum
from core.user import current_manager

only_active_variants = [
    (RoleEnum.MANAGER, True),
    (RoleEnum.MANAGER, None),
    (RoleEnum.ADMIN, True),
    (RoleEnum.USER, True),
    (RoleEnum.USER, False),
    (RoleEnum.USER, None),
]
all_actions_variants = [
    (RoleEnum.MANAGER, False),
    (RoleEnum.ADMIN, False),
    (RoleEnum.ADMIN, None),
]

router = APIRouter()


@router.get(
    '/',
    summary='Получение списка акций',
    response_model=list[ActionInfo],
)
async def get_all_actions(
    user: UserDep,
    session: SessionDep,
    show_active: Annotated[
        bool | None,
        Query(
            description=(
                'Показывать все акции, только активные или только не активные.\n\n'
                'По умолчанию показывает:\n\n'
                '- для пользователя - только активные\n'
                '(всегда, в не зависимости от значения параметра).\n'
                '- для администратора - все (и активные и не активные)\n'
                ' - для менеджера - активные'
            ),
        ),
    ] = None,
    cafe_id: Annotated[
        int,
        Query(
            description=(
                'ID кафе, в котором показывать акции.Если не задано - показывает все акции во всех кафе'
            ),
        ),
    ] = None,
) -> Sequence[Action]:
    """Получение списка акций.

    Для администраторов и менеджеров - все (с возможностью выбора), для пользователей - только активные.
    """
    conditions = []

    if cafe_id is not None:
        await check_object_exists(cafe_crud, cafe_id, session)
        conditions = [Action.cafe_id == cafe_id]

    if (user.role, show_active) in only_active_variants:
        show_active = True
    elif (user.role, show_active) in all_actions_variants:
        show_active = False

    if show_active is not None:
        conditions.append(Action.is_active.is_(show_active))
    return await action_crud.get_multi(
        session,
        *conditions,
    )


@router.get(
    '/{action_id}',
    summary='Получение информации об акции по ее ID',
    response_model=ActionInfo,
)
async def get_action(
    action_id: Annotated[int, Path(description='ID акции', gt=0)],
    user: UserDep,
    session: SessionDep,
) -> Action | None:
    """Получение информации об акции по ее ID.

    Для администраторов и менеджеров - все,
    для пользователей - только активные.
    """
    await check_object_exists(action_crud, action_id, session)

    conditions = [Action.id == action_id]
    if user.role == RoleEnum.USER:
        conditions.append(Action.is_active.is_(True))
    return await action_crud.get(action_id, session, *conditions)


@router.post(
    '/',
    response_model=ActionInfo,
    summary='Создание новой акции',
    dependencies=[Depends(current_manager)],
)
async def create_action(
    action_schema: ActionCreate,
    session: SessionDep,
) -> Action:
    """Создает новую акцию. Только для администраторов и менеджеров."""
    return await action_crud.create(
        action_schema,
        session,
    )


@router.patch(
    '/{action_id}',
    response_model=ActionInfo,
    summary='Обновление информации об акции по ее ID',
    dependencies=[Depends(current_manager)],
)
async def update_action(
    action_id: Annotated[int, Path(description='ID акции', gt=0)],
    session: SessionDep,
    obj_in: ActionUpdate,
) -> ActionCreate:
    """Обновление информации об акции по ее ID.

    Только для администраторов и менеджеров.
    """
    action = await check_object_exists(action_crud, action_id, session)
    return await action_crud.update(
        action,
        obj_in,
        session,
    )
