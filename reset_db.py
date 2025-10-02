#!/usr/bin/env python3
"""
Script para resetar o banco de dados (remover todos os dados)
"""
import os
import sys

def reset_database():
    """Remove todos os dados do banco"""
    print("🗑️ Resetando banco de dados...")
    
    try:
        # Adicionar diretório src ao path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.database.seed_data import clear_all_data
        from src.main import app
        
        with app.app_context():
            clear_all_data()
        
        print("✅ Banco resetado com sucesso!")
        print("💡 Execute 'python start_dev.py' para recriar os dados")
        
    except Exception as e:
        print(f"❌ Erro ao resetar banco: {e}")

def main():
    """Função principal"""
    print("⚠️ ATENÇÃO: Isso irá remover TODOS os dados do banco!")
    
    response = input("Tem certeza? Digite 'SIM' para confirmar: ")
    
    if response.upper() == 'SIM':
        reset_database()
    else:
        print("❌ Operação cancelada")

if __name__ == "__main__":
    main()
