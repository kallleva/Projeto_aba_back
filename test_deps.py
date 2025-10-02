#!/usr/bin/env python3
"""
Script para testar se todas as dependências estão instaladas corretamente
"""
import sys

def test_imports():
    """Testa se todas as dependências podem ser importadas"""
    print("🔍 Testando dependências...")
    
    dependencies = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('flask_cors', 'Flask-CORS'),
        ('psycopg2', 'psycopg2-binary'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('alembic', 'Alembic'),
        ('flasgger', 'Flasgger'),
        ('werkzeug', 'Werkzeug'),
        ('jinja2', 'Jinja2'),
        ('click', 'Click'),
        ('blinker', 'Blinker'),
        ('itsdangerous', 'ItsDangerous'),
        ('markupsafe', 'MarkupSafe'),
        ('greenlet', 'Greenlet'),
        ('typing_extensions', 'typing-extensions'),
        ('charset_normalizer', 'charset-normalizer'),
        ('et_xmlfile', 'et-xmlfile'),
        ('openpyxl', 'openpyxl'),
        ('pillow', 'Pillow'),
        ('pyjwt', 'PyJWT'),
        ('reportlab', 'ReportLab')
    ]
    
    failed = []
    
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError as e:
            print(f"❌ {package_name}: {e}")
            failed.append(package_name)
    
    if failed:
        print(f"\n❌ {len(failed)} dependências falharam:")
        for dep in failed:
            print(f"   • {dep}")
        return False
    else:
        print(f"\n✅ Todas as {len(dependencies)} dependências estão OK!")
        return True

def test_database_connection():
    """Testa conexão com banco de dados"""
    print("\n🔍 Testando conexão com banco de dados...")
    
    try:
        import psycopg2
        import os
        
        DB_USER = os.environ.get('DB_USER', 'aba_user')
        DB_PASS = os.environ.get('DB_PASS', 'aba_pass123')
        DB_NAME = os.environ.get('DB_NAME', 'aba_postgres')
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        
        conn = psycopg2.connect(
            host=DB_HOST,
            port=5432,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        conn.close()
        print("✅ Conexão com banco OK!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Testando ambiente de desenvolvimento...")
    
    # Testar imports
    deps_ok = test_imports()
    
    # Testar conexão com banco (opcional)
    db_ok = test_database_connection()
    
    print("\n📊 Resumo dos testes:")
    print(f"   Dependências: {'✅ OK' if deps_ok else '❌ FALHOU'}")
    print(f"   Banco de dados: {'✅ OK' if db_ok else '❌ FALHOU'}")
    
    if deps_ok and db_ok:
        print("\n🎉 Ambiente está pronto para desenvolvimento!")
    elif deps_ok:
        print("\n⚠️ Dependências OK, mas banco não disponível")
        print("💡 Execute: docker-compose up db")
    else:
        print("\n❌ Problemas encontrados")
        print("💡 Execute: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
