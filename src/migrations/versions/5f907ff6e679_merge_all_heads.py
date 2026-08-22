"""merge_all_heads

Revision ID: 5f907ff6e679
Revises: 8463ea70ee2e, 98ce460af7dd, dc4711241275
Create Date: 2026-08-22 07:49:47.734964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f907ff6e679'
down_revision: Union[str, Sequence[str], None] = ('8463ea70ee2e', '98ce460af7dd', 'dc4711241275')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
