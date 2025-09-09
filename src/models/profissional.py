from . import db

class Profissional(db.Model):
    __tablename__ = 'profissionais'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

    # Relacionamento
    planos_terapeuticos = db.relationship(
        'PlanoTerapeutico',
        back_populates='profissional',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Profissional {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'especialidade': self.especialidade,
            'email': self.email,
            'telefone': self.telefone
        }
