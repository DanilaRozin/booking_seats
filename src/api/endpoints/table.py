from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from api import SessionDep, UserDep
from api.validators import check_cafe_exists, check_table_exists
from crud import cafe_crud, table_crud
from models import Table
from schemas.table import TableCreate, TableInfo, TableUpdate

from core.constants import RoleEnum
from core.user import current_manager

router = APIRouter()

# TODO: Добавить валидацию.


@router.get(
    '/',
    summary='Список столов в кафе',
    response_model=list[TableInfo],
)
async def get_all_tables(
    cafe_id: Annotated[int, Path(description='ID кафе', gt=0)],
    user: UserDep,
    session: SessionDep,
    show_active: Annotated[
        bool | None,
        Query(
            description=('Показывать все столы в кафе, только активные или только не активные.'),
        ),
    ] = None,
) -> list[Table]:
    """Получение списка доступных для бронирования столов в кафе.

    Для администраторов и менеджеров - все столы (с возможностью выбора), для
    пользователей - только активные.

    По умолчанию показывает:
    - для администратора - все столы в кафе
    - для менеджера - активные столы в кафе

    """
    await check_cafe_exists(cafe_id, session)
    if user.role == RoleEnum.MANAGER and show_active is None or user.role == RoleEnum.USER:
        show_active = True
    conditions = [Table.cafe_id == cafe_id]
    if show_active is not None:
        conditions.append(Table.is_active.is_(show_active))

    return await table_crud.get_multi(
        session,
        *conditions,
    )


@router.get(
    '/{table_id}',
    summary='Информация о столе в кафе по его ID',
    response_model=TableInfo,
)
async def get_table(
    cafe_id: Annotated[int, Path(description='ID кафе', gt=0)],
    table_id: Annotated[int, Path(description='ID стола', gt=0)],
    user: UserDep,
    session: SessionDep,
) -> Table | None:
    """Получение информации о столе в кафе по его ID.

    Для администраторов и менеджеров - все столы, для пользователей - только
    активные.

    """
    conditions = [Table.cafe_id == cafe_id]
    if user.role == RoleEnum.USER:
        conditions.append(Table.is_active.is_(True))
    return await table_crud.get(table_id, session, *conditions)


@router.post(
    '/',
    response_model=TableInfo,
    summary='Новый стол в кафе',
    dependencies=[Depends(current_manager)],
)
async def create_table(
    cafe_id: Annotated[int, Path(description='ID кафе', gt=0)],
    table_schema: TableCreate,
    session: SessionDep,
) -> Table:
    """Создает новое стола кафе.

    Только для администраторов и менеджеров.

    """
    await check_cafe_exists(cafe_id, session)
    table_number = cafe_crud.get_new_table_number(cafe_id, session)

    return await table_crud.create(
        table_schema,
        session,
        id=table_number,
    )


@router.patch(
    '/{table_id}',
    response_model=TableInfo,
    summary='Обновление информации о столе в кафе по его ID',
    dependencies=[Depends(current_manager)],
)
async def update_table(
    cafe_id: Annotated[int, Path(description='ID кафе', gt=0)],
    table_id: Annotated[int, Path(description='ID стола', gt=0)],
    obj_in: TableUpdate,
    session: SessionDep,
) -> Table:
    """Обновление информации о столе в кафе по его ID.

    Только для администраторов и менеджеров.

    """
    table = await check_table_exists(cafe_id, table_id, session)

    return await table_crud.update(
        table,
        obj_in,
        session,
    )
