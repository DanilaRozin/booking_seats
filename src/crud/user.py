from crud.base import CRUDBase
from models import User


class CRUDUser(CRUDBase):
    """CRUD для модели User."""


user_crud = CRUDUser(User)
