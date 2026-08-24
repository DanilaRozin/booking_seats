from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User

from core.db import get_session
from core.user import current_user

SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[User, Depends(current_user)]
