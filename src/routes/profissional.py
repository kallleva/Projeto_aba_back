import logging
from flask import Blueprint, request, jsonify
from src.models import db, Profissional

# Configurar logger
logger = logging.getLogger('profissional_logger')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  # Log no console
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

profissional_bp = Blueprint('profissional', __name__)

# --- LISTAR ---
@profissional_bp.route('/profissionais', methods=['GET'])
def listar_profissionais():
    try:
        profissionais = Profissional.query.all()
        logger.info(f"Listando {len(profissionais)} profissionais")
        return jsonify([profissional.to_dict() for profissional in profissionais]), 200
    except Exception as e:
        logger.exception("Erro ao listar profissionais")
        return jsonify({'erro': str(e)}), 500

# --- OBTER ---
@profissional_bp.route('/profissionais/<int:profissional_id>', methods=['GET'])
def obter_profissional(profissional_id):
    try:
        profissional = Profissional.query.get_or_404(profissional_id)
        logger.info(f"Profissional obtido: {profissional.nome} (ID {profissional.id})")
        return jsonify(profissional.to_dict()), 200
    except Exception as e:
        logger.exception(f"Erro ao obter profissional ID {profissional_id}")
        return jsonify({'erro': str(e)}), 500

# --- CRIAR ---
@profissional_bp.route('/profissionais', methods=['POST'])
def criar_profissional():
    try:
        dados = request.get_json()
        logger.debug(f"Dados recebidos para criar profissional: {dados}")

        # Validações
        for campo in ['nome', 'especialidade', 'email', 'telefone']:
            if not dados.get(campo):
                logger.warning(f"Campo obrigatório ausente: {campo}")
                return jsonify({'erro': f'{campo} é obrigatório'}), 400

        # Checar email duplicado
        if Profissional.query.filter_by(email=dados['email']).first():
            logger.warning(f"Email já cadastrado: {dados['email']}")
            return jsonify({'erro': 'Email já cadastrado'}), 400

        profissional = Profissional(
            nome=dados['nome'],
            especialidade=dados['especialidade'],
            email=dados['email'],
            telefone=dados['telefone']
        )

        db.session.add(profissional)
        db.session.commit()

        logger.info(f"Profissional criado: {profissional.nome} (ID {profissional.id})")
        return jsonify(profissional.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.exception("Erro ao criar profissional")
        return jsonify({'erro': str(e)}), 500

# --- ATUALIZAR ---
@profissional_bp.route('/profissionais/<int:profissional_id>', methods=['PUT'])
def atualizar_profissional(profissional_id):
    try:
        profissional = Profissional.query.get_or_404(profissional_id)
        dados = request.get_json()
        logger.debug(f"Atualizando profissional ID {profissional_id} com dados: {dados}")

        if 'email' in dados and dados['email'] != profissional.email:
            if Profissional.query.filter_by(email=dados['email']).first():
                logger.warning(f"Email já cadastrado: {dados['email']}")
                return jsonify({'erro': 'Email já cadastrado'}), 400

        for campo in ['nome', 'especialidade', 'email', 'telefone']:
            if campo in dados:
                setattr(profissional, campo, dados[campo])

        db.session.commit()
        logger.info(f"Profissional atualizado: {profissional.nome} (ID {profissional.id})")
        return jsonify(profissional.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        logger.exception(f"Erro ao atualizar profissional ID {profissional_id}")
        return jsonify({'erro': str(e)}), 500

# --- DELETAR ---
@profissional_bp.route('/profissionais/<int:profissional_id>', methods=['DELETE'])
def deletar_profissional(profissional_id):
    try:
        profissional = Profissional.query.get_or_404(profissional_id)
        db.session.delete(profissional)
        db.session.commit()
        logger.info(f"Profissional deletado: {profissional.nome} (ID {profissional.id})")
        return jsonify({'mensagem': 'Profissional deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Erro ao deletar profissional ID {profissional_id}")
        return jsonify({'erro': str(e)}), 500
