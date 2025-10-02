from datetime import date
from enum import Enum
from . import db

class DiagnosticoEnum(Enum):
    TEA = "TEA"
    TDAH = "TDAH"
    OUTRO = "Outro"

class Paciente(db.Model):
    __tablename__ = 'pacientes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    responsavel = db.Column(db.String(100), nullable=False)
    contato = db.Column(db.String(50), nullable=False)
    diagnostico = db.Column(db.Enum(DiagnosticoEnum), nullable=False)

    # Relacionamentos
    planos_terapeuticos = db.relationship(
        'PlanoTerapeutico',
        back_populates='paciente',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    # Relacionamento many-to-many com profissionais
    vinculos_profissionais = db.relationship(
        'ProfissionalPaciente',
        back_populates='paciente',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Paciente {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'responsavel': self.responsavel,
            'contato': self.contato,
            'diagnostico': self.diagnostico.value if self.diagnostico else None
        }

    def calcular_idade(self):
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
    
    def to_dict_com_profissionais(self):
        """Retorna dados do paciente incluindo profissionais vinculados"""
        return {
            'id': self.id,
            'nome': self.nome,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'idade': self.calcular_idade(),
            'responsavel': self.responsavel,
            'contato': self.contato,
            'diagnostico': self.diagnostico.value if self.diagnostico else None,
            'profissionais_vinculados': [vinculo.to_dict_completo() for vinculo in self.vinculos_profissionais if vinculo.esta_ativo()],
            'total_profissionais_ativos': len([v for v in self.vinculos_profissionais if v.esta_ativo()])
        }
    
    def obter_profissionais_ativos(self):
        """Retorna lista de profissionais com vínculo ativo"""
        return [vinculo.profissional for vinculo in self.vinculos_profissionais if vinculo.esta_ativo()]
    
    def tem_vinculo_com_profissional(self, profissional_id):
        """Verifica se tem vínculo ativo com um profissional específico"""
        return any(v.profissional_id == profissional_id and v.esta_ativo() for v in self.vinculos_profissionais)
    
    def obter_tipos_atendimento(self):
        """Retorna lista de tipos de atendimento ativos"""
        return [v.tipo_atendimento.value for v in self.vinculos_profissionais if v.esta_ativo()]
