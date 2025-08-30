from datetime import date
from . import db

class ChecklistDiario(db.Model):
    __tablename__ = 'checklists_diarios'
    
    id = db.Column(db.Integer, primary_key=True)
    meta_id = db.Column(db.Integer, db.ForeignKey('metas_terapeuticas.id'), nullable=False)
    data = db.Column(db.Date, nullable=False, default=date.today)
    nota = db.Column(db.Integer, nullable=False)  # 1 a 5
    observacao = db.Column(db.Text, nullable=True)
    
    # Relacionamentos
    meta = db.relationship('MetaTerapeutica', backref='checklists')
    
    # Constraint para garantir que a nota esteja entre 1 e 5
    __table_args__ = (
        db.CheckConstraint('nota >= 1 AND nota <= 5', name='check_nota_range'),
        db.UniqueConstraint('meta_id', 'data', name='unique_meta_data'),  # Uma entrada por meta por dia
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
            'meta_descricao': self.meta.descricao if self.meta else None
        }
    
    @staticmethod
    def validar_nota(nota):
        """Valida se a nota está no intervalo correto"""
        return isinstance(nota, int) and 1 <= nota <= 5

