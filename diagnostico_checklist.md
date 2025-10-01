# Diagnóstico - Problemas com Salvamento de Respostas

## Possíveis Causas do Problema

### 1. **Problema de Relacionamento no Banco**
- Verificar se as foreign keys estão corretas
- Verificar se as tabelas existem
- Verificar se os relacionamentos estão configurados

### 2. **Problema na Criação das Respostas**
- Verificar se o loop está criando as respostas corretamente
- Verificar se as perguntas estão sendo encontradas
- Verificar se o `db.session.add()` está sendo chamado

### 3. **Problema de Commit**
- Verificar se o `db.session.commit()` está sendo executado
- Verificar se há rollback sendo chamado

## Como Diagnosticar

### 1. **Verificar Logs do Servidor**
```bash
# Executar o servidor com debug
python -m flask run --debug
```

### 2. **Testar com Script de Teste**
```bash
# Executar o script de teste
python teste_checklist_api.py
```

### 3. **Verificar Banco de Dados**
```sql
-- Verificar se as tabelas existem
SELECT * FROM checklists_diarios;
SELECT * FROM checklist_respostas;

-- Verificar relacionamentos
SELECT c.id, c.meta_id, c.data, cr.id as resposta_id, cr.pergunta_id, cr.resposta
FROM checklists_diarios c
LEFT JOIN checklist_respostas cr ON c.id = cr.checklist_id;
```

## Soluções Possíveis

### 1. **Verificar Imports**
Certifique-se de que todos os imports estão corretos:
```python
from src.models import db, ChecklistDiario, MetaTerapeutica, ChecklistResposta, Pergunta, TipoPerguntaEnum
```

### 2. **Verificar Relacionamentos**
No modelo `ChecklistDiario`, verificar:
```python
respostas = db.relationship('ChecklistResposta', back_populates='checklist', cascade='all, delete-orphan', lazy=True)
```

### 3. **Verificar Criação de Respostas**
No endpoint de criação, verificar se:
```python
# Adicionar respostas para todas as perguntas dos formulários vinculados
for formulario in meta.formularios:
    for pergunta in formulario.perguntas:
        resposta_texto = respostas_dict.get(str(pergunta.id), "")
        resposta_obj = ChecklistResposta(pergunta_id=pergunta.id, resposta=resposta_texto)
        
        # Calcular fórmula se for pergunta do tipo FORMULA
        if pergunta.tipo.value == 'FORMULA':
            resposta_calculada = resposta_obj.calcular_formula(respostas_dict)
            resposta_obj.resposta_calculada = resposta_calculada
        
        checklist.respostas.append(resposta_obj)
```

### 4. **Verificar Commit**
```python
db.session.add(checklist)
db.session.commit()  # Verificar se está sendo executado
```

## Teste Manual

### 1. **Criar Checklist via API**
```bash
curl -X POST http://localhost:5000/checklists-diarios \
  -H "Content-Type: application/json" \
  -d '{
    "meta_id": 1,
    "nota": 8,
    "observacao": "Teste",
    "respostas": {
      "1": "Sim",
      "2": "Não",
      "3": "8"
    }
  }'
```

### 2. **Verificar Resposta**
A resposta deve incluir as respostas criadas:
```json
{
  "id": 1,
  "meta_id": 1,
  "respostas": [
    {
      "id": 1,
      "pergunta_id": 1,
      "resposta": "Sim",
      "resposta_calculada": null,
      "eh_formula": false
    }
  ]
}
```

### 3. **Verificar Banco**
```sql
SELECT * FROM checklist_respostas WHERE checklist_id = 1;
```

## Código de Debug

Adicione logs para debug:

```python
# No endpoint de criação
print(f"Meta encontrada: {meta}")
print(f"Formulários da meta: {meta.formularios}")
print(f"Respostas recebidas: {respostas_dict}")

for formulario in meta.formularios:
    print(f"Formulário: {formulario.nome}")
    for pergunta in formulario.perguntas:
        print(f"Pergunta: {pergunta.texto} (ID: {pergunta.id})")
        resposta_texto = respostas_dict.get(str(pergunta.id), "")
        print(f"Resposta: '{resposta_texto}'")
        
        resposta_obj = ChecklistResposta(pergunta_id=pergunta.id, resposta=resposta_texto)
        print(f"Objeto resposta criado: {resposta_obj}")
        
        checklist.respostas.append(resposta_obj)
        print(f"Resposta adicionada ao checklist")

print(f"Total de respostas no checklist: {len(checklist.respostas)}")
```

## Verificações Importantes

1. **Meta tem formulários vinculados?**
2. **Formulários têm perguntas?**
3. **Respostas estão sendo criadas?**
4. **Commit está sendo executado?**
5. **Relacionamentos estão corretos?**

Execute o script de teste e verifique os logs para identificar onde está o problema!
