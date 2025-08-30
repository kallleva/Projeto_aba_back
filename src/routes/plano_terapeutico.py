from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models import db, PlanoTerapeutico, Paciente, Profissional

plano_terapeutico_bp = Blueprint('plano_terapeutico', __name__)

@plano_terapeutico_bp.route('/planos-terapeuticos', methods=['GET'])
def listar_planos():
    """Lista todos os planos terapêuticos"""
    try:
        planos = PlanoTerapeutico.query.all()
        return jsonify([plano.to_dict() for plano in planos]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@plano_terapeutico_bp.route('/planos-terapeuticos/<int:plano_id>', methods=['GET'])
def obter_plano(plano_id):
    """Obtém um plano terapêutico específico"""
    try:
        plano = PlanoTerapeutico.query.get_or_404(plano_id)
        return jsonify(plano.to_dict()), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@plano_terapeutico_bp.route('/planos-terapeuticos/paciente/<int:paciente_id>', methods=['GET'])
def listar_planos_por_paciente(paciente_id):
    """Lista planos terapêuticos de um paciente específico"""
    try:
        planos = PlanoTerapeutico.query.filter_by(paciente_id=paciente_id).all()
        return jsonify([plano.to_dict() for plano in planos]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@plano_terapeutico_bp.route('/planos-terapeuticos/profissional/<int:profissional_id>', methods=['GET'])
def listar_planos_por_profissional(profissional_id):
    """Lista planos terapêuticos de um profissional específico"""
    try:
        planos = PlanoTerapeutico.query.filter_by(profissional_id=profissional_id).all()
        return jsonify([plano.to_dict() for plano in planos]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@plano_terapeutico_bp.route('/planos-terapeuticos', methods=['POST'])
def criar_plano():
    """Cria um novo plano terapêutico"""
    try:
        dados = request.get_json()
        
        # Validações
        if not dados.get('paciente_id'):
            return jsonify({'erro': 'ID do paciente é obrigatório'}), 400
        if not dados.get('profissional_id'):
            return jsonify({'erro': 'ID do profissional é obrigatório'}), 400
        if not dados.get('objetivo_geral'):
            return jsonify({'erro': 'Objetivo geral é obrigatório'}), 400
        
        # Verificar se paciente e profissional existem
        paciente = Paciente.query.get(dados['paciente_id'])
        if not paciente:
            return jsonify({'erro': 'Paciente não encontrado'}), 404
        
        profissional = Profissional.query.get(dados['profissional_id'])
        if not profissional:
            return jsonify({'erro': 'Profissional não encontrado'}), 404
        
        # Processar data de criação
        data_criacao = None
        if dados.get('data_criacao'):
            try:
                data_criacao = datetime.strptime(dados['data_criacao'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        # Criar plano terapêutico
        plano = PlanoTerapeutico(
            paciente_id=dados['paciente_id'],
            profissional_id=dados['profissional_id'],
            objetivo_geral=dados['objetivo_geral'],
            data_criacao=data_criacao
        )
        
        db.session.add(plano)
        db.session.commit()
        
        return jsonify(plano.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@plano_terapeutico_bp.route('/planos-terapeuticos/<int:plano_id>', methods=['PUT'])
def atualizar_plano(plano_id):
    """Atualiza um plano terapêutico existente"""
    try:
        plano = PlanoTerapeutico.query.get_or_404(plano_id)
        dados = request.get_json()
        
        # Verificar se paciente existe (se está sendo alterado)
        if 'paciente_id' in dados:
            paciente = Paciente.query.get(dados['paciente_id'])
            if not paciente:
                return jsonify({'erro': 'Paciente não encontrado'}), 404
            plano.paciente_id = dados['paciente_id']
        
        # Verificar se profissional existe (se está sendo alterado)
        if 'profissional_id' in dados:
            profissional = Profissional.query.get(dados['profissional_id'])
            if not profissional:
                return jsonify({'erro': 'Profissional não encontrado'}), 404
            plano.profissional_id = dados['profissional_id']
        
        # Atualizar outros campos se fornecidos
        if 'objetivo_geral' in dados:
            plano.objetivo_geral = dados['objetivo_geral']
        if 'data_criacao' in dados:
            try:
                plano.data_criacao = datetime.strptime(dados['data_criacao'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        db.session.commit()
        return jsonify(plano.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@plano_terapeutico_bp.route('/planos-terapeuticos/<int:plano_id>', methods=['DELETE'])
def deletar_plano(plano_id):
    """Deleta um plano terapêutico"""
    try:
        plano = PlanoTerapeutico.query.get_or_404(plano_id)
        db.session.delete(plano)
        db.session.commit()
        return jsonify({'mensagem': 'Plano terapêutico deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

