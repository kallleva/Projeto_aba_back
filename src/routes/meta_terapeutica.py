from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models import db, MetaTerapeutica, PlanoTerapeutico, StatusMetaEnum

meta_terapeutica_bp = Blueprint('meta_terapeutica', __name__)

@meta_terapeutica_bp.route('/metas-terapeuticas', methods=['GET'])
def listar_metas():
    """Lista todas as metas terapêuticas"""
    try:
        metas = MetaTerapeutica.query.all()
        return jsonify([meta.to_dict() for meta in metas]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@meta_terapeutica_bp.route('/metas-terapeuticas/<int:meta_id>', methods=['GET'])
def obter_meta(meta_id):
    """Obtém uma meta terapêutica específica"""
    try:
        meta = MetaTerapeutica.query.get_or_404(meta_id)
        return jsonify(meta.to_dict()), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@meta_terapeutica_bp.route('/metas-terapeuticas/plano/<int:plano_id>', methods=['GET'])
def listar_metas_por_plano(plano_id):
    """Lista metas terapêuticas de um plano específico"""
    try:
        metas = MetaTerapeutica.query.filter_by(plano_id=plano_id).all()
        return jsonify([meta.to_dict() for meta in metas]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@meta_terapeutica_bp.route('/metas-terapeuticas/ativas', methods=['GET'])
def listar_metas_ativas():
    """Lista metas terapêuticas em andamento"""
    try:
        metas = MetaTerapeutica.query.filter_by(status=StatusMetaEnum.EM_ANDAMENTO).all()
        return jsonify([meta.to_dict() for meta in metas]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@meta_terapeutica_bp.route('/metas-terapeuticas/paciente/<int:paciente_id>/ativas', methods=['GET'])
def listar_metas_ativas_por_paciente(paciente_id):
    """Lista metas ativas de um paciente específico"""
    try:
        metas = db.session.query(MetaTerapeutica).join(PlanoTerapeutico).filter(
            PlanoTerapeutico.paciente_id == paciente_id,
            MetaTerapeutica.status == StatusMetaEnum.EM_ANDAMENTO
        ).all()
        return jsonify([meta.to_dict() for meta in metas]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@meta_terapeutica_bp.route('/metas-terapeuticas', methods=['POST'])
def criar_meta():
    """Cria uma nova meta terapêutica"""
    try:
        dados = request.get_json()
        
        # Validações
        if not dados.get('plano_id'):
            return jsonify({'erro': 'ID do plano é obrigatório'}), 400
        if not dados.get('descricao'):
            return jsonify({'erro': 'Descrição é obrigatória'}), 400
        if not dados.get('data_inicio'):
            return jsonify({'erro': 'Data de início é obrigatória'}), 400
        if not dados.get('data_previsao_termino'):
            return jsonify({'erro': 'Data de previsão de término é obrigatória'}), 400
        
        # Verificar se plano existe
        plano = PlanoTerapeutico.query.get(dados['plano_id'])
        if not plano:
            return jsonify({'erro': 'Plano terapêutico não encontrado'}), 404
        
        # Validar datas
        try:
            data_inicio = datetime.strptime(dados['data_inicio'], '%Y-%m-%d').date()
            data_previsao_termino = datetime.strptime(dados['data_previsao_termino'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        if data_previsao_termino <= data_inicio:
            return jsonify({'erro': 'Data de término deve ser posterior à data de início'}), 400
        
        # Validar status se fornecido
        status = StatusMetaEnum.EM_ANDAMENTO
        if dados.get('status'):
            try:
                status = StatusMetaEnum(dados['status'])
            except ValueError:
                return jsonify({'erro': 'Status inválido'}), 400
        
        # Criar meta terapêutica
        meta = MetaTerapeutica(
            plano_id=dados['plano_id'],
            descricao=dados['descricao'],
            data_inicio=data_inicio,
            data_previsao_termino=data_previsao_termino,
            status=status
        )
        
        db.session.add(meta)
        db.session.commit()
        
        return jsonify(meta.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@meta_terapeutica_bp.route('/metas-terapeuticas/<int:meta_id>', methods=['PUT'])
def atualizar_meta(meta_id):
    """Atualiza uma meta terapêutica existente"""
    try:
        meta = MetaTerapeutica.query.get_or_404(meta_id)
        dados = request.get_json()
        
        # Verificar se plano existe (se está sendo alterado)
        if 'plano_id' in dados:
            plano = PlanoTerapeutico.query.get(dados['plano_id'])
            if not plano:
                return jsonify({'erro': 'Plano terapêutico não encontrado'}), 404
            meta.plano_id = dados['plano_id']
        
        # Atualizar outros campos se fornecidos
        if 'descricao' in dados:
            meta.descricao = dados['descricao']
        
        if 'data_inicio' in dados:
            try:
                meta.data_inicio = datetime.strptime(dados['data_inicio'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data de início inválido. Use YYYY-MM-DD'}), 400
        
        if 'data_previsao_termino' in dados:
            try:
                meta.data_previsao_termino = datetime.strptime(dados['data_previsao_termino'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data de término inválido. Use YYYY-MM-DD'}), 400
        
        # Validar datas após atualização
        if meta.data_previsao_termino <= meta.data_inicio:
            return jsonify({'erro': 'Data de término deve ser posterior à data de início'}), 400
        
        if 'status' in dados:
            try:
                meta.status = StatusMetaEnum(dados['status'])
            except ValueError:
                return jsonify({'erro': 'Status inválido'}), 400
        
        db.session.commit()
        return jsonify(meta.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@meta_terapeutica_bp.route('/metas-terapeuticas/<int:meta_id>', methods=['DELETE'])
def deletar_meta(meta_id):
    """Deleta uma meta terapêutica"""
    try:
        meta = MetaTerapeutica.query.get_or_404(meta_id)
        db.session.delete(meta)
        db.session.commit()
        return jsonify({'mensagem': 'Meta terapêutica deletada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@meta_terapeutica_bp.route('/metas-terapeuticas/<int:meta_id>/concluir', methods=['PUT'])
def concluir_meta(meta_id):
    """Marca uma meta como concluída"""
    try:
        meta = MetaTerapeutica.query.get_or_404(meta_id)
        meta.status = StatusMetaEnum.CONCLUIDA
        db.session.commit()
        return jsonify(meta.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

