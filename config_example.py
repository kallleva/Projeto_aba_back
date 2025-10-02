"""
Arquivo de exemplo de configuração
Copie este arquivo para config.py e ajuste as configurações
"""
import os

# Configurações do Banco de Dados
DB_USER = os.environ.get('DB_USER', 'aba_user')
DB_PASS = os.environ.get('DB_PASS', 'aba_pass123')
DB_NAME = os.environ.get('DB_NAME', 'aba_postgres')
DB_HOST = os.environ.get('DB_HOST', 'localhost')

# Configurações da Aplicação
SECRET_KEY = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui_123')
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

# Configurações do Docker
COMPOSE_PROJECT_NAME = os.environ.get('COMPOSE_PROJECT_NAME', 'aba_project')

# URLs de conexão
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

print(f"""
🔧 Configurações carregadas:
   DB_USER: {DB_USER}
   DB_HOST: {DB_HOST}
   DB_NAME: {DB_NAME}
   FLASK_ENV: {FLASK_ENV}
   FLASK_DEBUG: {FLASK_DEBUG}
""")
