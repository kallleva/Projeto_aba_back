from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models import db, ChecklistDiario, MetaTerapeutica, ChecklistResposta

checklist_diario_bp = Blueprint('checklist_diario', __name__)

# --------------------------
# Listagens
# --------------------------
@checklist_diario_bp.route('/checklists-diarios', methods=['GET'])
def listar_checklists():
    try:
        checklists = ChecklistDiario.query.all()
        return jsonify([c.to_dict() for c in checklists]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@checklist_diario_bp.route('/checklists-diarios/<int:checklist_id>', methods=['GET'])
def obter_checklist(checklist_id):
    try:
        checklist = ChecklistDiario.query.get_or_404(checklist_id)
        return jsonify(checklist.to_dict()), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@checklist_diario_bp.route('/checklists-diarios/meta/<int:meta_id>', methods=['GET'])
def listar_checklists_por_meta(meta_id):
    try:
        checklists = ChecklistDiario.query.filter_by(meta_id=meta_id).order_by(ChecklistDiario.data.desc()).all()
        return jsonify([c.to_dict() for c in checklists]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# --------------------------
# Criação de checklist
# --------------------------
@checklist_diario_bp.route('/checklists-diarios', methods=['POST'])
def criar_checklist():
    try:
        dados = request.get_json()
        meta_id = dados.get('meta_id')
        nota = dados.get('nota')
        observacao = dados.get('observacao')
        respostas_dict = dados.get('respostas', {})  # {pergunta_id: resposta}

        # Validações
        if not meta_id:
            return jsonify({'erro': 'ID da meta é obrigatório'}), 400

        meta = MetaTerapeutica.query.get(meta_id)
        if not meta:
            return jsonify({'erro': 'Meta terapêutica não encontrada'}), 404

        # Data
        data_checklist = date.today()
        if dados.get('data'):
            try:
                data_checklist = datetime.strptime(dados['data'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

        # Checklist existente
        if ChecklistDiario.query.filter_by(meta_id=meta_id, data=data_checklist).first():
            return jsonify({'erro': 'Já existe um checklist para esta meta nesta data'}), 400

        # Criar checklist temporário para validação
        checklist_temp = ChecklistDiario(meta_id=meta_id, data=data_checklist, nota=nota, observacao=observacao)
        checklist_temp.meta = meta  # Para poder usar o método de validação
        
        # Validar respostas obrigatórias
        valido, mensagem = checklist_temp.validar_respostas(respostas_dict)
        if not valido:
            return jsonify({'erro': mensagem}), 400

        # Criar checklist
        checklist = ChecklistDiario(meta_id=meta_id, data=data_checklist, nota=nota, observacao=observacao)

        # Adicionar respostas para todas as perguntas dos formulários vinculados
        for formulario in meta.formularios:
            for pergunta in formulario.perguntas:
                resposta_texto = respostas_dict.get(str(pergunta.id), "")
                resposta_obj = ChecklistResposta(pergunta_id=pergunta.id, resposta=resposta_texto)
                
                # Calcular fórmula se for pergunta do tipo FORMULA
                if pergunta.tipo.value == 'FORMULA':
                    resposta_calculada = resposta_obj.calcular_formula(respostas_dict)
                    resposta_obj.resposta_calculada = resposta_calculada
                
                checklist.respostas.append(resposta_obj)

        db.session.add(checklist)
        db.session.commit()
        return jsonify(checklist.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# --------------------------
# Atualização de checklist
# --------------------------
@checklist_diario_bp.route('/checklists-diarios/<int:checklist_id>', methods=['PUT'])
def atualizar_checklist(checklist_id):
    try:
        checklist = ChecklistDiario.query.get_or_404(checklist_id)
        dados = request.get_json()

        if 'meta_id' in dados:
            meta = MetaTerapeutica.query.get(dados['meta_id'])
            if not meta:
                return jsonify({'erro': 'Meta terapêutica não encontrada'}), 404
            checklist.meta_id = meta.id

        if 'nota' in dados:
            checklist.nota = dados['nota']

        if 'observacao' in dados:
            checklist.observacao = dados['observacao']

        # Atualizar respostas
        respostas_dict = dados.get('respostas', {})
        if respostas_dict:
            # Validar respostas obrigatórias
            valido, mensagem = checklist.validar_respostas(respostas_dict)
            if not valido:
                return jsonify({'erro': mensagem}), 400
            
            for resposta in checklist.respostas:
                if str(resposta.pergunta_id) in respostas_dict:
                    resposta.resposta = respostas_dict[str(resposta.pergunta_id)]
                    
                    # Recalcular fórmula se for pergunta do tipo FORMULA
                    if resposta.pergunta and resposta.pergunta.tipo.value == 'FORMULA':
                        resposta.resposta_calculada = resposta.calcular_formula(respostas_dict)

        db.session.commit()
        return jsonify(checklist.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# --------------------------
# Deletar checklist
# --------------------------
@checklist_diario_bp.route('/checklists-diarios/<int:checklist_id>', methods=['DELETE'])
def deletar_checklist(checklist_id):
    try:
        checklist = ChecklistDiario.query.get_or_404(checklist_id)
        db.session.delete(checklist)
        db.session.commit()
        return jsonify({'mensagem': 'Checklist diário deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500
