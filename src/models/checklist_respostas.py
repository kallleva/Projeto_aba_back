from . import db

class ChecklistResposta(db.Model):
    __tablename__ = "checklist_respostas"

    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklists_diarios.id'), nullable=False)
    pergunta_id = db.Column(db.Integer, nullable=False)
    resposta = db.Column(db.Text, nullable=True)

    checklist = db.relationship('ChecklistDiario', back_populates='respostas')

    def to_dict(self):
        return {
            'id': self.id,
            'checklist_id': self.checklist_id,
            'pergunta_id': self.pergunta_id,
            'resposta': self.resposta
        }
