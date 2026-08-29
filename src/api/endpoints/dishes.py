from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from api import SessionDep, UserDep
from api.validators import check_cafe_exists, check_dish_exists
from crud import dish_crud
from models import Dish
from schemas.dish import DishCreate, DishInfo, DishUpdate

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
all_dishes_variants = [
    (RoleEnum.MANAGER, False),
    (RoleEnum.ADMIN, False),
    (RoleEnum.ADMIN, None),
]

router = APIRouter()


@router.get(
    '/',
    summary='Получение списка блюд',
    tags=['Блюда'],
    response_model=list[DishInfo],
)
async def get_all_dishes(
    user: UserDep,
    session: SessionDep,
    show_active: Annotated[
        bool | None,
        Query(
            description=(
                """Показывать все блюда, только активные или только не активные.

                По умолчанию показывает:

                - для пользователя - только активные блюда
                (всегда, в не зависимости от значения параметра).
                - для администратора - все блюда (и активные и не активные)
                - для менеджера - активные блюда
                 """
            ),
        ),
    ] = None,
    cafe_id: Annotated[
        int,
        Query(
            description=(
                'ID кафе, в котором показывать блюда.Если не задано - показывает все блюда во всех кафе'
            ),
        ),
    ] = None,
) -> Sequence[Dish]:
    """Получение списка блюд.

    Для администраторов и менеджеров - все блюда (с возможностью выбора), для пользователей - только активные.
    """
    conditions = []

    if cafe_id is not None:
        await check_cafe_exists(cafe_id, session)
        conditions = [Dish.cafe_id == cafe_id]

    if (user.role, show_active) in only_active_variants:
        show_active = True
    elif (user.role, show_active) in all_dishes_variants:
        show_active = False

    if show_active is not None:
        conditions.append(Dish.is_active.is_(show_active))
    return await dish_crud.get_multi(
        session,
        *conditions,
    )


@router.get(
    '/{dish_id}',
    summary='Получение информации о блюде по его ID',
    tags=['Блюда'],
    response_model=DishInfo,
)
async def get_dish(
    dish_id: Annotated[int, Path(description='ID блюда', gt=0)],
    user: UserDep,
    session: SessionDep,
) -> Dish | None:
    """Получение информации о блюде по его ID.

    Для администраторов и менеджеров - все блюда,
    для пользователей - только активные.
    """
    await check_dish_exists(dish_id, session)

    conditions = [Dish.id == dish_id]
    if user.role == RoleEnum.USER:
        conditions.append(Dish.is_active.is_(True))
    return await dish_crud.get(dish_id, session, *conditions)


@router.post(
    '/',
    response_model=DishInfo,
    tags=['Блюда'],
    summary='Создание нового блюда',
    dependencies=[Depends(current_manager)],
)
async def create_dish(
    dish_schema: DishCreate,
    session: SessionDep,
) -> Dish:
    """Создает новое блюда. Только для администраторов и менеджеров."""
    return await dish_crud.create(
        dish_schema,
        session,
    )


@router.patch(
    '/{dish_id}',
    response_model=DishInfo,
    tags=['Блюда'],
    summary='Обновление информации о блюде по его ID',
    dependencies=[Depends(current_manager)],
)
async def update_dish(
    dish_id: Annotated[int, Path(description='ID блюда', gt=0)],
    session: SessionDep,
    obj_in: DishUpdate,
) -> Dish:
    """Обновление информации о блюде по его ID.

    Только для администраторов и менеджеров.
    """
    dish = await check_dish_exists(dish_id, session)
    return await dish_crud.update(
        dish,
        obj_in,
        session,
    )
