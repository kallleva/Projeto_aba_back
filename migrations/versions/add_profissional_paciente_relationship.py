"""add_profissional_paciente_relationship

Revision ID: prof_pac_001
Revises: bf1b1840fd38
Create Date: 2024-10-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'prof_pac_001'
down_revision = 'bf1b1840fd38'
branch_labels = None
depends_on = None

def upgrade():
    # Criar enum para status do vínculo
    status_vinculo_enum = postgresql.ENUM('ATIVO', 'INATIVO', 'SUSPENSO', name='statusvinculoenum')
    status_vinculo_enum.create(op.get_bind())
    
    # Criar enum para tipo de atendimento
    tipo_atendimento_enum = postgresql.ENUM(
        'Terapia ABA', 'Psicologia', 'Fonoaudiologia', 
        'Terapia Ocupacional', 'Fisioterapia', 'Psicopedagogia', 'Outro', 
        name='tipoatendimentoenum'
    )
    tipo_atendimento_enum.create(op.get_bind())
    
    # Criar tabela profissional_paciente
    op.create_table('profissional_paciente',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('profissional_id', sa.Integer(), nullable=False),
        sa.Column('paciente_id', sa.Integer(), nullable=False),
        sa.Column('data_inicio', sa.Date(), nullable=False),
        sa.Column('data_fim', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('ATIVO', 'INATIVO', 'SUSPENSO', name='statusvinculoenum'), nullable=False),
        sa.Column('tipo_atendimento', sa.Enum('Terapia ABA', 'Psicologia', 'Fonoaudiologia', 'Terapia Ocupacional', 'Fisioterapia', 'Psicopedagogia', 'Outro', name='tipoatendimentoenum'), nullable=False),
        sa.Column('frequencia_semanal', sa.Integer(), nullable=True),
        sa.Column('duracao_sessao', sa.Integer(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('data_criacao', sa.Date(), nullable=False),
        sa.Column('criado_por', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['criado_por'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ),
        sa.ForeignKeyConstraint(['profissional_id'], ['profissionais.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('profissional_id', 'paciente_id', 'tipo_atendimento', name='unique_profissional_paciente_tipo')
    )

def downgrade():
    # Remover tabela
    op.drop_table('profissional_paciente')
    
    # Remover enums
    op.execute('DROP TYPE IF EXISTS statusvinculoenum')
    op.execute('DROP TYPE IF EXISTS tipoatendimentoenum')
