from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models import db, Paciente, DiagnosticoEnum

paciente_bp = Blueprint('paciente', __name__)

@paciente_bp.route('/pacientes', methods=['GET'])
def listar_pacientes():
    """Lista todos os pacientes"""
    try:
        pacientes = Paciente.query.all()
        return jsonify([paciente.to_dict() for paciente in pacientes]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@paciente_bp.route('/pacientes/<int:paciente_id>', methods=['GET'])
def obter_paciente(paciente_id):
    """Obtém um paciente específico"""
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        return jsonify(paciente.to_dict()), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@paciente_bp.route('/pacientes', methods=['POST'])
def criar_paciente():
    """Cria um novo paciente"""
    try:
        dados = request.get_json()
        
        # Validações
        if not dados.get('nome'):
            return jsonify({'erro': 'Nome é obrigatório'}), 400
        if not dados.get('data_nascimento'):
            return jsonify({'erro': 'Data de nascimento é obrigatória'}), 400
        if not dados.get('responsavel'):
            return jsonify({'erro': 'Responsável é obrigatório'}), 400
        if not dados.get('contato'):
            return jsonify({'erro': 'Contato é obrigatório'}), 400
        if not dados.get('diagnostico'):
            return jsonify({'erro': 'Diagnóstico é obrigatório'}), 400
        
        # Validar diagnóstico
        try:
            diagnostico = DiagnosticoEnum(dados['diagnostico'])
        except ValueError:
            return jsonify({'erro': 'Diagnóstico inválido'}), 400
        
        # Validar data de nascimento
        try:
            data_nascimento = datetime.strptime(dados['data_nascimento'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        # Criar paciente
        paciente = Paciente(
            nome=dados['nome'],
            data_nascimento=data_nascimento,
            responsavel=dados['responsavel'],
            contato=dados['contato'],
            diagnostico=diagnostico
        )
        
        db.session.add(paciente)
        db.session.commit()
        
        return jsonify(paciente.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@paciente_bp.route('/pacientes/<int:paciente_id>', methods=['PUT'])
def atualizar_paciente(paciente_id):
    """Atualiza um paciente existente"""
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        dados = request.get_json()
        
        # Atualizar campos se fornecidos
        if 'nome' in dados:
            paciente.nome = dados['nome']
        if 'data_nascimento' in dados:
            try:
                paciente.data_nascimento = datetime.strptime(dados['data_nascimento'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        if 'responsavel' in dados:
            paciente.responsavel = dados['responsavel']
        if 'contato' in dados:
            paciente.contato = dados['contato']
        if 'diagnostico' in dados:
            try:
                paciente.diagnostico = DiagnosticoEnum(dados['diagnostico'])
            except ValueError:
                return jsonify({'erro': 'Diagnóstico inválido'}), 400
        
        db.session.commit()
        return jsonify(paciente.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@paciente_bp.route('/pacientes/<int:paciente_id>', methods=['DELETE'])
def deletar_paciente(paciente_id):
    """Deleta um paciente"""
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        db.session.delete(paciente)
        db.session.commit()
        return jsonify({'mensagem': 'Paciente deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

