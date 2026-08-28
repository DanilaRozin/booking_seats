from crud.base import CRUDBase
from models.slots import Slot
from schemas.slots import CreateTimeSlot, UpdateTimeSlot


class SlotCRUD(CRUDBase[Slot, CreateTimeSlot, UpdateTimeSlot]):
    """CRUD методы для временных слотов."""


slot_crud = SlotCRUD(Slot)
