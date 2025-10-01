from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models import db, ChecklistDiario, MetaTerapeutica, ChecklistResposta, Pergunta, TipoPerguntaEnum

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

# --------------------------
# Relatórios de fórmulas
# --------------------------
@checklist_diario_bp.route('/checklists-diarios/<int:checklist_id>/formulas', methods=['GET'])
def obter_formulas_checklist(checklist_id):
    """
    Obtém todas as fórmulas calculadas de um checklist específico
    ---
    tags:
      - Checklist Diário
    parameters:
      - name: checklist_id
        in: path
        type: integer
        required: true
        description: ID do checklist
    responses:
      200:
        description: Fórmulas calculadas do checklist
    """
    try:
        checklist = ChecklistDiario.query.get_or_404(checklist_id)
        
        formulas_calculadas = []
        for resposta in checklist.respostas:
            if resposta.pergunta and resposta.pergunta.tipo == TipoPerguntaEnum.FORMULA:
                try:
                    valor_numerico = float(resposta.resposta_calculada) if resposta.resposta_calculada else None
                except (ValueError, TypeError):
                    valor_numerico = None
                
                formulas_calculadas.append({
                    'pergunta_id': resposta.pergunta_id,
                    'pergunta_texto': resposta.pergunta.texto,
                    'formula': resposta.pergunta.formula,
                    'resposta_original': resposta.resposta,
                    'valor_calculado': resposta.resposta_calculada,
                    'valor_numerico': valor_numerico,
                    'resposta_id': resposta.id
                })
        
        return jsonify({
            'checklist_id': checklist_id,
            'data': checklist.data.isoformat(),
            'meta_id': checklist.meta_id,
            'meta_descricao': checklist.meta.descricao if checklist.meta else None,
            'formulas_calculadas': formulas_calculadas,
            'total_formulas': len(formulas_calculadas)
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@checklist_diario_bp.route('/checklists-diarios/meta/<int:meta_id>/formulas', methods=['GET'])
def obter_formulas_meta(meta_id):
    """
    Obtém todas as fórmulas calculadas de uma meta específica
    ---
    tags:
      - Checklist Diário
    parameters:
      - name: meta_id
        in: path
        type: integer
        required: true
        description: ID da meta
      - name: data_inicio
        in: query
        type: string
        format: date
        description: Data inicial (YYYY-MM-DD)
      - name: data_fim
        in: query
        type: string
        format: date
        description: Data final (YYYY-MM-DD)
    responses:
      200:
        description: Fórmulas calculadas da meta
    """
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Buscar checklists da meta
        query = ChecklistDiario.query.filter_by(meta_id=meta_id)
        
        if data_inicio:
            query = query.filter(ChecklistDiario.data >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
        if data_fim:
            query = query.filter(ChecklistDiario.data <= datetime.strptime(data_fim, '%Y-%m-%d').date())
        
        checklists = query.order_by(ChecklistDiario.data).all()
        
        # Organizar fórmulas por pergunta
        formulas_por_pergunta = {}
        
        for checklist in checklists:
            for resposta in checklist.respostas:
                if resposta.pergunta and resposta.pergunta.tipo == TipoPerguntaEnum.FORMULA and resposta.resposta_calculada:
                    pergunta_id = resposta.pergunta_id
                    
                    if pergunta_id not in formulas_por_pergunta:
                        formulas_por_pergunta[pergunta_id] = {
                            'pergunta_id': pergunta_id,
                            'pergunta_texto': resposta.pergunta.texto,
                            'formula': resposta.pergunta.formula,
                            'valores': []
                        }
                    
                    try:
                        valor_numerico = float(resposta.resposta_calculada)
                    except (ValueError, TypeError):
                        valor_numerico = None
                    
                    formulas_por_pergunta[pergunta_id]['valores'].append({
                        'data': checklist.data.isoformat(),
                        'valor_calculado': resposta.resposta_calculada,
                        'valor_numerico': valor_numerico,
                        'checklist_id': checklist.id
                    })
        
        # Calcular estatísticas para cada fórmula
        for pergunta_id, dados in formulas_por_pergunta.items():
            valores_numericos = [v['valor_numerico'] for v in dados['valores'] if v['valor_numerico'] is not None]
            
            if valores_numericos:
                dados['estatisticas'] = {
                    'total_registros': len(valores_numericos),
                    'media': round(sum(valores_numericos) / len(valores_numericos), 2),
                    'maximo': max(valores_numericos),
                    'minimo': min(valores_numericos)
                }
            else:
                dados['estatisticas'] = {
                    'total_registros': 0,
                    'media': 0,
                    'maximo': 0,
                    'minimo': 0
                }
        
        return jsonify({
            'meta_id': meta_id,
            'meta_descricao': checklists[0].meta.descricao if checklists else None,
            'formulas_por_pergunta': list(formulas_por_pergunta.values()),
            'total_checklists': len(checklists),
            'total_formulas': len(formulas_por_pergunta)
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
