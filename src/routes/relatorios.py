from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_
from src.models import db, Paciente, Profissional, PlanoTerapeutico, MetaTerapeutica, ChecklistDiario, StatusMetaEnum

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
        dados_evolucao = [{'data': r.data.isoformat(), 'nota': r.nota, 'observacao': r.observacao} for r in registros]

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
                evolucao_por_meta[meta.id] = {
                    'meta_descricao': meta.descricao,
                    'registros': [{'data': r.data.isoformat(), 'nota': r.nota} for r in sorted(registros_meta, key=lambda x: x.data)]
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
        for r in registros:
            registros_por_data.setdefault(r.data.isoformat(), []).append(r.nota)

        evolucao_diaria = [{'data': d, 'media_notas': round(sum(notas) / len(notas), 2), 'total_registros': len(notas)}
                           for d, notas in sorted(registros_por_data.items())]

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
