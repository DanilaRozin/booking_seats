from collections.abc import Sequence
from typing import Annotated, Any, Callable

from fastapi import APIRouter, Depends, Path, Query, Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from api import SessionDep, UserDep
from api.validators import check_object_exists
from crud import cafe_crud, dish_crud
from models import Dish
from schemas.dish import DishCreate, DishInfo, DishUpdate
from services.media import MediaService

from core.constants import RoleEnum
from core.user import current_manager_without_cafe

DISHES_CACHE_SECONDS = 60

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


def user_aware_key_builder(
    func: Callable[..., Any],
    namespace: str = '',
    *,
    request: Request | None = None,
    response: Response | None = None,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Генерирует cache-ключ.

    Args:
        func (Callable[..., Any]): Декорируемая функция-обработчик (endpoint).
        namespace (str = ''): Пространство имен кэша (задается в декораторе @cache).
        request (Request | None): Объект HTTP-запроса FastAPI.
        response (Response | None): Объект HTTP-ответа FastAPI.
        args (tuple[Any, ...]): Позиционные аргументы, переданные в функцию.
        kwargs (dict[str, Any]): Именованные аргументы, переданные в функцию
            (включая зависимости user, session и query-параметры).

    Returns:
        str: Уникальный строковый ключ для хранения результата в кэше.

    """
    user = kwargs.get('user')
    show_active = kwargs.get('show_active')
    cafe_id = kwargs.get('cafe_id')
    prefix = FastAPICache.get_prefix()
    user_id = user.id if user else 'anon'
    return f'{prefix}:{namespace}:{func.__name__}:cafe_{cafe_id}:active_{show_active}:user_{user_id}'


@router.get(
    '/',
    summary='Получение списка блюд',
    response_model=list[DishInfo],
)
@cache(
    expire=DISHES_CACHE_SECONDS,
    namespace='get_all_dishes',
    key_builder=user_aware_key_builder,
)
async def get_all_dishes(
    user: UserDep,
    session: SessionDep,
    show_active: Annotated[
        bool,
        Query(
            description=(
                'Показывать все блюда, только активные или только не активные.\n\n'
                'По умолчанию показывает:\n\n'
                '- для пользователя - только активные блюда\n'
                '(всегда, в не зависимости от значения параметра).\n'
                '- для администратора - все блюда (и активные и не активные)\n'
                '- для менеджера - активные блюда\n'
            ),
        ),
    ] = None,
    cafe_id: Annotated[
        int | None,
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
        await check_object_exists(cafe_crud, cafe_id, session)
        conditions = [Dish.cafe_id == cafe_id]

    if (user.role, show_active) in only_active_variants:
        show_active = True
    elif (user.role, show_active) in all_dishes_variants:
        pass

    if show_active is not None:
        conditions.append(Dish.is_active.is_(show_active))
    return await dish_crud.get_multi(
        session,
        *conditions,
    )


@router.get(
    '/{dish_id}',
    summary='Получение информации о блюде по его ID',
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
    await check_object_exists(dish_crud, dish_id, session)

    conditions = [Dish.id == dish_id]
    if user.role == RoleEnum.USER:
        conditions.append(Dish.is_active.is_(True))
    return await dish_crud.get(dish_id, session, *conditions)


@router.post(
    '/',
    response_model=DishInfo,
    summary='Создание нового блюда',
    dependencies=[Depends(current_manager_without_cafe)],
)
async def create_dish(
    dish_schema: DishCreate,
    session: SessionDep,
) -> Dish:
    """Создает новое блюда. Только для администраторов и менеджеров."""
    if dish_schema.photo_id:
        MediaService.get_image_path(dish_schema.photo_id)
    created_dish = await dish_crud.create(
        dish_schema,
        session,
    )
    await FastAPICache.clear(namespace='get_all_dishes')
    return created_dish


@router.patch(
    '/{dish_id}',
    response_model=DishInfo,
    summary='Обновление информации о блюде по его ID',
    dependencies=[Depends(current_manager_without_cafe)],
)
async def update_dish(
    dish_id: Annotated[int, Path(description='ID блюда', gt=0)],
    session: SessionDep,
    obj_in: DishUpdate,
) -> Dish:
    """Обновление информации о блюде по его ID.

    Только для администраторов и менеджеров.
    """
    dish = await check_object_exists(dish_crud, dish_id, session)
    if obj_in.photo_id:
        MediaService.get_image_path(obj_in.photo_id)
    await FastAPICache.clear(namespace='get_all_dishes')
    return await dish_crud.update(
        dish,
        obj_in,
        session,
    )
