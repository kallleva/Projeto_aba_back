from flask import Blueprint, request, jsonify
from src.models import db, Profissional

profissional_bp = Blueprint('profissional', __name__)

@profissional_bp.route('/profissionais', methods=['GET'])
def listar_profissionais():
    """Lista todos os profissionais"""
    try:
        profissionais = Profissional.query.all()
        return jsonify([profissional.to_dict() for profissional in profissionais]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@profissional_bp.route('/profissionais/<int:profissional_id>', methods=['GET'])
def obter_profissional(profissional_id):
    """Obtém um profissional específico"""
    try:
        profissional = Profissional.query.get_or_404(profissional_id)
        return jsonify(profissional.to_dict()), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@profissional_bp.route('/profissionais', methods=['POST'])
def criar_profissional():
    """Cria um novo profissional"""
    try:
        dados = request.get_json()
        
        # Validações
        if not dados.get('nome'):
            return jsonify({'erro': 'Nome é obrigatório'}), 400
        if not dados.get('especialidade'):
            return jsonify({'erro': 'Especialidade é obrigatória'}), 400
        if not dados.get('email'):
            return jsonify({'erro': 'Email é obrigatório'}), 400
        if not dados.get('telefone'):
            return jsonify({'erro': 'Telefone é obrigatório'}), 400
        
        # Verificar se email já existe
        profissional_existente = Profissional.query.filter_by(email=dados['email']).first()
        if profissional_existente:
            return jsonify({'erro': 'Email já cadastrado'}), 400
        
        # Criar profissional
        profissional = Profissional(
            nome=dados['nome'],
            especialidade=dados['especialidade'],
            email=dados['email'],
            telefone=dados['telefone']
        )
        
        db.session.add(profissional)
        db.session.commit()
        
        return jsonify(profissional.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@profissional_bp.route('/profissionais/<int:profissional_id>', methods=['PUT'])
def atualizar_profissional(profissional_id):
    """Atualiza um profissional existente"""
    try:
        profissional = Profissional.query.get_or_404(profissional_id)
        dados = request.get_json()
        
        # Verificar se email já existe (se está sendo alterado)
        if 'email' in dados and dados['email'] != profissional.email:
            profissional_existente = Profissional.query.filter_by(email=dados['email']).first()
            if profissional_existente:
                return jsonify({'erro': 'Email já cadastrado'}), 400
        
        # Atualizar campos se fornecidos
        if 'nome' in dados:
            profissional.nome = dados['nome']
        if 'especialidade' in dados:
            profissional.especialidade = dados['especialidade']
        if 'email' in dados:
            profissional.email = dados['email']
        if 'telefone' in dados:
            profissional.telefone = dados['telefone']
        
        db.session.commit()
        return jsonify(profissional.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@profissional_bp.route('/profissionais/<int:profissional_id>', methods=['DELETE'])
def deletar_profissional(profissional_id):
    """Deleta um profissional"""
    try:
        profissional = Profissional.query.get_or_404(profissional_id)
        db.session.delete(profissional)
        db.session.commit()
        return jsonify({'mensagem': 'Profissional deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

