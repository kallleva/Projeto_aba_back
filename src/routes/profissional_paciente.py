from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models import db, ProfissionalPaciente, Profissional, Paciente, StatusVinculoEnum, TipoAtendimentoEnum

profissional_paciente_bp = Blueprint('profissional_paciente', __name__)

@profissional_paciente_bp.route('/vinculos', methods=['GET'])
def listar_vinculos():
    """
    Lista todos os vínculos profissional-paciente
    ---
    tags:
      - Vínculos Profissional-Paciente
    parameters:
      - name: status
        in: query
        type: string
        enum: [ATIVO, INATIVO, SUSPENSO]
        description: Filtrar por status do vínculo
      - name: profissional_id
        in: query
        type: integer
        description: Filtrar por ID do profissional
      - name: paciente_id
        in: query
        type: integer
        description: Filtrar por ID do paciente
      - name: tipo_atendimento
        in: query
        type: string
        description: Filtrar por tipo de atendimento
    responses:
      200:
        description: Lista de vínculos
        schema:
          type: array
          items:
            type: object
    """
    try:
        query = ProfissionalPaciente.query
        
        # Filtros opcionais
        status = request.args.get('status')
        if status:
            try:
                status_enum = StatusVinculoEnum(status)
                query = query.filter(ProfissionalPaciente.status == status_enum)
            except ValueError:
                return jsonify({'erro': 'Status inválido'}), 400
        
        profissional_id = request.args.get('profissional_id')
        if profissional_id:
            query = query.filter(ProfissionalPaciente.profissional_id == profissional_id)
        
        paciente_id = request.args.get('paciente_id')
        if paciente_id:
            query = query.filter(ProfissionalPaciente.paciente_id == paciente_id)
        
        tipo_atendimento = request.args.get('tipo_atendimento')
        if tipo_atendimento:
            try:
                tipo_enum = TipoAtendimentoEnum(tipo_atendimento)
                query = query.filter(ProfissionalPaciente.tipo_atendimento == tipo_enum)
            except ValueError:
                return jsonify({'erro': 'Tipo de atendimento inválido'}), 400
        
        vinculos = query.all()
        return jsonify([vinculo.to_dict_completo() for vinculo in vinculos]), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@profissional_paciente_bp.route('/vinculos/<int:vinculo_id>', methods=['GET'])
def obter_vinculo(vinculo_id):
    """
    Obtém um vínculo específico
    ---
    tags:
      - Vínculos Profissional-Paciente
    parameters:
      - name: vinculo_id
        in: path
        type: integer
        required: true
        description: ID do vínculo
    responses:
      200:
        description: Vínculo encontrado
      404:
        description: Vínculo não encontrado
    """
    try:
        vinculo = ProfissionalPaciente.query.get_or_404(vinculo_id)
        return jsonify(vinculo.to_dict_completo()), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@profissional_paciente_bp.route('/vinculos', methods=['POST'])
def criar_vinculo():
    """
    Cria um novo vínculo profissional-paciente
    ---
    tags:
      - Vínculos Profissional-Paciente
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - profissional_id
            - paciente_id
            - tipo_atendimento
          properties:
            profissional_id:
              type: integer
            paciente_id:
              type: integer
            tipo_atendimento:
              type: string
              enum: [Terapia ABA, Psicologia, Fonoaudiologia, Terapia Ocupacional, Fisioterapia, Psicopedagogia, Outro]
            data_inicio:
              type: string
              format: date
            frequencia_semanal:
              type: integer
            duracao_sessao:
              type: integer
            observacoes:
              type: string
    responses:
      201:
        description: Vínculo criado com sucesso
      400:
        description: Erro de validação
    """
    try:
        dados = request.get_json()
        
        # Validações obrigatórias
        if not dados.get('profissional_id'):
            return jsonify({'erro': 'ID do profissional é obrigatório'}), 400
        if not dados.get('paciente_id'):
            return jsonify({'erro': 'ID do paciente é obrigatório'}), 400
        if not dados.get('tipo_atendimento'):
            return jsonify({'erro': 'Tipo de atendimento é obrigatório'}), 400
        
        # Verificar se profissional existe
        profissional = Profissional.query.get(dados['profissional_id'])
        if not profissional:
            return jsonify({'erro': 'Profissional não encontrado'}), 404
        
        # Verificar se paciente existe
        paciente = Paciente.query.get(dados['paciente_id'])
        if not paciente:
            return jsonify({'erro': 'Paciente não encontrado'}), 404
        
        # Validar tipo de atendimento
        try:
            tipo_atendimento = TipoAtendimentoEnum(dados['tipo_atendimento'])
        except ValueError:
            return jsonify({'erro': 'Tipo de atendimento inválido'}), 400
        
        # Verificar se já existe vínculo ativo do mesmo tipo
        vinculo_existente = ProfissionalPaciente.query.filter_by(
            profissional_id=dados['profissional_id'],
            paciente_id=dados['paciente_id'],
            tipo_atendimento=tipo_atendimento,
            status=StatusVinculoEnum.ATIVO
        ).first()
        
        if vinculo_existente:
            return jsonify({'erro': 'Já existe um vínculo ativo deste tipo entre o profissional e paciente'}), 400
        
        # Processar data de início
        data_inicio = date.today()
        if dados.get('data_inicio'):
            try:
                data_inicio = datetime.strptime(dados['data_inicio'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        # Criar vínculo
        vinculo = ProfissionalPaciente(
            profissional_id=dados['profissional_id'],
            paciente_id=dados['paciente_id'],
            tipo_atendimento=tipo_atendimento,
            data_inicio=data_inicio,
            frequencia_semanal=dados.get('frequencia_semanal'),
            duracao_sessao=dados.get('duracao_sessao'),
            observacoes=dados.get('observacoes'),
            criado_por=dados.get('criado_por')  # ID do usuário que criou
        )
        
        db.session.add(vinculo)
        db.session.commit()
        
        return jsonify(vinculo.to_dict_completo()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@profissional_paciente_bp.route('/vinculos/<int:vinculo_id>', methods=['PUT'])
def atualizar_vinculo(vinculo_id):
    """
    Atualiza um vínculo existente
    ---
    tags:
      - Vínculos Profissional-Paciente
    parameters:
      - name: vinculo_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [ATIVO, INATIVO, SUSPENSO]
            data_fim:
              type: string
              format: date
            frequencia_semanal:
              type: integer
            duracao_sessao:
              type: integer
            observacoes:
              type: string
    responses:
      200:
        description: Vínculo atualizado
      404:
        description: Vínculo não encontrado
    """
    try:
        vinculo = ProfissionalPaciente.query.get_or_404(vinculo_id)
        dados = request.get_json()
        
        # Atualizar status se fornecido
        if 'status' in dados:
            try:
                novo_status = StatusVinculoEnum(dados['status'])
                vinculo.status = novo_status
                
                # Se inativando, definir data_fim se não fornecida
                if novo_status == StatusVinculoEnum.INATIVO and not dados.get('data_fim'):
                    vinculo.data_fim = date.today()
                elif novo_status == StatusVinculoEnum.ATIVO:
                    vinculo.data_fim = None
                    
            except ValueError:
                return jsonify({'erro': 'Status inválido'}), 400
        
        # Atualizar data_fim se fornecida
        if 'data_fim' in dados:
            if dados['data_fim']:
                try:
                    vinculo.data_fim = datetime.strptime(dados['data_fim'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
            else:
                vinculo.data_fim = None
        
        # Atualizar outros campos
        if 'frequencia_semanal' in dados:
            vinculo.frequencia_semanal = dados['frequencia_semanal']
        if 'duracao_sessao' in dados:
            vinculo.duracao_sessao = dados['duracao_sessao']
        if 'observacoes' in dados:
            vinculo.observacoes = dados['observacoes']
        
        db.session.commit()
        return jsonify(vinculo.to_dict_completo()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@profissional_paciente_bp.route('/vinculos/<int:vinculo_id>/ativar', methods=['POST'])
def ativar_vinculo(vinculo_id):
    """
    Ativa um vínculo
    ---
    tags:
      - Vínculos Profissional-Paciente
    parameters:
      - name: vinculo_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Vínculo ativado
      404:
        description: Vínculo não encontrado
    """
    try:
        vinculo = ProfissionalPaciente.query.get_or_404(vinculo_id)
        vinculo.ativar()
        db.session.commit()
        return jsonify(vinculo.to_dict_completo()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@profissional_paciente_bp.route('/vinculos/<int:vinculo_id>/inativar', methods=['POST'])
def inativar_vinculo(vinculo_id):
    """
    Inativa um vínculo
    ---
    tags:
      - Vínculos Profissional-Paciente
    parameters:
      - name: vinculo_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            data_fim:
              type: string
              format: date
    responses:
      200:
        description: Vínculo inativado
      404:
        description: Vínculo não encontrado
    """
    try:
        vinculo = ProfissionalPaciente.query.get_or_404(vinculo_id)
        dados = request.get_json() or {}
        
        data_fim = None
        if dados.get('data_fim'):
            try:
                data_fim = datetime.strptime(dados['data_fim'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        vinculo.inativar(data_fim)
        db.session.commit()
        return jsonify(vinculo.to_dict_completo()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@profissional_paciente_bp.route('/vinculos/<int:vinculo_id>/suspender', methods=['POST'])
def suspender_vinculo(vinculo_id):
    """
    Suspende um vínculo
    ---
    tags:
      - Vínculos Profissional-Paciente
    parameters:
      - name: vinculo_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Vínculo suspenso
      404:
        description: Vínculo não encontrado
    """
    try:
        vinculo = ProfissionalPaciente.query.get_or_404(vinculo_id)
        vinculo.suspender()
        db.session.commit()
        return jsonify(vinculo.to_dict_completo()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@profissional_paciente_bp.route('/profissionais/<int:profissional_id>/pacientes', methods=['GET'])
def listar_pacientes_do_profissional(profissional_id):
    """
    Lista pacientes vinculados a um profissional
    ---
    tags:
      - Vínculos Profissional-Paciente
    parameters:
      - name: profissional_id
        in: path
        type: integer
        required: true
      - name: apenas_ativos
        in: query
        type: boolean
        default: true
        description: Se deve retornar apenas vínculos ativos
    responses:
      200:
        description: Lista de pacientes do profissional
      404:
        description: Profissional não encontrado
    """
    try:
        profissional = Profissional.query.get_or_404(profissional_id)
        apenas_ativos = request.args.get('apenas_ativos', 'true').lower() == 'true'
        
        query = ProfissionalPaciente.query.filter_by(profissional_id=profissional_id)
        
        if apenas_ativos:
            query = query.filter_by(status=StatusVinculoEnum.ATIVO)
        
        vinculos = query.all()
        return jsonify([vinculo.to_dict_completo() for vinculo in vinculos]), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@profissional_paciente_bp.route('/pacientes/<int:paciente_id>/profissionais', methods=['GET'])
def listar_profissionais_do_paciente(paciente_id):
    """
    Lista profissionais vinculados a um paciente
    ---
    tags:
      - Vínculos Profissional-Paciente
    parameters:
      - name: paciente_id
        in: path
        type: integer
        required: true
      - name: apenas_ativos
        in: query
        type: boolean
        default: true
        description: Se deve retornar apenas vínculos ativos
    responses:
      200:
        description: Lista de profissionais do paciente
      404:
        description: Paciente não encontrado
    """
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        apenas_ativos = request.args.get('apenas_ativos', 'true').lower() == 'true'
        
        query = ProfissionalPaciente.query.filter_by(paciente_id=paciente_id)
        
        if apenas_ativos:
            query = query.filter_by(status=StatusVinculoEnum.ATIVO)
        
        vinculos = query.all()
        return jsonify([vinculo.to_dict_completo() for vinculo in vinculos]), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
