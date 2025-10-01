import logging
from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models import db, Agenda, Paciente, Profissional, StatusAgendamentoEnum

# Configurar logger
logger = logging.getLogger('agenda_logger')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

agenda_bp = Blueprint('agenda', __name__)

# --- LISTAR TODOS ---
@agenda_bp.route('/agenda', methods=['GET'])
def listar_agendamentos():
    """
    Lista todos os agendamentos
    ---
    tags:
      - Agenda
    parameters:
      - name: profissional_id
        in: query
        type: integer
        description: Filtrar por profissional
      - name: paciente_id
        in: query
        type: integer
        description: Filtrar por paciente
      - name: status
        in: query
        type: string
        description: Filtrar por status
      - name: data_inicio
        in: query
        type: string
        format: date
        description: Data de início (YYYY-MM-DD)
      - name: data_fim
        in: query
        type: string
        format: date
        description: Data de fim (YYYY-MM-DD)
    responses:
      200:
        description: Lista de agendamentos
    """
    try:
        query = Agenda.query
        
        # Filtros opcionais
        profissional_id = request.args.get('profissional_id', type=int)
        paciente_id = request.args.get('paciente_id', type=int)
        status = request.args.get('status')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if profissional_id:
            query = query.filter(Agenda.profissional_id == profissional_id)
        
        if paciente_id:
            query = query.filter(Agenda.paciente_id == paciente_id)
        
        if status:
            try:
                status_enum = StatusAgendamentoEnum(status)
                query = query.filter(Agenda.status == status_enum)
            except ValueError:
                return jsonify({'erro': 'Status inválido'}), 400
        
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
                query = query.filter(Agenda.data_hora >= data_inicio_dt)
            except ValueError:
                return jsonify({'erro': 'Formato de data_inicio inválido. Use YYYY-MM-DD'}), 400
        
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
                # Adiciona 23:59:59 para incluir o dia inteiro
                data_fim_dt = data_fim_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(Agenda.data_hora <= data_fim_dt)
            except ValueError:
                return jsonify({'erro': 'Formato de data_fim inválido. Use YYYY-MM-DD'}), 400
        
        agendamentos = query.order_by(Agenda.data_hora).all()
        logger.info(f"Listando {len(agendamentos)} agendamentos")
        
        return jsonify([agenda.to_dict() for agenda in agendamentos]), 200
        
    except Exception as e:
        logger.exception("Erro ao listar agendamentos")
        return jsonify({'erro': str(e)}), 500

# --- OBTER POR ID ---
@agenda_bp.route('/agenda/<int:agenda_id>', methods=['GET'])
def obter_agendamento(agenda_id):
    """
    Obtém um agendamento específico
    ---
    tags:
      - Agenda
    parameters:
      - name: agenda_id
        in: path
        type: integer
        required: true
        description: ID do agendamento
    responses:
      200:
        description: Agendamento encontrado
      404:
        description: Agendamento não encontrado
    """
    try:
        agenda = Agenda.query.get_or_404(agenda_id)
        logger.info(f"Agendamento obtido: ID {agenda.id}")
        return jsonify(agenda.to_dict()), 200
    except Exception as e:
        logger.exception(f"Erro ao obter agendamento ID {agenda_id}")
        return jsonify({'erro': str(e)}), 500

# --- CRIAR ---
@agenda_bp.route('/agenda', methods=['POST'])
def criar_agendamento():
    """
    Cria um novo agendamento
    ---
    tags:
      - Agenda
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - data_hora
            - paciente_id
            - profissional_id
          properties:
            data_hora:
              type: string
              format: date-time
            duracao_minutos:
              type: integer
              default: 60
            observacoes:
              type: string
            status:
              type: string
              enum: [Agendado, Confirmado, Cancelado, Realizado, Faltou]
              default: Agendado
            paciente_id:
              type: integer
            profissional_id:
              type: integer
    responses:
      201:
        description: Agendamento criado com sucesso
      400:
        description: Erro de validação
    """
    try:
        dados = request.get_json()
        logger.debug(f"Dados recebidos para criar agendamento: {dados}")

        # Validações obrigatórias
        for campo in ['data_hora', 'paciente_id', 'profissional_id']:
            if not dados.get(campo):
                logger.warning(f"Campo obrigatório ausente: {campo}")
                return jsonify({'erro': f'{campo} é obrigatório'}), 400

        # Validar se paciente existe
        paciente = Paciente.query.get(dados['paciente_id'])
        if not paciente:
            return jsonify({'erro': 'Paciente não encontrado'}), 400

        # Validar se profissional existe
        profissional = Profissional.query.get(dados['profissional_id'])
        if not profissional:
            return jsonify({'erro': 'Profissional não encontrado'}), 400

        # Converter data_hora
        try:
            data_hora = datetime.fromisoformat(dados['data_hora'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'erro': 'Formato de data_hora inválido. Use ISO format'}), 400

        # Validar duração
        duracao_minutos = dados.get('duracao_minutos', 60)
        if duracao_minutos <= 0:
            return jsonify({'erro': 'Duração deve ser maior que zero'}), 400

        # Verificar conflito de horário
        if Agenda.verificar_conflito_horario(
            dados['profissional_id'], 
            data_hora, 
            duracao_minutos
        ):
            return jsonify({'erro': 'Conflito de horário com outro agendamento'}), 400

        # Validar status
        status = StatusAgendamentoEnum.AGENDADO
        if 'status' in dados:
            try:
                # Mapear valores em maiúsculo para os valores corretos do enum
                status_map = {
                    'AGENDADO': 'Agendado',
                    'CONFIRMADO': 'Confirmado', 
                    'CANCELADO': 'Cancelado',
                    'REALIZADO': 'Realizado',
                    'FALTOU': 'Faltou'
                }
                status_value = status_map.get(dados['status'], dados['status'])
                status = StatusAgendamentoEnum(status_value)
            except ValueError:
                return jsonify({'erro': 'Status inválido. Valores aceitos: AGENDADO, CONFIRMADO, CANCELADO, REALIZADO, FALTOU'}), 400

        # Criar agendamento
        agenda = Agenda(
            data_hora=data_hora,
            duracao_minutos=duracao_minutos,
            observacoes=dados.get('observacoes'),
            status=status,
            presente=dados.get('presente'),  # None por padrão
            paciente_id=dados['paciente_id'],
            profissional_id=dados['profissional_id']
        )

        db.session.add(agenda)
        db.session.commit()

        logger.info(f"Agendamento criado: ID {agenda.id}")
        return jsonify(agenda.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.exception("Erro ao criar agendamento")
        return jsonify({'erro': str(e)}), 500

# --- ATUALIZAR ---
@agenda_bp.route('/agenda/<int:agenda_id>', methods=['PUT'])
def atualizar_agendamento(agenda_id):
    """
    Atualiza um agendamento existente
    ---
    tags:
      - Agenda
    parameters:
      - name: agenda_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            data_hora:
              type: string
              format: date-time
            duracao_minutos:
              type: integer
            observacoes:
              type: string
            status:
              type: string
              enum: [Agendado, Confirmado, Cancelado, Realizado, Faltou]
            paciente_id:
              type: integer
            profissional_id:
              type: integer
    responses:
      200:
        description: Agendamento atualizado
      400:
        description: Erro de validação
      404:
        description: Agendamento não encontrado
    """
    try:
        agenda = Agenda.query.get_or_404(agenda_id)
        dados = request.get_json()
        logger.debug(f"Atualizando agendamento ID {agenda_id} com dados: {dados}")

        # Atualizar campos
        if 'data_hora' in dados:
            try:
                agenda.data_hora = datetime.fromisoformat(dados['data_hora'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'erro': 'Formato de data_hora inválido. Use ISO format'}), 400

        if 'duracao_minutos' in dados:
            if dados['duracao_minutos'] <= 0:
                return jsonify({'erro': 'Duração deve ser maior que zero'}), 400
            agenda.duracao_minutos = dados['duracao_minutos']

        if 'observacoes' in dados:
            agenda.observacoes = dados['observacoes']

        if 'status' in dados:
            try:
                # Mapear valores em maiúsculo para os valores corretos do enum
                status_map = {
                    'AGENDADO': 'Agendado',
                    'CONFIRMADO': 'Confirmado', 
                    'CANCELADO': 'Cancelado',
                    'REALIZADO': 'Realizado',
                    'FALTOU': 'Faltou'
                }
                status_value = status_map.get(dados['status'], dados['status'])
                agenda.status = StatusAgendamentoEnum(status_value)
            except ValueError:
                return jsonify({'erro': 'Status inválido. Valores aceitos: AGENDADO, CONFIRMADO, CANCELADO, REALIZADO, FALTOU'}), 400

        if 'presente' in dados:
            agenda.presente = dados['presente']

        if 'paciente_id' in dados:
            paciente = Paciente.query.get(dados['paciente_id'])
            if not paciente:
                return jsonify({'erro': 'Paciente não encontrado'}), 400
            agenda.paciente_id = dados['paciente_id']

        if 'profissional_id' in dados:
            profissional = Profissional.query.get(dados['profissional_id'])
            if not profissional:
                return jsonify({'erro': 'Profissional não encontrado'}), 400
            agenda.profissional_id = dados['profissional_id']

        # Verificar conflito de horário se data/hora ou profissional mudou
        if any(campo in dados for campo in ['data_hora', 'profissional_id', 'duracao_minutos']):
            if Agenda.verificar_conflito_horario(
                agenda.profissional_id,
                agenda.data_hora,
                agenda.duracao_minutos,
                agenda_id
            ):
                return jsonify({'erro': 'Conflito de horário com outro agendamento'}), 400

        db.session.commit()
        logger.info(f"Agendamento atualizado: ID {agenda.id}")
        return jsonify(agenda.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        logger.exception(f"Erro ao atualizar agendamento ID {agenda_id}")
        return jsonify({'erro': str(e)}), 500

# --- DELETAR ---
@agenda_bp.route('/agenda/<int:agenda_id>', methods=['DELETE'])
def deletar_agendamento(agenda_id):
    """
    Deleta um agendamento
    ---
    tags:
      - Agenda
    parameters:
      - name: agenda_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Agendamento deletado com sucesso
      404:
        description: Agendamento não encontrado
    """
    try:
        agenda = Agenda.query.get_or_404(agenda_id)
        db.session.delete(agenda)
        db.session.commit()
        logger.info(f"Agendamento deletado: ID {agenda.id}")
        return jsonify({'mensagem': 'Agendamento deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Erro ao deletar agendamento ID {agenda_id}")
        return jsonify({'erro': str(e)}), 500

# --- AGENDAMENTOS POR MÊS ---
@agenda_bp.route('/agenda/mes/<int:ano>/<int:mes>', methods=['GET'])
def agendamentos_por_mes(ano, mes):
    """
    Lista agendamentos de um mês específico
    ---
    tags:
      - Agenda
    parameters:
      - name: ano
        in: path
        type: integer
        required: true
        description: Ano (ex: 2024)
      - name: mes
        in: path
        type: integer
        required: true
        description: Mês (1-12)
      - name: profissional_id
        in: query
        type: integer
        description: Filtrar por profissional
      - name: paciente_id
        in: query
        type: integer
        description: Filtrar por paciente
    responses:
      200:
        description: Lista de agendamentos do mês
      400:
        description: Parâmetros inválidos
    """
    try:
        # Validar mês
        if not 1 <= mes <= 12:
            return jsonify({'erro': 'Mês deve estar entre 1 e 12'}), 400

        # Validar ano
        if ano < 2020 or ano > 2030:
            return jsonify({'erro': 'Ano deve estar entre 2020 e 2030'}), 400

        profissional_id = request.args.get('profissional_id', type=int)
        paciente_id = request.args.get('paciente_id', type=int)

        agendamentos = Agenda.get_agendamentos_por_mes(
            ano, mes, profissional_id, paciente_id
        )

        logger.info(f"Agendamentos do mês {mes}/{ano}: {len(agendamentos)} encontrados")
        return jsonify([agenda.to_dict() for agenda in agendamentos]), 200

    except Exception as e:
        logger.exception(f"Erro ao listar agendamentos do mês {mes}/{ano}")
        return jsonify({'erro': str(e)}), 500

# --- AGENDAMENTOS POR DIA ---
@agenda_bp.route('/agenda/dia/<string:data>', methods=['GET'])
def agendamentos_por_dia(data):
    """
    Lista agendamentos de um dia específico
    ---
    tags:
      - Agenda
    parameters:
      - name: data
        in: path
        type: string
        required: true
        description: Data no formato YYYY-MM-DD
      - name: profissional_id
        in: query
        type: integer
        description: Filtrar por profissional
      - name: paciente_id
        in: query
        type: integer
        description: Filtrar por paciente
    responses:
      200:
        description: Lista de agendamentos do dia
      400:
        description: Formato de data inválido
    """
    try:
        # Validar formato da data
        try:
            data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

        profissional_id = request.args.get('profissional_id', type=int)
        paciente_id = request.args.get('paciente_id', type=int)

        agendamentos = Agenda.get_agendamentos_por_dia(
            data_obj, profissional_id, paciente_id
        )

        logger.info(f"Agendamentos do dia {data}: {len(agendamentos)} encontrados")
        return jsonify([agenda.to_dict() for agenda in agendamentos]), 200

    except Exception as e:
        logger.exception(f"Erro ao listar agendamentos do dia {data}")
        return jsonify({'erro': str(e)}), 500

# --- ATUALIZAR PRESENÇA ---
@agenda_bp.route('/agenda/<int:agenda_id>/presenca', methods=['PATCH'])
def atualizar_presenca_agendamento(agenda_id):
    """
    Atualiza apenas a presença de um agendamento
    ---
    tags:
      - Agenda
    parameters:
      - name: agenda_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - presente
          properties:
            presente:
              type: boolean
              description: true = presente, false = ausente, null = não informado
    responses:
      200:
        description: Presença atualizada
      400:
        description: Dados inválidos
      404:
        description: Agendamento não encontrado
    """
    try:
        agenda = Agenda.query.get_or_404(agenda_id)
        dados = request.get_json()

        if 'presente' not in dados:
            return jsonify({'erro': 'Campo presente é obrigatório'}), 400

        # Validar se o valor é boolean ou null
        if dados['presente'] is not None and not isinstance(dados['presente'], bool):
            return jsonify({'erro': 'Campo presente deve ser true, false ou null'}), 400

        agenda.presente = dados['presente']
        db.session.commit()
        
        logger.info(f"Presença do agendamento ID {agenda_id} atualizada para {agenda.presente}")
        return jsonify(agenda.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        logger.exception(f"Erro ao atualizar presença do agendamento ID {agenda_id}")
        return jsonify({'erro': str(e)}), 500

# --- ATUALIZAR STATUS ---
@agenda_bp.route('/agenda/<int:agenda_id>/status', methods=['PATCH'])
def atualizar_status_agendamento(agenda_id):
    """
    Atualiza apenas o status de um agendamento
    ---
    tags:
      - Agenda
    parameters:
      - name: agenda_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [Agendado, Confirmado, Cancelado, Realizado, Faltou]
    responses:
      200:
        description: Status atualizado
      400:
        description: Status inválido
      404:
        description: Agendamento não encontrado
    """
    try:
        agenda = Agenda.query.get_or_404(agenda_id)
        dados = request.get_json()

        if 'status' not in dados:
            return jsonify({'erro': 'Status é obrigatório'}), 400

        try:
            # Mapear valores em maiúsculo para os valores corretos do enum
            status_map = {
                'AGENDADO': 'Agendado',
                'CONFIRMADO': 'Confirmado', 
                'CANCELADO': 'Cancelado',
                'REALIZADO': 'Realizado',
                'FALTOU': 'Faltou'
            }
            status_value = status_map.get(dados['status'], dados['status'])
            agenda.status = StatusAgendamentoEnum(status_value)
        except ValueError:
            return jsonify({'erro': 'Status inválido. Valores aceitos: AGENDADO, CONFIRMADO, CANCELADO, REALIZADO, FALTOU'}), 400

        db.session.commit()
        logger.info(f"Status do agendamento ID {agenda_id} atualizado para {agenda.status.value}")
        return jsonify(agenda.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        logger.exception(f"Erro ao atualizar status do agendamento ID {agenda_id}")
        return jsonify({'erro': str(e)}), 500
