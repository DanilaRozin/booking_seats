from crud.base import CRUDBase
from models.slots import Slot


class SlotCRUD(CRUDBase):
    """CRUD методы для временных слотов."""


slot_crud = SlotCRUD(Slot)
