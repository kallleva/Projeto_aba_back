from datetime import date
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class TipoUsuarioEnum(Enum):
    PROFISSIONAL = "Profissional"
    RESPONSAVEL = "Responsavel"

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    tipo_usuario = db.Column(db.Enum(TipoUsuarioEnum), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(db.Date, nullable=False, default=date.today)
    
    # Relacionamentos específicos por tipo
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissionais.id'), nullable=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=True)  # Para responsáveis
    
    # Relacionamentos
    profissional = db.relationship('Profissional', backref='usuario', uselist=False)
    paciente = db.relationship('Paciente', backref='responsavel_usuario', uselist=False)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'
    
    def set_senha(self, senha):
        """Define a senha do usuário (com hash)"""
        self.senha_hash = generate_password_hash(senha)
    
    def verificar_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'nome': self.nome,
            'tipo_usuario': self.tipo_usuario.value if self.tipo_usuario else None,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'profissional_id': self.profissional_id,
            'paciente_id': self.paciente_id
        }
    
    def pode_acessar_paciente(self, paciente_id):
        """Verifica se o usuário pode acessar dados de um paciente específico"""
        if self.tipo_usuario == TipoUsuarioEnum.PROFISSIONAL:
            # Profissionais podem acessar pacientes que atendem
            return True  # Por simplicidade, profissionais podem ver todos os pacientes
        elif self.tipo_usuario == TipoUsuarioEnum.RESPONSAVEL:
            # Responsáveis só podem acessar dados do próprio filho
            return self.paciente_id == paciente_id
        return False
    
    def pode_editar_dados(self):
        """Verifica se o usuário pode editar dados do sistema"""
        return self.tipo_usuario == TipoUsuarioEnum.PROFISSIONAL
    
    def pode_criar_planos(self):
        """Verifica se o usuário pode criar planos terapêuticos"""
        return self.tipo_usuario == TipoUsuarioEnum.PROFISSIONAL
    
    def pode_registrar_progresso(self):
        """Verifica se o usuário pode registrar progresso diário"""
        return self.tipo_usuario == TipoUsuarioEnum.PROFISSIONAL

