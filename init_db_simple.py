#!/usr/bin/env python3
"""
Script de inicialização simplificado do banco de dados para Docker
"""
import os
import sys
import time
import subprocess

def wait_for_database():
    """Aguarda o banco de dados estar disponível usando pg_isready"""
    print("🔄 Aguardando banco de dados estar disponível...")
    
    # Configurações do banco
    DB_USER = os.environ.get('DB_USER', 'aba_user')
    DB_PASS = os.environ.get('DB_PASS', 'aba_pass123')
    DB_NAME = os.environ.get('DB_NAME', 'aba_postgres')
    DB_HOST = os.environ.get('DB_HOST', 'db')
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            # Usar pg_isready para verificar se o banco está disponível
            result = subprocess.run([
                'pg_isready',
                '-h', DB_HOST,
                '-p', '5432',
                '-U', DB_USER,
                '-d', DB_NAME
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ Banco de dados está disponível!")
                return True
            else:
                print(f"⏳ Tentativa {attempt + 1}/{max_attempts} - Banco ainda não disponível...")
                
        except Exception as e:
            print(f"⏳ Tentativa {attempt + 1}/{max_attempts} - Erro: {str(e)[:50]}...")
        
        attempt += 1
        time.sleep(2)
    
    print("❌ Timeout: Banco de dados não ficou disponível")
    return False

def run_migrations():
    """Executa migrations do Alembic"""
    print("📦 Executando migrations...")
    
    try:
        # Executar alembic upgrade
        result = subprocess.run([
            'alembic', 'upgrade', 'head'
        ], capture_output=True, text=True, check=True)
        
        print("✅ Migrations executadas com sucesso!")
        if result.stdout.strip():
            print(f"Output: {result.stdout.strip()}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar migrations: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def run_seed_data():
    """Executa seed data"""
    print("🌱 Executando seed data...")
    
    try:
        # Adicionar diretório src ao path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.database.seed_data import create_seed_data
        from src.main import app
        
        with app.app_context():
            create_seed_data()
        
        print("✅ Seed data executado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar seed data: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal de inicialização"""
    print("🚀 Iniciando inicialização do banco de dados...")
    
    # Aguardar banco estar disponível
    if not wait_for_database():
        print("❌ Falha na inicialização: banco não disponível")
        sys.exit(1)
    
    # Executar migrations
    if not run_migrations():
        print("⚠️ Migrations falharam, mas continuando...")
    
    # Executar seed data
    if not run_seed_data():
        print("⚠️ Seed data falhou, mas continuando...")
    
    print("🎉 Inicialização do banco concluída!")
    print("\n📋 Próximos passos:")
    print("   1. Inicie a aplicação Flask")
    print("   2. Acesse a documentação da API em /api/")
    print("   3. Use as credenciais criadas para fazer login")

if __name__ == "__main__":
    main()
