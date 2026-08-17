from crud.base import CRUDBase
from models import Table


class CRUDCTable(CRUDBase[Table]):
    """Класс для CRUD-операций c ORM-моделью cтолов."""


table_crud = CRUDCTable(Table)
