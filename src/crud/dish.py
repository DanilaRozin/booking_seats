from crud.base import CRUDBase
from models import Dish


class CRUDDish(CRUDBase[Dish]):
    """Класс для CRUD-операций с ORM-моделью блюд."""


dish_crud = CRUDDish(Dish)
