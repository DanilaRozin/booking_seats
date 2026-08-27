"""update cafe

Revision ID: 77829ad9504d
Revises: 29fbf1bcb8ab, 8ae1e05a39d1
Create Date: 2026-08-27 17:43:43.909322

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77829ad9504d'
down_revision: Union[str, Sequence[str], None] = ('29fbf1bcb8ab', '8ae1e05a39d1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
