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
    planos_terapeuticos = db.relationship('PlanoTerapeutico', backref='paciente_ref', lazy=True, cascade='all, delete-orphan')
    
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
        """Calcula a idade do paciente em anos"""
        if self.data_nascimento:
            hoje = date.today()
            return hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return None

