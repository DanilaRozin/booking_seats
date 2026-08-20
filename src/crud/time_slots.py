from src.crud.base import CRUDBase
from src.models.time_slots import Slot


class SlotCRUD(CRUDBase):
    """CRUD методы для временных слотов."""


slot_crud = SlotCRUD(Slot)
