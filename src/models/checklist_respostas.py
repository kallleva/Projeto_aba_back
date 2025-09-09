from . import db
from .pergunta import Pergunta

class ChecklistResposta(db.Model):
    __tablename__ = 'checklist_respostas'

    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklists_diarios.id'), nullable=False)
    pergunta_id = db.Column(db.Integer, db.ForeignKey('perguntas.id'), nullable=False)
    resposta = db.Column(db.Text, nullable=True)

    checklist = db.relationship('ChecklistDiario', back_populates='respostas')
    pergunta = db.relationship('Pergunta')

    __table_args__ = (
        db.UniqueConstraint('checklist_id', 'pergunta_id', name='unique_resposta_pergunta'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'pergunta_id': self.pergunta_id,
            'pergunta_texto': self.pergunta.texto if self.pergunta else None,
            'resposta': self.resposta
        }
