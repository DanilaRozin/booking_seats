from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.validators import check_cafe_exists, check_name_duplicate
from src.core.db import get_session
from src.crud.cafe import cafe_crud
from src.schemas.cafe import CafeCreate, CafeInfo, CafeShortInfo, CafeUpdate

router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    '/',
    response_model=CafeInfo,
    response_model_exclude_none=True,
    # dependencies=
)
async def create_new_cafe(
    cafe: CafeCreate,
    session: SessionDep,
) -> object:
    """Создать кафе. Для менеджеров."""
    await check_name_duplicate(cafe.name, session)

    new_cafe = await cafe_crud.create(
        cafe,
        session,
    )
    return {
        'id': new_cafe.id,
        'name': new_cafe.name,
        'address': new_cafe.address,
        'phone': new_cafe.phone,
        'description': new_cafe.description,
        'photo_id': new_cafe.photo_id,
        'is_active': True,
        'created_at': new_cafe.created_at,
        'updated_at': new_cafe.updated_at,
        'managers': [],
    }
    # await session.refresh(new_cafe)
    # return new_cafe


@router.get(
    '/',
    response_model=list[CafeShortInfo],
    # response_model_exclude_none=True,
)
async def get_all_cafe(
    session: SessionDep,
) -> list[object]:
    """Получить список кафе."""
    return await cafe_crud.get_multi(session)


@router.patch(
    '/{cafe_id}',
    response_model=CafeInfo,
    response_model_exclude_none=True,
    # dependencies=
)
async def partial_update_cafe(
    cafe_id: int,
    obj_in: CafeUpdate,
    session: SessionDep,
) -> object:
    """Редактировать кафе."""
    db_cafe = await check_cafe_exists(
        cafe_id,
        session,
    )
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    db_cafe = await cafe_crud.update(
        db_cafe,
        obj_in,
        session,
    )
    await session.commit()
    await session.refresh(db_cafe)
    return {
        'id': db_cafe.id,
        'name': db_cafe.name,
        'address': db_cafe.address,
        'phone': db_cafe.phone,
        'description': db_cafe.description,
        'photo_id': db_cafe.photo_id,
        'is_active': True,
        'created_at': db_cafe.created_at,
        'updated_at': db_cafe.updated_at,
        'managers': [],
    }


# @router.delete(
#     '/{cafe_id}',
#     response_model=CafeInfo,
#     # dependencies=
# )
# async def remove_cafe(
#     cafe_id: int,
#     session: AsyncSession,
# ) -> None:
#     """Удалить кафе."""
#     db_cafe = await check_cafe_exists(
#         cafe_id,
#         session,
#     )
#     return await cafe_crud.remove(
#         db_cafe,
#         session,
#     )
