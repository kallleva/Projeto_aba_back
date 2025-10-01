"""Add presente field to agenda

Revision ID: bf1b1840fd38
Revises: 6614ebe00428
Create Date: 2025-10-01 01:15:55.293360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf1b1840fd38'
down_revision: Union[str, Sequence[str], None] = '6614ebe00428'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Adicionar campo presente à tabela agenda
    op.add_column('agenda', sa.Column('presente', sa.Boolean(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remover campo presente da tabela agenda
    op.drop_column('agenda', 'presente')
