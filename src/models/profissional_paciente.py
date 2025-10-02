from datetime import date
from enum import Enum
from . import db

class StatusVinculoEnum(Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    SUSPENSO = "SUSPENSO"

class TipoAtendimentoEnum(Enum):
    TERAPIA_ABA = "Terapia ABA"
    PSICOLOGIA = "Psicologia"
    FONOAUDIOLOGIA = "Fonoaudiologia"
    TERAPIA_OCUPACIONAL = "Terapia Ocupacional"
    FISIOTERAPIA = "Fisioterapia"
    PSICOPEDAGOGIA = "Psicopedagogia"
    OUTRO = "Outro"

class ProfissionalPaciente(db.Model):
    """
    Tabela de relacionamento many-to-many entre Profissional e Paciente
    Permite que um profissional atenda múltiplos pacientes
    e um paciente seja atendido por múltiplos profissionais
    """
    __tablename__ = 'profissional_paciente'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Chaves estrangeiras
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissionais.id'), nullable=False)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    
    # Informações do vínculo
    data_inicio = db.Column(db.Date, nullable=False, default=date.today)
    data_fim = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum(StatusVinculoEnum), nullable=False, default=StatusVinculoEnum.ATIVO)
    tipo_atendimento = db.Column(db.Enum(TipoAtendimentoEnum), nullable=False)
    
    # Configurações do atendimento
    frequencia_semanal = db.Column(db.Integer, nullable=True, comment="Número de sessões por semana")
    duracao_sessao = db.Column(db.Integer, nullable=True, comment="Duração da sessão em minutos")
    observacoes = db.Column(db.Text, nullable=True)
    
    # Dados de controle
    data_criacao = db.Column(db.Date, nullable=False, default=date.today)
    criado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    # Relacionamentos
    profissional = db.relationship('Profissional', back_populates='vinculos_pacientes')
    paciente = db.relationship('Paciente', back_populates='vinculos_profissionais')
    usuario_criador = db.relationship('Usuario', foreign_keys=[criado_por])
    
    # Constraint para evitar duplicatas
    __table_args__ = (
        db.UniqueConstraint('profissional_id', 'paciente_id', 'tipo_atendimento', 
                          name='unique_profissional_paciente_tipo'),
    )
    
    def __repr__(self):
        return f'<ProfissionalPaciente {self.profissional_id}-{self.paciente_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'profissional_id': self.profissional_id,
            'paciente_id': self.paciente_id,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'status': self.status.value if self.status else None,
            'tipo_atendimento': self.tipo_atendimento.value if self.tipo_atendimento else None,
            'frequencia_semanal': self.frequencia_semanal,
            'duracao_sessao': self.duracao_sessao,
            'observacoes': self.observacoes,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'criado_por': self.criado_por
        }
    
    def to_dict_completo(self):
        """Retorna dados completos incluindo informações do profissional e paciente"""
        return {
            'id': self.id,
            'profissional': self.profissional.to_dict() if self.profissional else None,
            'paciente': self.paciente.to_dict() if self.paciente else None,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'status': self.status.value if self.status else None,
            'tipo_atendimento': self.tipo_atendimento.value if self.tipo_atendimento else None,
            'frequencia_semanal': self.frequencia_semanal,
            'duracao_sessao': self.duracao_sessao,
            'observacoes': self.observacoes,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'criado_por': self.criado_por
        }
    
    def ativar(self):
        """Ativa o vínculo"""
        self.status = StatusVinculoEnum.ATIVO
        self.data_fim = None
    
    def inativar(self, data_fim=None):
        """Inativa o vínculo"""
        self.status = StatusVinculoEnum.INATIVO
        self.data_fim = data_fim or date.today()
    
    def suspender(self):
        """Suspende temporariamente o vínculo"""
        self.status = StatusVinculoEnum.SUSPENSO
    
    def esta_ativo(self):
        """Verifica se o vínculo está ativo"""
        return self.status == StatusVinculoEnum.ATIVO
    
    def calcular_duracao_vinculo(self):
        """Calcula a duração do vínculo em dias"""
        data_fim = self.data_fim or date.today()
        return (data_fim - self.data_inicio).days if self.data_inicio else 0
