#!/usr/bin/env python3
"""
Script para iniciar o ambiente de desenvolvimento local
"""
import os
import sys
import subprocess
import time

def check_requirements():
    """Verifica se os requirements estão instalados"""
    print("🔍 Verificando dependências...")
    
    try:
        import flask
        import flask_sqlalchemy
        import psycopg2
        print("✅ Dependências Python OK")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False

def check_postgres():
    """Verifica se o PostgreSQL está rodando"""
    print("🔍 Verificando PostgreSQL...")
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="aba_user",
            password="aba_pass123",
            database="aba_postgres"
        )
        conn.close()
        print("✅ PostgreSQL OK")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL não disponível: {e}")
        print("💡 Execute: docker-compose up db")
        return False

def setup_environment():
    """Configura variáveis de ambiente"""
    print("⚙️ Configurando ambiente...")
    
    env_vars = {
        'DB_USER': 'aba_user',
        'DB_PASS': 'aba_pass123',
        'DB_NAME': 'aba_postgres',
        'DB_HOST': 'localhost',
        'SECRET_KEY': 'dev_secret_key_123'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"   {key}={value}")
    
    print("✅ Ambiente configurado")

def run_migrations():
    """Executa migrations"""
    print("📦 Executando migrations...")
    
    try:
        result = subprocess.run([
            'alembic', 'upgrade', 'head'
        ], capture_output=True, text=True, check=True)
        
        print("✅ Migrations OK")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro nas migrations: {e}")
        return False

def run_seed_data():
    """Executa seed data"""
    print("🌱 Executando seed data...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.database.seed_data import create_seed_data
        from src.main import app
        
        with app.app_context():
            create_seed_data()
        
        print("✅ Seed data OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro no seed data: {e}")
        return False

def start_app():
    """Inicia a aplicação Flask"""
    print("🚀 Iniciando aplicação Flask...")
    
    try:
        subprocess.run([sys.executable, 'src/main.py'])
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")

def main():
    """Função principal"""
    print("🎯 Iniciando ambiente de desenvolvimento...")
    
    # Verificar dependências
    if not check_requirements():
        return
    
    # Verificar PostgreSQL
    if not check_postgres():
        return
    
    # Configurar ambiente
    setup_environment()
    
    # Executar migrations
    if not run_migrations():
        print("⚠️ Migrations falharam, mas continuando...")
    
    # Executar seed data
    if not run_seed_data():
        print("⚠️ Seed data falhou, mas continuando...")
    
    # Iniciar aplicação
    start_app()

if __name__ == "__main__":
    main()
