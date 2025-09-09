from flask import Blueprint, request, jsonify
from datetime import datetime
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


@meta_terapeutica_bp.route('/metas-terapeuticas/ativas', methods=['GET'])
def listar_metas_ativas():
    try:
        metas = MetaTerapeutica.query.filter_by(status=StatusMetaEnum.EM_ANDAMENTO).all()
        return jsonify([meta.to_dict() for meta in metas]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@meta_terapeutica_bp.route('/metas-terapeuticas/paciente/<int:paciente_id>/ativas', methods=['GET'])
def listar_metas_ativas_por_paciente(paciente_id):
    try:
        metas = db.session.query(MetaTerapeutica).join(PlanoTerapeutico).filter(
            PlanoTerapeutico.paciente_id == paciente_id,
            MetaTerapeutica.status == StatusMetaEnum.EM_ANDAMENTO
        ).all()
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

        # Verificar plano
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

        # Criar formulário se enviado
        if dados.get('formulario'):
            f = dados['formulario']
            formulario = Formulario(
                nome=f.get('nome'),
                descricao=f.get('descricao')
            )
            meta.formulario = formulario
            db.session.add(formulario)

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

        # Plano
        if 'plano_id' in dados:
            plano = PlanoTerapeutico.query.get(dados['plano_id'])
            if not plano:
                return jsonify({'erro': 'Plano terapêutico não encontrado'}), 404
            meta.plano_id = dados['plano_id']

        # Campos
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

        # Atualizar formulário
        if 'formulario' in dados:
            f = dados['formulario']
            if meta.formulario:
                meta.formulario.nome = f.get('nome', meta.formulario.nome)
                meta.formulario.descricao = f.get('descricao', meta.formulario.descricao)
            else:
                formulario = Formulario(
                    nome=f.get('nome'),
                    descricao=f.get('descricao')
                )
                meta.formulario = formulario
                db.session.add(formulario)

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
