from datetime import datetime
from . import db
from .meta_terapeutica import meta_formulario

class Formulario(db.Model):
    __tablename__ = "formularios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(400))
    categoria = db.Column(db.String(50), nullable=False, default="avaliacao")
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    perguntas = db.relationship("Pergunta", backref="formulario", cascade="all, delete-orphan")

    # Relacionamento Many-to-Many com MetaTerapeutica
    metas = db.relationship(
        "MetaTerapeutica",
        secondary=meta_formulario,
        back_populates="formularios",
        lazy="subquery"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "categoria": self.categoria,
            "criadoEm": self.criado_em.isoformat() if self.criado_em else None,
            "atualizadoEm": self.atualizado_em.isoformat() if self.atualizado_em else None,
            "perguntas": [p.to_dict() for p in self.perguntas]
        }
