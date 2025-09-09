from enum import Enum
from . import db

# Enum padronizado com letras maiúsculas para coincidir com o banco
class TipoPerguntaEnum(Enum):
    TEXTO = "TEXTO"
    NUMERO = "NUMERO"
    BOOLEANO = "BOOLEANO"
    MULTIPLA = "MULTIPLA"

class Pergunta(db.Model):
    __tablename__ = "perguntas"

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.Enum(TipoPerguntaEnum, name="tipoperguntaenum"), nullable=False)
    obrigatoria = db.Column(db.Boolean, default=False)
    ordem = db.Column(db.Integer, nullable=False)
    formulario_id = db.Column(db.Integer, db.ForeignKey("formularios.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "texto": self.texto,
            "tipo": self.tipo.value,  # retorna string maiúscula
            "obrigatoria": self.obrigatoria,
            "ordem": self.ordem,
            "formulario_id": self.formulario_id
        }
