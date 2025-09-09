from datetime import date
from . import db
from .meta_terapeutica import MetaTerapeutica

class ChecklistDiario(db.Model):
    __tablename__ = 'checklists_diarios'

    id = db.Column(db.Integer, primary_key=True)
    meta_id = db.Column(db.Integer, db.ForeignKey('metas_terapeuticas.id'), nullable=False)
    data = db.Column(db.Date, nullable=False, default=date.today)
    
    # 🔹 Agora a nota não é mais obrigatória
    nota = db.Column(db.Integer, nullable=True)  # Opcional (1 a 5)
    
    observacao = db.Column(db.Text, nullable=True)

    # Relacionamento com meta
    meta = db.relationship(
        'MetaTerapeutica',
        back_populates='checklists_diarios'
    )

    # Respostas vinculadas
    respostas = db.relationship(
        'ChecklistResposta',
        back_populates='checklist',
        cascade='all, delete-orphan',
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint('nota >= 1 AND nota <= 5', name='check_nota_range'),
        db.UniqueConstraint('meta_id', 'data', name='unique_meta_data')
    )

    def __repr__(self):
        return f'<ChecklistDiario {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'meta_id': self.meta_id,
            'data': self.data.isoformat() if self.data else None,
            'nota': self.nota,
            'observacao': self.observacao,
            'meta_descricao': self.meta.descricao if self.meta else None,
            'respostas': [r.to_dict() for r in self.respostas]
        }

    @staticmethod
    def validar_nota(nota):
        return isinstance(nota, int) and 1 <= nota <= 5
