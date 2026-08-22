from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_users import exceptions

from api import SessionDep
from api.validators import existing_user
from crud.user import user_crud
from models import User
from schemas.user import UserAdminUpdate, UserCreate, UserInfo, UserUpdate

from core.user import UserManager, current_manager, current_user, ensure_can_deactivate, get_user_manager

router = APIRouter()


# Регистрация пользователя
@router.post(
    '',
    response_model=UserInfo,
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация пользователя',
)
async def register(
    user_create: UserCreate,
    request: Request,
    user_manager: UserManager = Depends(get_user_manager),
) -> User:
    """Регистрация пользователя.

    - **username**: юзернейм пользователя
    - **email**: адрес электронной почты
    - **phone**: номер телефона
    - **tg_id**: Telegram ID (опционально)
    - **password**: пароль
    """
    await existing_user(user_create, user_manager)
    try:
        user = await user_manager.create(user_create, safe=True, request=request)
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='REGISTER_USER_ALREADY_EXISTS',
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={'code': 'REGISTER_INVALID_PASSWORD', 'reason': e.reason},
        )
    return user


@router.get(
    '',
    response_model=list[UserInfo],
    response_model_exclude_none=True,
    dependencies=[Depends(current_manager)],
    summary='Посмотреть список всех пользователей',
)
async def get_list_user_info(
    session: SessionDep,
) -> Sequence[User]:
    """Возращает список состоящий из всех пользователей."""
    return await user_crud.get_multi(session)


@router.get(
    '/me',
    response_model=UserInfo,
    response_model_exclude_none=True,
    summary='Посмотреть информацию о себе',
)
async def get_me_info(
    session: SessionDep,
    user: Annotated[User, Depends(current_user)],
) -> User:
    """Возращает информацию о пользователе."""
    return await user_crud.get(obj_id=user.id, session=session)


@router.patch(
    '/me',
    response_model=UserInfo,
    response_model_exclude_none=True,
)
async def update_me_info(
    obj_in: UserUpdate,
    user: Annotated[User, Depends(current_user)],
    user_manager: UserManager = Depends(get_user_manager),
    request: Request = None,
) -> User:
    """Обновляет данные текущего пользователя."""
    return await user_manager.update(obj_in, user, safe=True, request=request)


@router.get(
    '/{user_id}',
    response_model=UserInfo,
    response_model_exclude_none=True,
    dependencies=[Depends(current_manager)],
)
async def get_user_info_by_id(
    session: SessionDep,
    user_id: int,
) -> User:
    """Возвращает данные пользователя по id (для менеджеров и админов)."""
    return await user_crud.get(obj_id=user_id, session=session)


@router.patch(
    '/{user_id}',
    response_model=UserInfo,
    response_model_exclude_none=True,
)
async def update_user_info(
    obj_in: UserAdminUpdate,
    user_id: int,
    request: Request,
    user: User = Depends(current_manager),
    user_manager: UserManager = Depends(get_user_manager),
) -> User:
    """Обновляет данные пользователя по id (для менеджеров и админов)."""
    ensure_can_deactivate(obj_in, user)
    user_obj = await user_manager.get(user_id)
    return await user_manager.update(obj_in, user_obj, request=request)
