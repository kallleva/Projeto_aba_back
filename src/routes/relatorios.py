from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_
from src.models import db, Paciente, Profissional, PlanoTerapeutico, MetaTerapeutica, ChecklistDiario, StatusMetaEnum, DiagnosticoEnum

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/relatorios/dashboard', methods=['GET'])
def obter_dados_dashboard():
    """Obtém dados estatísticos para o dashboard"""
    try:
        # Contadores básicos
        total_pacientes = Paciente.query.count()
        total_profissionais = Profissional.query.count()
        total_metas_ativas = MetaTerapeutica.query.filter_by(status=StatusMetaEnum.EM_ANDAMENTO).count()
        
        # Registros de hoje
        hoje = date.today()
        registros_hoje = ChecklistDiario.query.filter_by(data=hoje).count()
        
        # Distribuição por diagnóstico
        diagnosticos = db.session.query(
            Paciente.diagnostico,
            func.count(Paciente.id).label('count')
        ).group_by(Paciente.diagnostico).all()
        
        distribuicao_diagnosticos = [
            {'diagnostico': diag.value, 'count': count} 
            for diag, count in diagnosticos
        ]
        
        # Metas por status
        metas_status = db.session.query(
            MetaTerapeutica.status,
            func.count(MetaTerapeutica.id).label('count')
        ).group_by(MetaTerapeutica.status).all()
        
        distribuicao_metas = [
            {'status': status.value, 'count': count} 
            for status, count in metas_status
        ]
        
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
    """Obtém dados de evolução de uma meta específica"""
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Query base
        query = ChecklistDiario.query.filter_by(meta_id=meta_id)
        
        # Aplicar filtros de data se fornecidos
        if data_inicio:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            query = query.filter(ChecklistDiario.data >= data_inicio_obj)
        
        if data_fim:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            query = query.filter(ChecklistDiario.data <= data_fim_obj)
        
        # Ordenar por data
        registros = query.order_by(ChecklistDiario.data).all()
        
        # Formatar dados para gráfico
        dados_evolucao = [
            {
                'data': registro.data.isoformat(),
                'nota': registro.nota,
                'observacao': registro.observacao
            }
            for registro in registros
        ]
        
        # Calcular estatísticas
        if registros:
            notas = [r.nota for r in registros]
            estatisticas = {
                'total_registros': len(registros),
                'nota_media': round(sum(notas) / len(notas), 2),
                'nota_maxima': max(notas),
                'nota_minima': min(notas),
                'tendencia': 'crescente' if len(notas) > 1 and notas[-1] > notas[0] else 'decrescente' if len(notas) > 1 and notas[-1] < notas[0] else 'estável'
            }
        else:
            estatisticas = {
                'total_registros': 0,
                'nota_media': 0,
                'nota_maxima': 0,
                'nota_minima': 0,
                'tendencia': 'sem_dados'
            }
        
        return jsonify({
            'evolucao': dados_evolucao,
            'estatisticas': estatisticas
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@relatorios_bp.route('/relatorios/paciente/<int:paciente_id>', methods=['GET'])
def obter_relatorio_paciente(paciente_id):
    """Obtém relatório completo de um paciente"""
    try:
        # Buscar paciente
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Buscar planos terapêuticos
        planos = PlanoTerapeutico.query.filter_by(paciente_id=paciente_id).all()
        
        # Buscar metas
        metas_ids = [meta.id for plano in planos for meta in plano.metas_terapeuticas]
        metas = MetaTerapeutica.query.filter(MetaTerapeutica.id.in_(metas_ids)).all() if metas_ids else []
        
        # Buscar registros dos últimos 30 dias
        data_limite = date.today() - timedelta(days=30)
        registros_recentes = db.session.query(ChecklistDiario).join(MetaTerapeutica).join(PlanoTerapeutico).filter(
            PlanoTerapeutico.paciente_id == paciente_id,
            ChecklistDiario.data >= data_limite
        ).order_by(ChecklistDiario.data.desc()).all()
        
        # Calcular estatísticas
        total_metas = len(metas)
        metas_concluidas = len([m for m in metas if m.status == StatusMetaEnum.CONCLUIDA])
        metas_ativas = total_metas - metas_concluidas
        
        # Média de notas dos últimos 30 dias
        if registros_recentes:
            notas_recentes = [r.nota for r in registros_recentes]
            media_notas_recentes = round(sum(notas_recentes) / len(notas_recentes), 2)
        else:
            media_notas_recentes = 0
        
        # Evolução por meta (últimos 30 dias)
        evolucao_por_meta = {}
        for meta in metas:
            registros_meta = [r for r in registros_recentes if r.meta_id == meta.id]
            if registros_meta:
                evolucao_por_meta[meta.id] = {
                    'meta_descricao': meta.descricao,
                    'registros': [
                        {
                            'data': r.data.isoformat(),
                            'nota': r.nota
                        }
                        for r in sorted(registros_meta, key=lambda x: x.data)
                    ]
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
    """Obtém relatório de atividades de um profissional"""
    try:
        # Buscar profissional
        profissional = Profissional.query.get_or_404(profissional_id)
        
        # Buscar planos do profissional
        planos = PlanoTerapeutico.query.filter_by(profissional_id=profissional_id).all()
        
        # Buscar pacientes atendidos
        pacientes_ids = [plano.paciente_id for plano in planos]
        pacientes = Paciente.query.filter(Paciente.id.in_(pacientes_ids)).all() if pacientes_ids else []
        
        # Buscar metas
        metas_ids = [meta.id for plano in planos for meta in plano.metas_terapeuticas]
        metas = MetaTerapeutica.query.filter(MetaTerapeutica.id.in_(metas_ids)).all() if metas_ids else []
        
        # Distribuição de pacientes por diagnóstico
        distribuicao_diagnosticos = {}
        for paciente in pacientes:
            diag = paciente.diagnostico.value
            distribuicao_diagnosticos[diag] = distribuicao_diagnosticos.get(diag, 0) + 1
        
        # Estatísticas de metas
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
            'distribuicao_diagnosticos': [
                {'diagnostico': diag, 'count': count}
                for diag, count in distribuicao_diagnosticos.items()
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@relatorios_bp.route('/relatorios/periodo', methods=['GET'])
def obter_relatorio_periodo():
    """Obtém relatório de um período específico"""
    try:
        # Parâmetros obrigatórios
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if not data_inicio or not data_fim:
            return jsonify({'erro': 'data_inicio e data_fim são obrigatórios'}), 400
        
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        
        # Registros no período
        registros = ChecklistDiario.query.filter(
            and_(
                ChecklistDiario.data >= data_inicio_obj,
                ChecklistDiario.data <= data_fim_obj
            )
        ).all()
        
        # Agrupar registros por data
        registros_por_data = {}
        for registro in registros:
            data_str = registro.data.isoformat()
            if data_str not in registros_por_data:
                registros_por_data[data_str] = []
            registros_por_data[data_str].append(registro.nota)
        
        # Calcular médias diárias
        evolucao_diaria = []
        for data_str in sorted(registros_por_data.keys()):
            notas = registros_por_data[data_str]
            evolucao_diaria.append({
                'data': data_str,
                'media_notas': round(sum(notas) / len(notas), 2),
                'total_registros': len(notas)
            })
        
        # Estatísticas gerais do período
        if registros:
            todas_notas = [r.nota for r in registros]
            estatisticas = {
                'total_registros': len(registros),
                'media_geral': round(sum(todas_notas) / len(todas_notas), 2),
                'nota_maxima': max(todas_notas),
                'nota_minima': min(todas_notas)
            }
        else:
            estatisticas = {
                'total_registros': 0,
                'media_geral': 0,
                'nota_maxima': 0,
                'nota_minima': 0
            }
        
        return jsonify({
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': data_fim
            },
            'evolucao_diaria': evolucao_diaria,
            'estatisticas': estatisticas
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

