from crud.base import CRUDBase
from models import Dish
from schemas.dish import DishCreate, DishUpdate


class CRUDDish(CRUDBase[Dish, DishCreate, DishUpdate]):
    """Класс для CRUD-операций с ORM-моделью блюд."""


dish_crud = CRUDDish(Dish)
