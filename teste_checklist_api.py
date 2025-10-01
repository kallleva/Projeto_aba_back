#!/usr/bin/env python3
"""
Script de teste para verificar se as respostas dos checklists estão sendo salvas corretamente.
Execute este script para testar a API de checklists.
"""

import requests
import json
from datetime import date

# Configuração da API
BASE_URL = "http://localhost:5000"  # Ajuste conforme necessário

def testar_criacao_checklist():
    """Testa a criação de um checklist com respostas"""
    
    # Dados de teste
    dados_checklist = {
        "meta_id": 1,  # Ajuste para um ID de meta existente
        "data": date.today().isoformat(),
        "nota": 8,
        "observacao": "Teste de checklist",
        "respostas": {
            "1": "Sim",      # Pergunta booleana
            "2": "Não",      # Pergunta booleana  
            "3": "8",        # Pergunta numérica
            "4": "Resposta de texto",  # Pergunta texto
            "5": ""          # Pergunta fórmula (vazia)
        }
    }
    
    print("=== TESTE DE CRIAÇÃO DE CHECKLIST ===")
    print(f"Enviando dados: {json.dumps(dados_checklist, indent=2)}")
    
    try:
        # Fazer requisição POST
        response = requests.post(
            f"{BASE_URL}/checklists-diarios",
            json=dados_checklist,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            checklist_criado = response.json()
            print("✅ Checklist criado com sucesso!")
            print(f"ID do Checklist: {checklist_criado.get('id')}")
            print(f"Total de respostas: {len(checklist_criado.get('respostas', []))}")
            
            # Verificar respostas
            print("\n=== RESPOSTAS SALVAS ===")
            for resposta in checklist_criado.get('respostas', []):
                print(f"Pergunta ID: {resposta.get('pergunta_id')}")
                print(f"Resposta: '{resposta.get('resposta')}'")
                print(f"Resposta Calculada: '{resposta.get('resposta_calculada')}'")
                print(f"É Fórmula: {resposta.get('eh_formula')}")
                print("---")
            
            return checklist_criado.get('id')
            
        else:
            print("❌ Erro ao criar checklist")
            print(f"Resposta: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API")
        print("Certifique-se de que o servidor está rodando em http://localhost:5000")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def testar_buscar_checklist(checklist_id):
    """Testa a busca de um checklist específico"""
    
    print(f"\n=== TESTE DE BUSCA DE CHECKLIST {checklist_id} ===")
    
    try:
        response = requests.get(f"{BASE_URL}/checklists-diarios/{checklist_id}")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            checklist = response.json()
            print("✅ Checklist encontrado!")
            print(f"Total de respostas: {len(checklist.get('respostas', []))}")
            
            # Verificar se as respostas foram salvas
            print("\n=== VERIFICAÇÃO DAS RESPOSTAS ===")
            for resposta in checklist.get('respostas', []):
                print(f"Pergunta ID: {resposta.get('pergunta_id')}")
                print(f"Resposta: '{resposta.get('resposta')}'")
                print(f"Resposta Calculada: '{resposta.get('resposta_calculada')}'")
                print(f"É Fórmula: {resposta.get('eh_formula')}")
                print("---")
        else:
            print("❌ Erro ao buscar checklist")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def testar_listar_checklists():
    """Testa a listagem de todos os checklists"""
    
    print("\n=== TESTE DE LISTAGEM DE CHECKLISTS ===")
    
    try:
        response = requests.get(f"{BASE_URL}/checklists-diarios")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            checklists = response.json()
            print(f"✅ Encontrados {len(checklists)} checklists")
            
            for i, checklist in enumerate(checklists):
                print(f"Checklist {i+1}:")
                print(f"  ID: {checklist.get('id')}")
                print(f"  Meta: {checklist.get('meta_descricao')}")
                print(f"  Data: {checklist.get('data')}")
                print(f"  Respostas: {len(checklist.get('respostas', []))}")
                print("---")
        else:
            print("❌ Erro ao listar checklists")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def main():
    """Função principal de teste"""
    
    print("🧪 INICIANDO TESTES DA API DE CHECKLISTS")
    print("=" * 50)
    
    # Teste 1: Criar checklist
    checklist_id = testar_criacao_checklist()
    
    if checklist_id:
        # Teste 2: Buscar checklist criado
        testar_buscar_checklist(checklist_id)
    
    # Teste 3: Listar todos os checklists
    testar_listar_checklists()
    
    print("\n" + "=" * 50)
    print("🏁 TESTES CONCLUÍDOS")

if __name__ == "__main__":
    main()
