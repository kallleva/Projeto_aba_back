from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_
from src.models import db, Paciente, Profissional, PlanoTerapeutico, MetaTerapeutica, ChecklistDiario, StatusMetaEnum, ChecklistResposta, Pergunta, TipoPerguntaEnum

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/relatorios/dashboard', methods=['GET'])
def obter_dados_dashboard():
    """
    Obtém dados estatísticos para o dashboard
    ---
    tags:
      - Relatórios
    responses:
      200:
        description: Retorna resumo geral e distribuições
        schema:
          type: object
          properties:
            resumo:
              type: object
              properties:
                total_pacientes: { type: integer }
                total_profissionais: { type: integer }
                total_metas_ativas: { type: integer }
                registros_hoje: { type: integer }
            distribuicao_diagnosticos:
              type: array
              items:
                type: object
                properties:
                  diagnostico: { type: string }
                  count: { type: integer }
            distribuicao_metas:
              type: array
              items:
                type: object
                properties:
                  status: { type: string }
                  count: { type: integer }
    """
    try:
        total_pacientes = Paciente.query.count()
        total_profissionais = Profissional.query.count()
        total_metas_ativas = MetaTerapeutica.query.filter_by(status=StatusMetaEnum.EM_ANDAMENTO).count()
        hoje = date.today()
        registros_hoje = ChecklistDiario.query.filter_by(data=hoje).count()

        diagnosticos = db.session.query(
            Paciente.diagnostico,
            func.count(Paciente.id).label('count')
        ).group_by(Paciente.diagnostico).all()

        distribuicao_diagnosticos = [{'diagnostico': diag.value, 'count': count} for diag, count in diagnosticos]

        metas_status = db.session.query(
            MetaTerapeutica.status,
            func.count(MetaTerapeutica.id).label('count')
        ).group_by(MetaTerapeutica.status).all()

        distribuicao_metas = [{'status': status.value, 'count': count} for status, count in metas_status]

        return jsonify({
            'resumo': {
                'total_pacientes': total_pacientes,
                'total_profissionais': total_profissionais,
                'total_metas_ativas': total_metas_ativas,
                'registros_hoje': registros_hoje
            },
            'distribuicao_diagnosticos': distribuicao_diagnosticos,
            'distribuicao_metas': distribuicao_metas
        }), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@relatorios_bp.route('/relatorios/evolucao-meta/<int:meta_id>', methods=['GET'])
def obter_evolucao_meta(meta_id):
    """
    Obtém evolução de uma meta específica
    ---
    tags:
      - Relatórios
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
        description: Evolução da meta
        schema:
          type: object
          properties:
            evolucao:
              type: array
              items:
                type: object
                properties:
                  data: { type: string }
                  nota: { type: integer }
                  observacao: { type: string }
            estatisticas:
              type: object
              properties:
                total_registros: { type: integer }
                nota_media: { type: number }
                nota_maxima: { type: integer }
                nota_minima: { type: integer }
                tendencia: { type: string }
    """
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')

        query = ChecklistDiario.query.filter_by(meta_id=meta_id)

        if data_inicio:
            query = query.filter(ChecklistDiario.data >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
        if data_fim:
            query = query.filter(ChecklistDiario.data <= datetime.strptime(data_fim, '%Y-%m-%d').date())

        registros = query.order_by(ChecklistDiario.data).all()
        
        # Incluir dados das fórmulas calculadas
        dados_evolucao = []
        for r in registros:
            dados_registro = {
                'data': r.data.isoformat(), 
                'nota': r.nota, 
                'observacao': r.observacao,
                'formulas_calculadas': []
            }
            
            # Buscar fórmulas calculadas deste checklist
            for resposta in r.respostas:
                if resposta.pergunta and resposta.pergunta.tipo == TipoPerguntaEnum.FORMULA and resposta.resposta_calculada:
                    try:
                        valor_numerico = float(resposta.resposta_calculada)
                    except (ValueError, TypeError):
                        valor_numerico = None
                    
                    dados_registro['formulas_calculadas'].append({
                        'pergunta_id': resposta.pergunta_id,
                        'pergunta_texto': resposta.pergunta.texto,
                        'formula': resposta.pergunta.formula,
                        'valor_calculado': resposta.resposta_calculada,
                        'valor_numerico': valor_numerico
                    })
            
            dados_evolucao.append(dados_registro)

        if registros:
            notas = [r.nota for r in registros]
            estatisticas = {
                'total_registros': len(registros),
                'nota_media': round(sum(notas) / len(notas), 2),
                'nota_maxima': max(notas),
                'nota_minima': min(notas),
                'tendencia': 'crescente' if notas[-1] > notas[0] else 'decrescente' if notas[-1] < notas[0] else 'estável'
            }
        else:
            estatisticas = {
                'total_registros': 0,
                'nota_media': 0,
                'nota_maxima': 0,
                'nota_minima': 0,
                'tendencia': 'sem_dados'
            }

        return jsonify({'evolucao': dados_evolucao, 'estatisticas': estatisticas}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@relatorios_bp.route('/relatorios/paciente/<int:paciente_id>', methods=['GET'])
def obter_relatorio_paciente(paciente_id):
    """
    Obtém relatório completo de um paciente
    ---
    tags:
      - Relatórios
    parameters:
      - name: paciente_id
        in: path
        type: integer
        required: true
        description: ID do paciente
    responses:
      200:
        description: Relatório do paciente
    """
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        planos = PlanoTerapeutico.query.filter_by(paciente_id=paciente_id).all()
        metas_ids = [meta.id for plano in planos for meta in plano.metas_terapeuticas]
        metas = MetaTerapeutica.query.filter(MetaTerapeutica.id.in_(metas_ids)).all() if metas_ids else []

        data_limite = date.today() - timedelta(days=30)
        registros_recentes = db.session.query(ChecklistDiario).join(MetaTerapeutica).join(PlanoTerapeutico).filter(
            PlanoTerapeutico.paciente_id == paciente_id,
            ChecklistDiario.data >= data_limite
        ).order_by(ChecklistDiario.data.desc()).all()

        total_metas = len(metas)
        metas_concluidas = len([m for m in metas if m.status == StatusMetaEnum.CONCLUIDA])
        metas_ativas = total_metas - metas_concluidas

        media_notas_recentes = round(sum(r.nota for r in registros_recentes) / len(registros_recentes), 2) if registros_recentes else 0

        evolucao_por_meta = {}
        for meta in metas:
            registros_meta = [r for r in registros_recentes if r.meta_id == meta.id]
            if registros_meta:
                registros_detalhados = []
                for r in sorted(registros_meta, key=lambda x: x.data):
                    registro_detalhado = {
                        'data': r.data.isoformat(), 
                        'nota': r.nota,
                        'formulas_calculadas': []
                    }
                    
                    # Incluir fórmulas calculadas
                    for resposta in r.respostas:
                        if resposta.pergunta and resposta.pergunta.tipo == TipoPerguntaEnum.FORMULA and resposta.resposta_calculada:
                            try:
                                valor_numerico = float(resposta.resposta_calculada)
                            except (ValueError, TypeError):
                                valor_numerico = None
                            
                            registro_detalhado['formulas_calculadas'].append({
                                'pergunta_id': resposta.pergunta_id,
                                'pergunta_texto': resposta.pergunta.texto,
                                'formula': resposta.pergunta.formula,
                                'valor_calculado': resposta.resposta_calculada,
                                'valor_numerico': valor_numerico
                            })
                    
                    registros_detalhados.append(registro_detalhado)
                
                evolucao_por_meta[meta.id] = {
                    'meta_descricao': meta.descricao,
                    'registros': registros_detalhados
                }

        return jsonify({
            'paciente': paciente.to_dict(),
            'resumo': {
                'total_planos': len(planos),
                'total_metas': total_metas,
                'metas_ativas': metas_ativas,
                'metas_concluidas': metas_concluidas,
                'registros_ultimos_30_dias': len(registros_recentes),
                'media_notas_recentes': media_notas_recentes
            },
            'evolucao_por_meta': evolucao_por_meta
        }), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@relatorios_bp.route('/relatorios/profissional/<int:profissional_id>', methods=['GET'])
def obter_relatorio_profissional(profissional_id):
    """
    Obtém relatório de atividades de um profissional
    ---
    tags:
      - Relatórios
    parameters:
      - name: profissional_id
        in: path
        type: integer
        required: true
        description: ID do profissional
    responses:
      200:
        description: Relatório do profissional
    """
    try:
        profissional = Profissional.query.get_or_404(profissional_id)
        planos = PlanoTerapeutico.query.filter_by(profissional_id=profissional_id).all()
        pacientes_ids = [plano.paciente_id for plano in planos]
        pacientes = Paciente.query.filter(Paciente.id.in_(pacientes_ids)).all() if pacientes_ids else []

        metas_ids = [meta.id for plano in planos for meta in plano.metas_terapeuticas]
        metas = MetaTerapeutica.query.filter(MetaTerapeutica.id.in_(metas_ids)).all() if metas_ids else []

        distribuicao_diagnosticos = {}
        for paciente in pacientes:
            diag = paciente.diagnostico.value
            distribuicao_diagnosticos[diag] = distribuicao_diagnosticos.get(diag, 0) + 1

        total_metas = len(metas)
        metas_concluidas = len([m for m in metas if m.status == StatusMetaEnum.CONCLUIDA])

        return jsonify({
            'profissional': profissional.to_dict(),
            'resumo': {
                'total_pacientes': len(pacientes),
                'total_planos': len(planos),
                'total_metas': total_metas,
                'metas_concluidas': metas_concluidas,
                'taxa_conclusao': round((metas_concluidas / total_metas * 100), 2) if total_metas > 0 else 0
            },
            'distribuicao_diagnosticos': [{'diagnostico': diag, 'count': count} for diag, count in distribuicao_diagnosticos.items()]
        }), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@relatorios_bp.route('/relatorios/periodo', methods=['GET'])
def obter_relatorio_periodo():
    """
    Obtém relatório de um período específico
    ---
    tags:
      - Relatórios
    parameters:
      - name: data_inicio
        in: query
        type: string
        format: date
        required: true
        description: Data inicial (YYYY-MM-DD)
      - name: data_fim
        in: query
        type: string
        format: date
        required: true
        description: Data final (YYYY-MM-DD)
    responses:
      200:
        description: Relatório do período
    """
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')

        if not data_inicio or not data_fim:
            return jsonify({'erro': 'data_inicio e data_fim são obrigatórios'}), 400

        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()

        registros = ChecklistDiario.query.filter(
            and_(ChecklistDiario.data >= data_inicio_obj, ChecklistDiario.data <= data_fim_obj)
        ).all()

        registros_por_data = {}
        formulas_por_data = {}
        
        for r in registros:
            data_str = r.data.isoformat()
            registros_por_data.setdefault(data_str, []).append(r.nota)
            
            # Coletar fórmulas calculadas por data
            formulas_do_dia = []
            for resposta in r.respostas:
                if resposta.pergunta and resposta.pergunta.tipo == TipoPerguntaEnum.FORMULA and resposta.resposta_calculada:
                    try:
                        valor_numerico = float(resposta.resposta_calculada)
                    except (ValueError, TypeError):
                        valor_numerico = None
                    
                    formulas_do_dia.append({
                        'pergunta_id': resposta.pergunta_id,
                        'pergunta_texto': resposta.pergunta.texto,
                        'formula': resposta.pergunta.formula,
                        'valor_calculado': resposta.resposta_calculada,
                        'valor_numerico': valor_numerico
                    })
            
            if formulas_do_dia:
                formulas_por_data[data_str] = formulas_do_dia

        evolucao_diaria = []
        for d, notas in sorted(registros_por_data.items()):
            evolucao_dia = {
                'data': d, 
                'media_notas': round(sum(notas) / len(notas), 2), 
                'total_registros': len(notas),
                'formulas_calculadas': formulas_por_data.get(d, [])
            }
            evolucao_diaria.append(evolucao_dia)

        if registros:
            todas_notas = [r.nota for r in registros]
            estatisticas = {
                'total_registros': len(registros),
                'media_geral': round(sum(todas_notas) / len(todas_notas), 2),
                'nota_maxima': max(todas_notas),
                'nota_minima': min(todas_notas)
            }
        else:
            estatisticas = {'total_registros': 0, 'media_geral': 0, 'nota_maxima': 0, 'nota_minima': 0}

        return jsonify({
            'periodo': {'data_inicio': data_inicio, 'data_fim': data_fim},
            'evolucao_diaria': evolucao_diaria,
            'estatisticas': estatisticas
        }), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@relatorios_bp.route('/relatorios/formulas/<int:meta_id>', methods=['GET'])
def obter_relatorio_formulas(meta_id):
    """
    Obtém relatório das fórmulas calculadas de uma meta específica
    ---
    tags:
      - Relatórios
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
        description: Relatório das fórmulas calculadas
        schema:
          type: object
          properties:
            meta_id: { type: integer }
            meta_descricao: { type: string }
            formulas_calculadas:
              type: array
              items:
                type: object
                properties:
                  pergunta_id: { type: integer }
                  pergunta_texto: { type: string }
                  formula: { type: string }
                  valores_calculados:
                    type: array
                    items:
                      type: object
                      properties:
                        data: { type: string }
                        valor_calculado: { type: string }
                        checklist_id: { type: integer }
            estatisticas_formulas:
              type: object
              properties:
                total_formulas: { type: integer }
                formulas_com_dados: { type: integer }
                media_por_formula:
                  type: array
                  items:
                    type: object
                    properties:
                      pergunta_id: { type: integer }
                      media_valor: { type: number }
    """
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')

        # Buscar a meta
        meta = MetaTerapeutica.query.get_or_404(meta_id)
        
        # Buscar checklists da meta
        query = ChecklistDiario.query.filter_by(meta_id=meta_id)
        
        if data_inicio:
            query = query.filter(ChecklistDiario.data >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
        if data_fim:
            query = query.filter(ChecklistDiario.data <= datetime.strptime(data_fim, '%Y-%m-%d').date())
        
        checklists = query.order_by(ChecklistDiario.data).all()
        
        # Buscar todas as perguntas do tipo FORMULA dos formulários da meta
        perguntas_formula = []
        for formulario in meta.formularios:
            perguntas_formula.extend([
                p for p in formulario.perguntas 
                if p.tipo == TipoPerguntaEnum.FORMULA
            ])
        
        # Organizar dados das fórmulas
        formulas_calculadas = []
        for pergunta in perguntas_formula:
            valores_calculados = []
            
            # Buscar respostas calculadas desta pergunta
            for checklist in checklists:
                resposta = next(
                    (r for r in checklist.respostas if r.pergunta_id == pergunta.id), 
                    None
                )
                
                if resposta and resposta.resposta_calculada:
                    try:
                        valor_numerico = float(resposta.resposta_calculada)
                        valores_calculados.append({
                            'data': checklist.data.isoformat(),
                            'valor_calculado': resposta.resposta_calculada,
                            'valor_numerico': valor_numerico,
                            'checklist_id': checklist.id
                        })
                    except (ValueError, TypeError):
                        valores_calculados.append({
                            'data': checklist.data.isoformat(),
                            'valor_calculado': resposta.resposta_calculada,
                            'valor_numerico': None,
                            'checklist_id': checklist.id
                        })
            
            formulas_calculadas.append({
                'pergunta_id': pergunta.id,
                'pergunta_texto': pergunta.texto,
                'formula': pergunta.formula,
                'valores_calculados': valores_calculados
            })
        
        # Calcular estatísticas das fórmulas
        estatisticas_formulas = {
            'total_formulas': len(perguntas_formula),
            'formulas_com_dados': len([f for f in formulas_calculadas if f['valores_calculados']]),
            'media_por_formula': []
        }
        
        for formula_data in formulas_calculadas:
            valores_numericos = [
                v['valor_numerico'] for v in formula_data['valores_calculados'] 
                if v['valor_numerico'] is not None
            ]
            
            if valores_numericos:
                media = round(sum(valores_numericos) / len(valores_numericos), 2)
                estatisticas_formulas['media_por_formula'].append({
                    'pergunta_id': formula_data['pergunta_id'],
                    'media_valor': media,
                    'total_registros': len(valores_numericos)
                })
        
        return jsonify({
            'meta_id': meta_id,
            'meta_descricao': meta.descricao,
            'formulas_calculadas': formulas_calculadas,
            'estatisticas_formulas': estatisticas_formulas
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@relatorios_bp.route('/relatorios/formulas/evolucao/<int:pergunta_id>', methods=['GET'])
def obter_evolucao_formula(pergunta_id):
    """
    Obtém evolução de uma fórmula específica ao longo do tempo
    ---
    tags:
      - Relatórios
    parameters:
      - name: pergunta_id
        in: path
        type: integer
        required: true
        description: ID da pergunta (fórmula)
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
        description: Evolução da fórmula
    """
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Buscar a pergunta
        pergunta = Pergunta.query.get_or_404(pergunta_id)
        
        if pergunta.tipo != TipoPerguntaEnum.FORMULA:
            return jsonify({'erro': 'Pergunta não é do tipo fórmula'}), 400
        
        # Buscar respostas calculadas
        query = db.session.query(ChecklistResposta).join(ChecklistDiario).filter(
            ChecklistResposta.pergunta_id == pergunta_id,
            ChecklistResposta.resposta_calculada.isnot(None)
        )
        
        if data_inicio:
            query = query.filter(ChecklistDiario.data >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
        if data_fim:
            query = query.filter(ChecklistDiario.data <= datetime.strptime(data_fim, '%Y-%m-%d').date())
        
        respostas = query.order_by(ChecklistDiario.data).all()
        
        # Organizar dados de evolução
        evolucao = []
        valores_numericos = []
        
        for resposta in respostas:
            try:
                valor_numerico = float(resposta.resposta_calculada)
                valores_numericos.append(valor_numerico)
            except (ValueError, TypeError):
                valor_numerico = None
            
            evolucao.append({
                'data': resposta.checklist.data.isoformat(),
                'valor_calculado': resposta.resposta_calculada,
                'valor_numerico': valor_numerico,
                'checklist_id': resposta.checklist_id,
                'meta_id': resposta.checklist.meta_id,
                'meta_descricao': resposta.checklist.meta.descricao if resposta.checklist.meta else None
            })
        
        # Calcular estatísticas
        estatisticas = {
            'total_registros': len(evolucao),
            'formula': pergunta.formula,
            'pergunta_texto': pergunta.texto
        }
        
        if valores_numericos:
            estatisticas.update({
                'media': round(sum(valores_numericos) / len(valores_numericos), 2),
                'maximo': max(valores_numericos),
                'minimo': min(valores_numericos),
                'tendencia': 'crescente' if len(valores_numericos) > 1 and valores_numericos[-1] > valores_numericos[0] else 'decrescente' if len(valores_numericos) > 1 and valores_numericos[-1] < valores_numericos[0] else 'estável'
            })
        else:
            estatisticas.update({
                'media': 0,
                'maximo': 0,
                'minimo': 0,
                'tendencia': 'sem_dados'
            })
        
        return jsonify({
            'pergunta': pergunta.to_dict(),
            'evolucao': evolucao,
            'estatisticas': estatisticas
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
