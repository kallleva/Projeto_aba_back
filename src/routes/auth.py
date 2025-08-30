from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from src.models import db, Usuario, Profissional, Paciente, TipoUsuarioEnum
import jwt
import os

auth_bp = Blueprint('auth', __name__)

# Chave secreta para JWT (em produção, usar variável de ambiente)
JWT_SECRET = os.environ.get('JWT_SECRET', 'sua-chave-secreta-super-segura')
JWT_EXPIRATION_HOURS = 24

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Realiza login do usuário"""
    try:
        dados = request.get_json()
        
        # Validações
        if not dados.get('email'):
            return jsonify({'erro': 'Email é obrigatório'}), 400
        if not dados.get('senha'):
            return jsonify({'erro': 'Senha é obrigatória'}), 400
        
        # Buscar usuário
        usuario = Usuario.query.filter_by(email=dados['email']).first()
        
        if not usuario or not usuario.verificar_senha(dados['senha']):
            return jsonify({'erro': 'Email ou senha incorretos'}), 401
        
        if not usuario.ativo:
            return jsonify({'erro': 'Usuário inativo'}), 401
        
        # Gerar token JWT
        payload = {
            'user_id': usuario.id,
            'email': usuario.email,
            'tipo_usuario': usuario.tipo_usuario.value,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        
        # Dados do usuário para retorno
        user_data = usuario.to_dict()
        
        # Adicionar informações específicas do tipo de usuário
        if usuario.tipo_usuario == TipoUsuarioEnum.PROFISSIONAL and usuario.profissional:
            user_data['profissional_info'] = usuario.profissional.to_dict()
        elif usuario.tipo_usuario == TipoUsuarioEnum.RESPONSAVEL and usuario.paciente:
            user_data['paciente_info'] = usuario.paciente.to_dict()
        
        return jsonify({
            'token': token,
            'usuario': user_data,
            'expires_in': JWT_EXPIRATION_HOURS * 3600  # em segundos
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """Registra um novo usuário"""
    try:
        dados = request.get_json()
        
        # Validações
        if not dados.get('email'):
            return jsonify({'erro': 'Email é obrigatório'}), 400
        if not dados.get('senha'):
            return jsonify({'erro': 'Senha é obrigatória'}), 400
        if not dados.get('nome'):
            return jsonify({'erro': 'Nome é obrigatório'}), 400
        if not dados.get('tipo_usuario'):
            return jsonify({'erro': 'Tipo de usuário é obrigatório'}), 400
        
        # Verificar se email já existe
        usuario_existente = Usuario.query.filter_by(email=dados['email']).first()
        if usuario_existente:
            return jsonify({'erro': 'Email já cadastrado'}), 400
        
        # Validar tipo de usuário
        try:
            tipo_usuario = TipoUsuarioEnum(dados['tipo_usuario'])
        except ValueError:
            return jsonify({'erro': 'Tipo de usuário inválido'}), 400
        
        # Validações específicas por tipo
        if tipo_usuario == TipoUsuarioEnum.PROFISSIONAL:
            if not dados.get('profissional_id'):
                return jsonify({'erro': 'ID do profissional é obrigatório'}), 400
            
            # Verificar se profissional existe
            profissional = Profissional.query.get(dados['profissional_id'])
            if not profissional:
                return jsonify({'erro': 'Profissional não encontrado'}), 404
            
            # Verificar se profissional já tem usuário
            usuario_prof_existente = Usuario.query.filter_by(profissional_id=dados['profissional_id']).first()
            if usuario_prof_existente:
                return jsonify({'erro': 'Profissional já possui usuário cadastrado'}), 400
        
        elif tipo_usuario == TipoUsuarioEnum.RESPONSAVEL:
            if not dados.get('paciente_id'):
                return jsonify({'erro': 'ID do paciente é obrigatório'}), 400
            
            # Verificar se paciente existe
            paciente = Paciente.query.get(dados['paciente_id'])
            if not paciente:
                return jsonify({'erro': 'Paciente não encontrado'}), 404
            
            # Verificar se paciente já tem responsável usuário
            usuario_resp_existente = Usuario.query.filter_by(paciente_id=dados['paciente_id']).first()
            if usuario_resp_existente:
                return jsonify({'erro': 'Paciente já possui responsável usuário cadastrado'}), 400
        
        # Criar usuário
        usuario = Usuario(
            email=dados['email'],
            nome=dados['nome'],
            tipo_usuario=tipo_usuario,
            profissional_id=dados.get('profissional_id'),
            paciente_id=dados.get('paciente_id')
        )
        
        usuario.set_senha(dados['senha'])
        
        db.session.add(usuario)
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Usuário criado com sucesso',
            'usuario': usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/auth/verify-token', methods=['POST'])
def verify_token():
    """Verifica se o token JWT é válido"""
    try:
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'erro': 'Token não fornecido'}), 401
        
        # Remover 'Bearer ' do início se presente
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Decodificar token
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'erro': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'erro': 'Token inválido'}), 401
        
        # Buscar usuário
        usuario = Usuario.query.get(payload['user_id'])
        if not usuario or not usuario.ativo:
            return jsonify({'erro': 'Usuário não encontrado ou inativo'}), 401
        
        # Dados do usuário para retorno
        user_data = usuario.to_dict()
        
        # Adicionar informações específicas do tipo de usuário
        if usuario.tipo_usuario == TipoUsuarioEnum.PROFISSIONAL and usuario.profissional:
            user_data['profissional_info'] = usuario.profissional.to_dict()
        elif usuario.tipo_usuario == TipoUsuarioEnum.RESPONSAVEL and usuario.paciente:
            user_data['paciente_info'] = usuario.paciente.to_dict()
        
        return jsonify({
            'valido': True,
            'usuario': user_data
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    """Realiza logout do usuário"""
    # Em uma implementação com JWT, o logout é feito no frontend removendo o token
    # Aqui podemos implementar uma blacklist de tokens se necessário
    return jsonify({'mensagem': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/auth/change-password', methods=['PUT'])
def change_password():
    """Altera a senha do usuário"""
    try:
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'erro': 'Token não fornecido'}), 401
        
        # Remover 'Bearer ' do início se presente
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Decodificar token
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'erro': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'erro': 'Token inválido'}), 401
        
        # Buscar usuário
        usuario = Usuario.query.get(payload['user_id'])
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        dados = request.get_json()
        
        # Validações
        if not dados.get('senha_atual'):
            return jsonify({'erro': 'Senha atual é obrigatória'}), 400
        if not dados.get('nova_senha'):
            return jsonify({'erro': 'Nova senha é obrigatória'}), 400
        
        # Verificar senha atual
        if not usuario.verificar_senha(dados['senha_atual']):
            return jsonify({'erro': 'Senha atual incorreta'}), 400
        
        # Alterar senha
        usuario.set_senha(dados['nova_senha'])
        db.session.commit()
        
        return jsonify({'mensagem': 'Senha alterada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# Função auxiliar para verificar autenticação em outras rotas
def verificar_autenticacao():
    """Função auxiliar para verificar autenticação em outras rotas"""
    token = request.headers.get('Authorization')
    
    if not token:
        return None, {'erro': 'Token não fornecido'}, 401
    
    # Remover 'Bearer ' do início se presente
    if token.startswith('Bearer '):
        token = token[7:]
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None, {'erro': 'Token expirado'}, 401
    except jwt.InvalidTokenError:
        return None, {'erro': 'Token inválido'}, 401
    
    # Buscar usuário
    usuario = Usuario.query.get(payload['user_id'])
    if not usuario or not usuario.ativo:
        return None, {'erro': 'Usuário não encontrado ou inativo'}, 401
    
    return usuario, None, None

