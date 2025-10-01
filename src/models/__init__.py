from flask_sqlalchemy import SQLAlchemy

# Instância única do SQLAlchemy
db = SQLAlchemy()

# Importar todos os modelos
from .paciente import Paciente, DiagnosticoEnum
from .profissional import Profissional
from .plano_terapeutico import PlanoTerapeutico
from .meta_terapeutica import MetaTerapeutica, StatusMetaEnum
from .checklist_diario import ChecklistDiario
from .usuario import Usuario, TipoUsuarioEnum
from .formulario import Formulario
from .pergunta import Pergunta, TipoPerguntaEnum
from .checklist_respostas import ChecklistResposta
from .checklist_diario import ChecklistDiario

# Exportar para facilitar importações
__all__ = [
    'db',
    'Paciente',
    'Profissional', 
    'PlanoTerapeutico',
    'MetaTerapeutica',
    'ChecklistDiario',
    'Usuario',
    'Formulario',     
    'Pergunta',  
    'ChecklistResposta',
    'ChecklistDiario',      # <--- adicione esta linha
    'DiagnosticoEnum',
    'StatusMetaEnum',
    'TipoUsuarioEnum',
    'TipoPerguntaEnum'
]

