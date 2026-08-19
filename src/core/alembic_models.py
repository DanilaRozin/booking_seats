from models import *  # noqa: F403
from models import __all__ as models_names

from core.base_model import Base

__all__ = [
    'Base',
    *models_names,
]
