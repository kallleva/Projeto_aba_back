#!/usr/bin/env python3
"""
Script de demonstração - mostra como usar o sistema de inicialização
"""
import os
import sys
import time

def print_banner():
    """Exibe banner do sistema"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🚀 SISTEMA ABA - DEMO                    ║
║              Inicialização Automática de Dados              ║
╚══════════════════════════════════════════════════════════════╝
""")

def show_menu():
    """Exibe menu de opções"""
    print("""
📋 OPÇÕES DISPONÍVEIS:

1. 🐳 Iniciar com Docker (Recomendado)
   Comando: docker-compose up --build

2. 💻 Iniciar desenvolvimento local
   Comando: python start_dev.py

3. 🔄 Resetar banco de dados
   Comando: python reset_db.py

4. 🌱 Executar apenas seed data
   Comando: python src/database/seed_data.py

5. 📦 Executar apenas migrations
   Comando: alembic upgrade head

6. 🔍 Verificar status do banco
   Comando: python -c "from src.main import app; print('✅ Banco OK')"

7. 📖 Ver documentação da API
   URL: http://localhost:5000/api/

8. 🚪 Sair
""")

def show_credentials():
    """Exibe credenciais de acesso"""
    print("""
🔑 CREDENCIAIS DE ACESSO CRIADAS:

👨‍⚕️ PROFISSIONAIS:
   • prof1@clinica.com | senha: prof123
   • prof2@clinica.com | senha: prof123
   • prof3@clinica.com | senha: prof123

👨‍👩‍👧‍👦 RESPONSÁVEIS:
   • carlos.oliveira@email.com | senha: resp123
   • sandra.ferreira@email.com | senha: resp123
   • roberto.rodrigues@email.com | senha: resp123
""")

def show_data_summary():
    """Exibe resumo dos dados criados"""
    print("""
📊 DADOS CRIADOS AUTOMATICAMENTE:

👨‍⚕️ Profissionais:
   • Dr. João Silva (Terapia ABA)
   • Dra. Maria Santos (Psicologia Comportamental)
   • Dr. Pedro Costa (Fonoaudiologia)

👶 Pacientes:
   • Ana Clara Oliveira (TEA)
   • Lucas Ferreira (TEA)
   • Sophia Rodrigues (TEA)

📋 Planos Terapêuticos:
   • 3 planos ativos (um para cada paciente)
   • Metas específicas para cada plano
   • Período de 90-120 dias

🎯 Metas Terapêuticas:
   • Comunicação Verbal
   • Interação Social
   • Autonomia Pessoal
   • Controle Comportamental
   • Desenvolvimento da Fala
   • Compreensão de Instruções
""")

def show_next_steps():
    """Exibe próximos passos"""
    print("""
🎯 PRÓXIMOS PASSOS:

1. ✅ Sistema inicializado com sucesso
2. 🌐 Acesse: http://localhost:5000/api/
3. 🔐 Faça login com as credenciais fornecidas
4. 📝 Teste as funcionalidades da API
5. 🚀 Desenvolva novas features usando os dados de exemplo

💡 DICAS:
   • Use o Swagger UI para testar endpoints
   • Verifique os logs para debug
   • Os dados são recriados a cada inicialização
   • Use reset_db.py para limpar dados quando necessário
""")

def main():
    """Função principal"""
    print_banner()
    
    while True:
        show_menu()
        
        try:
            choice = input("Escolha uma opção (1-8): ").strip()
            
            if choice == '1':
                print("\n🐳 Iniciando com Docker...")
                print("Execute: docker-compose up --build")
                print("Isso irá:")
                print("  • Criar containers do banco e aplicação")
                print("  • Executar migrations automaticamente")
                print("  • Popular dados iniciais")
                print("  • Iniciar a aplicação Flask")
                
            elif choice == '2':
                print("\n💻 Iniciando desenvolvimento local...")
                print("Execute: python start_dev.py")
                print("Isso irá:")
                print("  • Verificar dependências")
                print("  • Conectar ao PostgreSQL")
                print("  • Executar migrations")
                print("  • Popular dados iniciais")
                print("  • Iniciar aplicação Flask")
                
            elif choice == '3':
                print("\n🔄 Resetando banco de dados...")
                print("Execute: python reset_db.py")
                print("⚠️ ATENÇÃO: Isso remove TODOS os dados!")
                
            elif choice == '4':
                print("\n🌱 Executando seed data...")
                print("Execute: python src/database/seed_data.py")
                
            elif choice == '5':
                print("\n📦 Executando migrations...")
                print("Execute: alembic upgrade head")
                
            elif choice == '6':
                print("\n🔍 Verificando banco...")
                print("Execute: python -c \"from src.main import app; print('✅ Banco OK')\"")
                
            elif choice == '7':
                print("\n📖 Documentação da API:")
                print("URL: http://localhost:5000/api/")
                print("Swagger UI disponível para testar endpoints")
                
            elif choice == '8':
                print("\n👋 Até logo!")
                break
                
            else:
                print("\n❌ Opção inválida!")
                
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                input("\nPressione Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main()
