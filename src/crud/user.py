from crud.base import CRUDBase
from models import User
from schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD для модели User."""


user_crud = CRUDUser(User)
