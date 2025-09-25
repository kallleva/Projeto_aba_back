from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models import db, MetaTerapeutica, PlanoTerapeutico, StatusMetaEnum, Formulario

meta_terapeutica_bp = Blueprint('meta_terapeutica', __name__)

# -----------------------
# GETs
# -----------------------

@meta_terapeutica_bp.route('/metas-terapeuticas', methods=['GET'])
def listar_metas():
    try:
        metas = MetaTerapeutica.query.all()
        return jsonify([meta.to_dict() for meta in metas]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@meta_terapeutica_bp.route('/metas-terapeuticas/<int:meta_id>', methods=['GET'])
def obter_meta(meta_id):
    try:
        meta = MetaTerapeutica.query.get_or_404(meta_id)
        return jsonify(meta.to_dict()), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@meta_terapeutica_bp.route('/metas-terapeuticas/plano/<int:plano_id>', methods=['GET'])
def listar_metas_por_plano(plano_id):
    try:
        metas = MetaTerapeutica.query.filter_by(plano_id=plano_id).all()
        return jsonify([meta.to_dict() for meta in metas]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# -----------------------
# POST
# -----------------------

@meta_terapeutica_bp.route('/metas-terapeuticas', methods=['POST'])
def criar_meta():
    try:
        dados = request.get_json()

        # Validações obrigatórias
        for campo in ['plano_id', 'descricao', 'data_inicio', 'data_previsao_termino']:
            if not dados.get(campo):
                return jsonify({'erro': f'{campo} é obrigatório'}), 400

        plano = PlanoTerapeutico.query.get(dados['plano_id'])
        if not plano:
            return jsonify({'erro': 'Plano terapêutico não encontrado'}), 404

        # Datas
        try:
            data_inicio = datetime.strptime(dados['data_inicio'], '%Y-%m-%d').date()
            data_previsao_termino = datetime.strptime(dados['data_previsao_termino'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

        if data_previsao_termino <= data_inicio:
            return jsonify({'erro': 'Data de término deve ser posterior à data de início'}), 400

        # Status
        status = StatusMetaEnum.EM_ANDAMENTO
        if dados.get('status'):
            try:
                status = StatusMetaEnum(dados['status'])
            except ValueError:
                return jsonify({'erro': 'Status inválido'}), 400

        # Criar meta
        meta = MetaTerapeutica(
            plano_id=dados['plano_id'],
            descricao=dados['descricao'],
            data_inicio=data_inicio,
            data_previsao_termino=data_previsao_termino,
            status=status
        )

        # Vincular múltiplos formulários existentes
        formulario_ids = dados.get('formularios', [])
        if formulario_ids:
            formularios = Formulario.query.filter(Formulario.id.in_(formulario_ids)).all()
            meta.formularios = formularios

        db.session.add(meta)
        db.session.commit()

        return jsonify(meta.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# -----------------------
# PUT
# -----------------------

@meta_terapeutica_bp.route('/metas-terapeuticas/<int:meta_id>', methods=['PUT'])
def atualizar_meta(meta_id):
    try:
        meta = MetaTerapeutica.query.get_or_404(meta_id)
        dados = request.get_json()

        if 'plano_id' in dados:
            plano = PlanoTerapeutico.query.get(dados['plano_id'])
            if not plano:
                return jsonify({'erro': 'Plano terapêutico não encontrado'}), 404
            meta.plano_id = dados['plano_id']

        if 'descricao' in dados:
            meta.descricao = dados['descricao']

        if 'data_inicio' in dados:
            try:
                meta.data_inicio = datetime.strptime(dados['data_inicio'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data de início inválido'}), 400

        if 'data_previsao_termino' in dados:
            try:
                meta.data_previsao_termino = datetime.strptime(dados['data_previsao_termino'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data de término inválido'}), 400

        if meta.data_previsao_termino <= meta.data_inicio:
            return jsonify({'erro': 'Data de término deve ser posterior à data de início'}), 400

        if 'status' in dados:
            try:
                meta.status = StatusMetaEnum(dados['status'])
            except ValueError:
                return jsonify({'erro': 'Status inválido'}), 400

        # Atualizar múltiplos formulários
        if 'formularios' in dados:
            formulario_ids = dados['formularios']
            formularios = Formulario.query.filter(Formulario.id.in_(formulario_ids)).all()
            meta.formularios = formularios

        db.session.commit()
        return jsonify(meta.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# -----------------------
# DELETE
# -----------------------

@meta_terapeutica_bp.route('/metas-terapeuticas/<int:meta_id>', methods=['DELETE'])
def deletar_meta(meta_id):
    try:
        meta = MetaTerapeutica.query.get_or_404(meta_id)
        db.session.delete(meta)
        db.session.commit()
        return jsonify({'mensagem': 'Meta terapêutica deletada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# -----------------------
# Concluir meta
# -----------------------

@meta_terapeutica_bp.route('/metas-terapeuticas/<int:meta_id>/concluir', methods=['PUT'])
def concluir_meta(meta_id):
    try:
        meta = MetaTerapeutica.query.get_or_404(meta_id)
        meta.status = StatusMetaEnum.CONCLUIDA
        db.session.commit()
        return jsonify(meta.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500
