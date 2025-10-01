"""Create agenda table

Revision ID: 6614ebe00428
Revises: 7318b0978428
Create Date: 2025-10-01 01:06:39.575631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6614ebe00428'
down_revision: Union[str, Sequence[str], None] = '7318b0978428'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Criar tabela agenda
    op.create_table('agenda',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data_hora', sa.DateTime(), nullable=False),
        sa.Column('duracao_minutos', sa.Integer(), nullable=False),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('AGENDADO', 'CONFIRMADO', 'CANCELADO', 'REALIZADO', 'FALTOU', name='statusagendamentoenum'), nullable=False),
        sa.Column('paciente_id', sa.Integer(), nullable=False),
        sa.Column('profissional_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ),
        sa.ForeignKeyConstraint(['profissional_id'], ['profissionais.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices
    op.create_index('idx_agenda_data_hora', 'agenda', ['data_hora'])
    op.create_index('idx_agenda_paciente', 'agenda', ['paciente_id'])
    op.create_index('idx_agenda_profissional', 'agenda', ['profissional_id'])
    op.create_index('idx_agenda_status', 'agenda', ['status'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remover índices
    op.drop_index('idx_agenda_status', table_name='agenda')
    op.drop_index('idx_agenda_profissional', table_name='agenda')
    op.drop_index('idx_agenda_paciente', table_name='agenda')
    op.drop_index('idx_agenda_data_hora', table_name='agenda')
    
    # Remover tabela agenda
    op.drop_table('agenda')
