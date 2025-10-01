from datetime import datetime, date, timedelta
from enum import Enum
from . import db

class StatusAgendamentoEnum(Enum):
    AGENDADO = "Agendado"
    CONFIRMADO = "Confirmado"
    CANCELADO = "Cancelado"
    REALIZADO = "Realizado"
    FALTOU = "Faltou"

class Agenda(db.Model):
    __tablename__ = 'agenda'

    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    duracao_minutos = db.Column(db.Integer, default=60, nullable=False)
    observacoes = db.Column(db.Text)
    status = db.Column(db.Enum(StatusAgendamentoEnum), default=StatusAgendamentoEnum.AGENDADO, nullable=False)
    presente = db.Column(db.Boolean, default=None, nullable=True)  # None = não informado, True = presente, False = ausente
    
    # Chaves estrangeiras
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissionais.id'), nullable=False)
    
    # Relacionamentos
    paciente = db.relationship('Paciente', backref='agendamentos')
    profissional = db.relationship('Profissional', backref='agendamentos')
    
    # Índices para melhor performance
    __table_args__ = (
        db.Index('idx_agenda_data_hora', 'data_hora'),
        db.Index('idx_agenda_paciente', 'paciente_id'),
        db.Index('idx_agenda_profissional', 'profissional_id'),
        db.Index('idx_agenda_status', 'status'),
    )

    def __repr__(self):
        return f'<Agenda {self.id}: {self.paciente.nome} - {self.data_hora}>'

    def to_dict(self):
        return {
            'id': self.id,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'duracao_minutos': self.duracao_minutos,
            'observacoes': self.observacoes,
            'status': self.status.value if self.status else None,
            'presente': self.presente,
            'paciente_id': self.paciente_id,
            'profissional_id': self.profissional_id,
            'paciente': {
                'id': self.paciente.id,
                'nome': self.paciente.nome
            } if self.paciente else None,
            'profissional': {
                'id': self.profissional.id,
                'nome': self.profissional.nome,
                'especialidade': self.profissional.especialidade
            } if self.profissional else None
        }

    @classmethod
    def get_agendamentos_por_mes(cls, ano, mes, profissional_id=None, paciente_id=None):
        """
        Retorna agendamentos de um mês específico
        """
        query = cls.query.filter(
            db.extract('year', cls.data_hora) == ano,
            db.extract('month', cls.data_hora) == mes
        )
        
        if profissional_id:
            query = query.filter(cls.profissional_id == profissional_id)
        
        if paciente_id:
            query = query.filter(cls.paciente_id == paciente_id)
            
        return query.order_by(cls.data_hora).all()

    @classmethod
    def get_agendamentos_por_dia(cls, data, profissional_id=None, paciente_id=None):
        """
        Retorna agendamentos de um dia específico
        """
        query = cls.query.filter(
            db.func.date(cls.data_hora) == data
        )
        
        if profissional_id:
            query = query.filter(cls.profissional_id == profissional_id)
        
        if paciente_id:
            query = query.filter(cls.paciente_id == paciente_id)
            
        return query.order_by(cls.data_hora).all()

    @classmethod
    def verificar_conflito_horario(cls, profissional_id, data_hora, duracao_minutos, agenda_id=None):
        """
        Verifica se há conflito de horário para o profissional
        """
        inicio = data_hora
        fim = data_hora + timedelta(minutes=duracao_minutos)
        
        # Buscar agendamentos do mesmo profissional
        agendamentos = cls.query.filter(
            cls.profissional_id == profissional_id,
            cls.id != agenda_id,
            cls.data_hora.isnot(None),
            cls.duracao_minutos.isnot(None)
        ).all()
        
        # Verificar conflitos manualmente
        for agenda in agendamentos:
            inicio_existente = agenda.data_hora
            fim_existente = agenda.data_hora + timedelta(minutes=agenda.duracao_minutos)
            
            # Verificar se há sobreposição
            if (inicio < fim_existente and fim > inicio_existente):
                return True
        
        return False
