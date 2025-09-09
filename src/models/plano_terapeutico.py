from datetime import date
from . import db

class PlanoTerapeutico(db.Model):
    __tablename__ = 'planos_terapeuticos'

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissionais.id'), nullable=False)
    objetivo_geral = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.Date, nullable=False, default=date.today)

    # Relacionamentos
    paciente = db.relationship(
        'Paciente',
        back_populates='planos_terapeuticos'
    )
    profissional = db.relationship(
        'Profissional',
        back_populates='planos_terapeuticos'
    )
    metas_terapeuticas = db.relationship(
        'MetaTerapeutica',
        back_populates='plano',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<PlanoTerapeutico {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'paciente_id': self.paciente_id,
            'profissional_id': self.profissional_id,
            'objetivo_geral': self.objetivo_geral,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'paciente_nome': self.paciente.nome if self.paciente else None,
            'profissional_nome': self.profissional.nome if self.profissional else None
        }
