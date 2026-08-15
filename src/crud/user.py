from src.crud.base import CRUDBase
from src.models import User


class CRUDUser(CRUDBase):
    """CRUD для модели User."""


user_crud = CRUDUser(User)
