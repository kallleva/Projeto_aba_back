from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models import db, ChecklistDiario, MetaTerapeutica

checklist_diario_bp = Blueprint('checklist_diario', __name__)

@checklist_diario_bp.route('/checklists-diarios', methods=['GET'])
def listar_checklists():
    """Lista todos os checklists diários"""
    try:
        checklists = ChecklistDiario.query.all()
        return jsonify([checklist.to_dict() for checklist in checklists]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@checklist_diario_bp.route('/checklists-diarios/<int:checklist_id>', methods=['GET'])
def obter_checklist(checklist_id):
    """Obtém um checklist diário específico"""
    try:
        checklist = ChecklistDiario.query.get_or_404(checklist_id)
        return jsonify(checklist.to_dict()), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@checklist_diario_bp.route('/checklists-diarios/meta/<int:meta_id>', methods=['GET'])
def listar_checklists_por_meta(meta_id):
    """Lista checklists diários de uma meta específica"""
    try:
        checklists = ChecklistDiario.query.filter_by(meta_id=meta_id).order_by(ChecklistDiario.data.desc()).all()
        return jsonify([checklist.to_dict() for checklist in checklists]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@checklist_diario_bp.route('/checklists-diarios/meta/<int:meta_id>/data/<string:data>', methods=['GET'])
def obter_checklist_por_meta_e_data(meta_id, data):
    """Obtém checklist de uma meta em uma data específica"""
    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        checklist = ChecklistDiario.query.filter_by(meta_id=meta_id, data=data_obj).first()
        if checklist:
            return jsonify(checklist.to_dict()), 200
        else:
            return jsonify({'mensagem': 'Checklist não encontrado para esta data'}), 404
    except ValueError:
        return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@checklist_diario_bp.route('/checklists-diarios/hoje', methods=['GET'])
def listar_checklists_hoje():
    """Lista checklists diários de hoje"""
    try:
        hoje = date.today()
        checklists = ChecklistDiario.query.filter_by(data=hoje).all()
        return jsonify([checklist.to_dict() for checklist in checklists]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@checklist_diario_bp.route('/checklists-diarios', methods=['POST'])
def criar_checklist():
    """Cria um novo checklist diário"""
    try:
        dados = request.get_json()
        
        # Validações
        if not dados.get('meta_id'):
            return jsonify({'erro': 'ID da meta é obrigatório'}), 400
        if 'nota' not in dados:
            return jsonify({'erro': 'Nota é obrigatória'}), 400
        
        # Verificar se meta existe
        meta = MetaTerapeutica.query.get(dados['meta_id'])
        if not meta:
            return jsonify({'erro': 'Meta terapêutica não encontrada'}), 404
        
        # Validar nota
        if not ChecklistDiario.validar_nota(dados['nota']):
            return jsonify({'erro': 'Nota deve ser um número inteiro entre 1 e 5'}), 400
        
        # Processar data
        data_checklist = date.today()
        if dados.get('data'):
            try:
                data_checklist = datetime.strptime(dados['data'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        # Verificar se já existe checklist para esta meta nesta data
        checklist_existente = ChecklistDiario.query.filter_by(
            meta_id=dados['meta_id'], 
            data=data_checklist
        ).first()
        if checklist_existente:
            return jsonify({'erro': 'Já existe um checklist para esta meta nesta data'}), 400
        
        # Criar checklist diário
        checklist = ChecklistDiario(
            meta_id=dados['meta_id'],
            data=data_checklist,
            nota=dados['nota'],
            observacao=dados.get('observacao')
        )
        
        db.session.add(checklist)
        db.session.commit()
        
        return jsonify(checklist.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@checklist_diario_bp.route('/checklists-diarios/<int:checklist_id>', methods=['PUT'])
def atualizar_checklist(checklist_id):
    """Atualiza um checklist diário existente"""
    try:
        checklist = ChecklistDiario.query.get_or_404(checklist_id)
        dados = request.get_json()
        
        # Verificar se meta existe (se está sendo alterada)
        if 'meta_id' in dados:
            meta = MetaTerapeutica.query.get(dados['meta_id'])
            if not meta:
                return jsonify({'erro': 'Meta terapêutica não encontrada'}), 404
            
            # Verificar se já existe checklist para a nova meta na data atual
            if dados['meta_id'] != checklist.meta_id:
                checklist_existente = ChecklistDiario.query.filter_by(
                    meta_id=dados['meta_id'], 
                    data=checklist.data
                ).first()
                if checklist_existente:
                    return jsonify({'erro': 'Já existe um checklist para esta meta nesta data'}), 400
            
            checklist.meta_id = dados['meta_id']
        
        # Atualizar outros campos se fornecidos
        if 'nota' in dados:
            if not ChecklistDiario.validar_nota(dados['nota']):
                return jsonify({'erro': 'Nota deve ser um número inteiro entre 1 e 5'}), 400
            checklist.nota = dados['nota']
        
        if 'data' in dados:
            try:
                nova_data = datetime.strptime(dados['data'], '%Y-%m-%d').date()
                # Verificar se já existe checklist para esta meta na nova data
                if nova_data != checklist.data:
                    checklist_existente = ChecklistDiario.query.filter_by(
                        meta_id=checklist.meta_id, 
                        data=nova_data
                    ).first()
                    if checklist_existente:
                        return jsonify({'erro': 'Já existe um checklist para esta meta nesta data'}), 400
                checklist.data = nova_data
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        if 'observacao' in dados:
            checklist.observacao = dados['observacao']
        
        db.session.commit()
        return jsonify(checklist.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@checklist_diario_bp.route('/checklists-diarios/<int:checklist_id>', methods=['DELETE'])
def deletar_checklist(checklist_id):
    """Deleta um checklist diário"""
    try:
        checklist = ChecklistDiario.query.get_or_404(checklist_id)
        db.session.delete(checklist)
        db.session.commit()
        return jsonify({'mensagem': 'Checklist diário deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@checklist_diario_bp.route('/checklists-diarios/estatisticas/meta/<int:meta_id>', methods=['GET'])
def obter_estatisticas_meta(meta_id):
    """Obtém estatísticas de uma meta específica"""
    try:
        checklists = ChecklistDiario.query.filter_by(meta_id=meta_id).all()
        
        if not checklists:
            return jsonify({
                'total_registros': 0,
                'nota_media': 0,
                'nota_maxima': 0,
                'nota_minima': 0
            }), 200
        
        notas = [c.nota for c in checklists]
        
        estatisticas = {
            'total_registros': len(checklists),
            'nota_media': round(sum(notas) / len(notas), 2),
            'nota_maxima': max(notas),
            'nota_minima': min(notas),
            'ultimo_registro': max(checklists, key=lambda x: x.data).data.isoformat()
        }
        
        return jsonify(estatisticas), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

