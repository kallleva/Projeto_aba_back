from . import db

class Profissional(db.Model):
    __tablename__ = 'profissionais'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

    # Relacionamentos
    planos_terapeuticos = db.relationship(
        'PlanoTerapeutico',
        back_populates='profissional',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    # Relacionamento many-to-many com pacientes
    vinculos_pacientes = db.relationship(
        'ProfissionalPaciente',
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
    
    def to_dict_com_pacientes(self):
        """Retorna dados do profissional incluindo pacientes vinculados"""
        return {
            'id': self.id,
            'nome': self.nome,
            'especialidade': self.especialidade,
            'email': self.email,
            'telefone': self.telefone,
            'pacientes_vinculados': [vinculo.to_dict_completo() for vinculo in self.vinculos_pacientes if vinculo.esta_ativo()],
            'total_pacientes_ativos': len([v for v in self.vinculos_pacientes if v.esta_ativo()])
        }
    
    def obter_pacientes_ativos(self):
        """Retorna lista de pacientes com vínculo ativo"""
        return [vinculo.paciente for vinculo in self.vinculos_pacientes if vinculo.esta_ativo()]
    
    def tem_vinculo_com_paciente(self, paciente_id):
        """Verifica se tem vínculo ativo com um paciente específico"""
        return any(v.paciente_id == paciente_id and v.esta_ativo() for v in self.vinculos_pacientes)
