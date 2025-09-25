from datetime import date
from enum import Enum
from . import db

# Tabela de associação Many-to-Many entre MetaTerapeutica e Formulario
meta_formulario = db.Table(
    "meta_formulario",
    db.Column("meta_id", db.Integer, db.ForeignKey("metas_terapeuticas.id"), primary_key=True),
    db.Column("formulario_id", db.Integer, db.ForeignKey("formularios.id"), primary_key=True)
)

class StatusMetaEnum(Enum):
    EM_ANDAMENTO = "EmAndamento"
    CONCLUIDA = "Concluida"

class MetaTerapeutica(db.Model):
    __tablename__ = 'metas_terapeuticas'

    id = db.Column(db.Integer, primary_key=True)
    plano_id = db.Column(db.Integer, db.ForeignKey('planos_terapeuticos.id'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_previsao_termino = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(StatusMetaEnum), nullable=False, default=StatusMetaEnum.EM_ANDAMENTO)

    # Relacionamento com plano
    plano = db.relationship('PlanoTerapeutico', back_populates='metas_terapeuticas')

    # Relacionamento com checklist diário
    checklists_diarios = db.relationship('ChecklistDiario', back_populates='meta', cascade='all, delete-orphan')

    # Relacionamento Many-to-Many com Formulario
    formularios = db.relationship(
        "Formulario",
        secondary=meta_formulario,
        back_populates="metas",
        lazy="subquery"
    )

    def to_dict(self):
        return {
            'id': self.id,
            'plano_id': self.plano_id,
            'descricao': self.descricao,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_previsao_termino': self.data_previsao_termino.isoformat() if self.data_previsao_termino else None,
            'status': self.status.value if self.status else None,
            'formularios': [f.to_dict() for f in self.formularios]
        }

    def calcular_progresso(self):
        if not self.data_inicio or not self.data_previsao_termino:
            return 0
        hoje = date.today()
        total_dias = (self.data_previsao_termino - self.data_inicio).days
        dias_decorridos = (hoje - self.data_inicio).days
        if total_dias <= 0:
            return 100
        progresso = min(100, max(0, (dias_decorridos / total_dias) * 100))
        return round(progresso, 2)
