"""
Script para popular o banco de dados com dados iniciais
"""
import os
import sys
from datetime import date, datetime, timedelta
from src.models import (
    db, Usuario, Profissional, Paciente, PlanoTerapeutico, MetaTerapeutica, 
    ProfissionalPaciente, TipoUsuarioEnum, DiagnosticoEnum, StatusMetaEnum,
    StatusVinculoEnum, TipoAtendimentoEnum
)

def create_seed_data():
    """Cria dados iniciais para o sistema"""
    print("🌱 Iniciando criação de dados iniciais...")
    
    try:
        # Verificar se já existem dados
        if Usuario.query.first():
            print("⚠️  Dados já existem no banco. Pulando criação de seed data.")
            return
        
        # 1. Criar Profissionais
        print("👨‍⚕️ Criando profissionais...")
        
        profissional1 = Profissional(
            nome="Dr. João Silva",
            especialidade="Terapia ABA",
            email="joao.silva@clinica.com",
            telefone="(11) 99999-1111"
        )
        
        profissional2 = Profissional(
            nome="Dra. Maria Santos",
            especialidade="Psicologia Comportamental",
            email="maria.santos@clinica.com",
            telefone="(11) 99999-2222"
        )
        
        profissional3 = Profissional(
            nome="Dr. Pedro Costa",
            especialidade="Fonoaudiologia",
            email="pedro.costa@clinica.com",
            telefone="(11) 99999-3333"
        )
        
        db.session.add_all([profissional1, profissional2, profissional3])
        db.session.flush()  # Para obter os IDs
        
        # 2. Criar Pacientes
        print("👶 Criando pacientes...")
        
        paciente1 = Paciente(
            nome="Ana Clara Oliveira",
            data_nascimento=date(2018, 5, 15),
            diagnostico=DiagnosticoEnum.TEA,
            responsavel="Carlos Oliveira",
            contato="(11) 99999-4444"
        )
        
        paciente2 = Paciente(
            nome="Lucas Ferreira",
            data_nascimento=date(2017, 8, 22),
            diagnostico=DiagnosticoEnum.TEA,
            responsavel="Sandra Ferreira",
            contato="(11) 99999-5555"
        )
        
        paciente3 = Paciente(
            nome="Sophia Rodrigues",
            data_nascimento=date(2019, 3, 10),
            diagnostico=DiagnosticoEnum.TEA,
            responsavel="Roberto Rodrigues",
            contato="(11) 99999-6666"
        )
        
        db.session.add_all([paciente1, paciente2, paciente3])
        db.session.flush()
        
        # 3. Criar Usuários Profissionais
        print("👤 Criando usuários profissionais...")
        
        usuario_prof1 = Usuario(
            email="prof1@clinica.com",
            nome="Dr. João Silva",
            tipo_usuario=TipoUsuarioEnum.PROFISSIONAL,
            profissional_id=profissional1.id
        )
        usuario_prof1.set_senha("prof123")
        
        usuario_prof2 = Usuario(
            email="prof2@clinica.com",
            nome="Dra. Maria Santos",
            tipo_usuario=TipoUsuarioEnum.PROFISSIONAL,
            profissional_id=profissional2.id
        )
        usuario_prof2.set_senha("prof123")
        
        usuario_prof3 = Usuario(
            email="prof3@clinica.com",
            nome="Dr. Pedro Costa",
            tipo_usuario=TipoUsuarioEnum.PROFISSIONAL,
            profissional_id=profissional3.id
        )
        usuario_prof3.set_senha("prof123")
        
        # 4. Criar Usuários Responsáveis
        print("👨‍👩‍👧‍👦 Criando usuários responsáveis...")
        
        usuario_resp1 = Usuario(
            email="carlos.oliveira@email.com",
            nome="Carlos Oliveira",
            tipo_usuario=TipoUsuarioEnum.RESPONSAVEL,
            paciente_id=paciente1.id
        )
        usuario_resp1.set_senha("resp123")
        
        usuario_resp2 = Usuario(
            email="sandra.ferreira@email.com",
            nome="Sandra Ferreira",
            tipo_usuario=TipoUsuarioEnum.RESPONSAVEL,
            paciente_id=paciente2.id
        )
        usuario_resp2.set_senha("resp123")
        
        usuario_resp3 = Usuario(
            email="roberto.rodrigues@email.com",
            nome="Roberto Rodrigues",
            tipo_usuario=TipoUsuarioEnum.RESPONSAVEL,
            paciente_id=paciente3.id
        )
        usuario_resp3.set_senha("resp123")
        
        # 5. Criar Usuário Administrador
        print("🛠️ Criando usuário administrador...")
        
        usuario_admin = Usuario(
            email="admin@clinica.com",
            nome="Administrador",
            tipo_usuario=TipoUsuarioEnum.ADMIN
        )
        usuario_admin.set_senha("admin123")
        
        db.session.add_all([
            usuario_prof1, usuario_prof2, usuario_prof3,
            usuario_resp1, usuario_resp2, usuario_resp3,
            usuario_admin
        ])
        db.session.flush()
        
        # 6. Criar Vínculos Profissional-Paciente
        print("🔗 Criando vínculos profissional-paciente...")
        
        # Ana Clara com Dr. João (ABA) e Dra. Maria (Psicologia)
        vinculo1 = ProfissionalPaciente(
            profissional_id=profissional1.id,
            paciente_id=paciente1.id,
            tipo_atendimento=TipoAtendimentoEnum.TERAPIA_ABA,
            data_inicio=date.today() - timedelta(days=30),
            frequencia_semanal=3,
            duracao_sessao=60,
            observacoes="Paciente com boa evolução na comunicação",
            criado_por=usuario_admin.id
        )
        
        vinculo2 = ProfissionalPaciente(
            profissional_id=profissional2.id,
            paciente_id=paciente1.id,
            tipo_atendimento=TipoAtendimentoEnum.PSICOLOGIA,
            data_inicio=date.today() - timedelta(days=20),
            frequencia_semanal=2,
            duracao_sessao=45,
            observacoes="Trabalho focado em habilidades sociais",
            criado_por=usuario_admin.id
        )
        
        # Lucas com Dra. Maria (Psicologia) e Dr. Pedro (Fonoaudiologia)
        vinculo3 = ProfissionalPaciente(
            profissional_id=profissional2.id,
            paciente_id=paciente2.id,
            tipo_atendimento=TipoAtendimentoEnum.PSICOLOGIA,
            data_inicio=date.today() - timedelta(days=45),
            frequencia_semanal=2,
            duracao_sessao=50,
            observacoes="Foco em comportamentos adaptativos",
            criado_por=usuario_admin.id
        )
        
        vinculo4 = ProfissionalPaciente(
            profissional_id=profissional3.id,
            paciente_id=paciente2.id,
            tipo_atendimento=TipoAtendimentoEnum.FONOAUDIOLOGIA,
            data_inicio=date.today() - timedelta(days=15),
            frequencia_semanal=2,
            duracao_sessao=40,
            observacoes="Desenvolvimento da linguagem oral",
            criado_por=usuario_admin.id
        )
        
        # Sophia com Dr. João (ABA) e Dr. Pedro (Fonoaudiologia)
        vinculo5 = ProfissionalPaciente(
            profissional_id=profissional1.id,
            paciente_id=paciente3.id,
            tipo_atendimento=TipoAtendimentoEnum.TERAPIA_ABA,
            data_inicio=date.today() - timedelta(days=10),
            frequencia_semanal=4,
            duracao_sessao=45,
            observacoes="Paciente iniciante, adaptação ao ambiente",
            criado_por=usuario_admin.id
        )
        
        vinculo6 = ProfissionalPaciente(
            profissional_id=profissional3.id,
            paciente_id=paciente3.id,
            tipo_atendimento=TipoAtendimentoEnum.FONOAUDIOLOGIA,
            data_inicio=date.today() - timedelta(days=5),
            frequencia_semanal=1,
            duracao_sessao=30,
            observacoes="Estimulação precoce da comunicação",
            criado_por=usuario_admin.id
        )
        
        db.session.add_all([vinculo1, vinculo2, vinculo3, vinculo4, vinculo5, vinculo6])
        
        # 7. Criar Planos Terapêuticos
        print("📋 Criando planos terapêuticos...")
        
        plano1 = PlanoTerapeutico(
            paciente_id=paciente1.id,
            profissional_id=profissional1.id,
            titulo="Plano de Desenvolvimento - Ana Clara",
            descricao="Plano focado em comunicação e habilidades sociais",
            data_inicio=date.today(),
            data_fim=date.today() + timedelta(days=90),
            ativo=True
        )
        
        plano2 = PlanoTerapeutico(
            paciente_id=paciente2.id,
            profissional_id=profissional2.id,
            titulo="Plano de Desenvolvimento - Lucas",
            descricao="Plano focado em comportamento e autonomia",
            data_inicio=date.today(),
            data_fim=date.today() + timedelta(days=120),
            ativo=True
        )
        
        plano3 = PlanoTerapeutico(
            paciente_id=paciente3.id,
            profissional_id=profissional1.id,
            titulo="Plano de Desenvolvimento - Sophia",
            descricao="Plano focado em comunicação e linguagem",
            data_inicio=date.today(),
            data_fim=date.today() + timedelta(days=100),
            ativo=True
        )
        
        db.session.add_all([plano1, plano2, plano3])
        db.session.flush()
        
        # 8. Criar Metas Terapêuticas
        print("🎯 Criando metas terapêuticas...")
        
        metas_plano1 = [
            MetaTerapeutica(
                plano_terapeutico_id=plano1.id,
                titulo="Comunicação Verbal",
                descricao="Aumentar vocabulário expressivo em 50%",
                status=StatusMetaEnum.EM_ANDAMENTO,
                data_limite=date.today() + timedelta(days=30)
            ),
            MetaTerapeutica(
                plano_terapeutico_id=plano1.id,
                titulo="Interação Social",
                descricao="Participar de atividades em grupo por 15 minutos",
                status=StatusMetaEnum.EM_ANDAMENTO,
                data_limite=date.today() + timedelta(days=45)
            )
        ]
        
        metas_plano2 = [
            MetaTerapeutica(
                plano_terapeutico_id=plano2.id,
                titulo="Autonomia Pessoal",
                descricao="Vestir-se independentemente",
                status=StatusMetaEnum.EM_ANDAMENTO,
                data_limite=date.today() + timedelta(days=60)
            ),
            MetaTerapeutica(
                plano_terapeutico_id=plano2.id,
                titulo="Controle Comportamental",
                descricao="Reduzir comportamentos disruptivos em 70%",
                status=StatusMetaEnum.EM_ANDAMENTO,
                data_limite=date.today() + timedelta(days=90)
            )
        ]
        
        metas_plano3 = [
            MetaTerapeutica(
                plano_terapeutico_id=plano3.id,
                titulo="Desenvolvimento da Fala",
                descricao="Produzir 20 palavras diferentes",
                status=StatusMetaEnum.EM_ANDAMENTO,
                data_limite=date.today() + timedelta(days=40)
            ),
            MetaTerapeutica(
                plano_terapeutico_id=plano3.id,
                titulo="Compreensão de Instruções",
                descricao="Seguir comandos simples de 2 etapas",
                status=StatusMetaEnum.EM_ANDAMENTO,
                data_limite=date.today() + timedelta(days=50)
            )
        ]
        
        db.session.add_all(metas_plano1 + metas_plano2 + metas_plano3)
        
        # Commit todas as alterações
        db.session.commit()
        
        print("✅ Dados iniciais criados com sucesso!")
        print("\n📊 Resumo dos dados criados:")
        print(f"   • {Profissional.query.count()} Profissionais")
        print(f"   • {Paciente.query.count()} Pacientes")
        print(f"   • {Usuario.query.count()} Usuários")
        print(f"   • {ProfissionalPaciente.query.count()} Vínculos Profissional-Paciente")
        print(f"   • {PlanoTerapeutico.query.count()} Planos Terapêuticos")
        print(f"   • {MetaTerapeutica.query.count()} Metas Terapêuticas")
        
        print("\n🔑 Credenciais de acesso:")
        print("   ADMINISTRADOR:")
        print("   • Email: admin@clinica.com | Senha: admin123")
        print("\n   PROFISSIONAIS:")
        print("   • Email: prof1@clinica.com | Senha: prof123")
        print("   • Email: prof2@clinica.com | Senha: prof123")
        print("   • Email: prof3@clinica.com | Senha: prof123")
        print("\n   RESPONSÁVEIS:")
        print("   • Email: carlos.oliveira@email.com | Senha: resp123")
        print("   • Email: sandra.ferreira@email.com | Senha: resp123")
        print("   • Email: roberto.rodrigues@email.com | Senha: resp123")
        
        print("\n🔗 Vínculos criados:")
        print("   • Ana Clara: Dr. João (ABA) + Dra. Maria (Psicologia)")
        print("   • Lucas: Dra. Maria (Psicologia) + Dr. Pedro (Fonoaudiologia)")
        print("   • Sophia: Dr. João (ABA) + Dr. Pedro (Fonoaudiologia)")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados iniciais: {e}")
        db.session.rollback()
        raise

def clear_all_data():
    """Remove todos os dados do banco (cuidado!)"""
    print("🗑️  Removendo todos os dados do banco...")
    
    try:
        # Remover em ordem reversa para respeitar foreign keys
        MetaTerapeutica.query.delete()
        PlanoTerapeutico.query.delete()
        ProfissionalPaciente.query.delete()
        Usuario.query.delete()
        Paciente.query.delete()
        Profissional.query.delete()
        
        db.session.commit()
        print("✅ Todos os dados foram removidos!")
        
    except Exception as e:
        print(f"❌ Erro ao remover dados: {e}")
        db.session.rollback()
        raise

if __name__ == "__main__":
    # Este script pode ser executado diretamente para criar dados de teste
    from src.main import app
    
    with app.app_context():
        create_seed_data()