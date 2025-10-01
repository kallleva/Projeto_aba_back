# Documentação da API - Checklist Diário

## Visão Geral

Esta documentação descreve como o frontend deve interagir com a API para criar, atualizar e consultar checklists diários, incluindo o salvamento de respostas e cálculo de fórmulas.

## Estrutura de Dados

### Checklist Diário
```typescript
interface ChecklistDiario {
  id: number;
  meta_id: number;
  meta_descricao: string;
  data: string; // YYYY-MM-DD
  nota: number;
  observacao: string;
  respostas: ChecklistResposta[];
  perguntas: Pergunta[];
}
```

### Resposta do Checklist
```typescript
interface ChecklistResposta {
  id: number;
  checklist_id: number;
  pergunta_id: number;
  resposta: string;
  resposta_calculada: string; // Para fórmulas
  pergunta: Pergunta;
  eh_formula: boolean;
}
```

### Pergunta
```typescript
interface Pergunta {
  id: number;
  texto: string;
  tipo: 'TEXTO' | 'NUMERO' | 'BOOLEANO' | 'MULTIPLA' | 'FORMULA';
  obrigatoria: boolean;
  ordem: number;
  formulario_id: number;
  formula: string; // Apenas para tipo FORMULA
}
```

## Endpoints da API

### 1. Listar Todos os Checklists
**GET** `/checklists-diarios`

**Resposta:**
```json
[
  {
    "id": 1,
    "meta_id": 1,
    "meta_descricao": "Melhorar coordenação motora",
    "data": "2024-01-15",
    "nota": 8,
    "observacao": "Bom progresso",
    "respostas": [
      {
        "id": 1,
        "pergunta_id": 1,
        "resposta": "Sim",
        "resposta_calculada": null,
        "eh_formula": false,
        "pergunta": {
          "id": 1,
          "texto": "Conseguiu realizar a atividade?",
          "tipo": "BOOLEANO",
          "obrigatoria": true
        }
      }
    ],
    "perguntas": [...]
  }
]
```

### 2. Obter Checklist Específico
**GET** `/checklists-diarios/{checklist_id}`

**Resposta:** Mesma estrutura do item acima, mas para um checklist específico.

### 3. Listar Checklists por Meta
**GET** `/checklists-diarios/meta/{meta_id}`

**Resposta:** Array de checklists da meta especificada.

### 4. Criar Checklist (IMPORTANTE)
**POST** `/checklists-diarios`

**Corpo da Requisição:**
```json
{
  "meta_id": 1,
  "data": "2024-01-15", // Opcional, usa data atual se não informado
  "nota": 8,
  "observacao": "Bom progresso",
  "respostas": {
    "1": "Sim",           // pergunta_id: resposta
    "2": "Não",
    "3": "8",
    "4": "Texto da resposta",
    "5": ""               // Pergunta fórmula - será calculada automaticamente
  }
}
```

**Resposta de Sucesso (201):**
```json
{
  "id": 1,
  "meta_id": 1,
  "meta_descricao": "Melhorar coordenação motora",
  "data": "2024-01-15",
  "nota": 8,
  "observacao": "Bom progresso",
  "respostas": [
    {
      "id": 1,
      "pergunta_id": 1,
      "resposta": "Sim",
      "resposta_calculada": null,
      "eh_formula": false,
      "pergunta": {...}
    },
    {
      "id": 2,
      "pergunta_id": 5,
      "resposta": "",
      "resposta_calculada": "7.5", // Fórmula calculada automaticamente
      "eh_formula": true,
      "pergunta": {
        "id": 5,
        "texto": "Índice de coordenação",
        "tipo": "FORMULA",
        "formula": "({1} + {2} + {3}) / 3"
      }
    }
  ],
  "perguntas": [...]
}
```

### 5. Atualizar Checklist
**PUT** `/checklists-diarios/{checklist_id}`

**Corpo da Requisição:**
```json
{
  "nota": 9,
  "observacao": "Excelente progresso",
  "respostas": {
    "1": "Sim",
    "2": "Sim", // Mudança de resposta
    "3": "9"    // Mudança de resposta
  }
}
```

**Resposta:** Checklist atualizado com a mesma estrutura do POST.

### 6. Deletar Checklist
**DELETE** `/checklists-diarios/{checklist_id}`

**Resposta:**
```json
{
  "mensagem": "Checklist diário deletado com sucesso"
}
```

## Endpoints de Fórmulas

### 7. Fórmulas de Checklist Específico
**GET** `/checklists-diarios/{checklist_id}/formulas`

**Resposta:**
```json
{
  "checklist_id": 1,
  "data": "2024-01-15",
  "meta_id": 1,
  "meta_descricao": "Melhorar coordenação motora",
  "formulas_calculadas": [
    {
      "pergunta_id": 5,
      "pergunta_texto": "Índice de coordenação",
      "formula": "({1} + {2} + {3}) / 3",
      "resposta_original": "",
      "valor_calculado": "7.5",
      "valor_numerico": 7.5,
      "resposta_id": 2
    }
  ],
  "total_formulas": 1
}
```

### 8. Fórmulas de Meta
**GET** `/checklists-diarios/meta/{meta_id}/formulas?data_inicio=2024-01-01&data_fim=2024-01-31`

**Resposta:**
```json
{
  "meta_id": 1,
  "meta_descricao": "Melhorar coordenação motora",
  "formulas_por_pergunta": [
    {
      "pergunta_id": 5,
      "pergunta_texto": "Índice de coordenação",
      "formula": "({1} + {2} + {3}) / 3",
      "valores": [
        {
          "data": "2024-01-15",
          "valor_calculado": "7.5",
          "valor_numerico": 7.5,
          "checklist_id": 1
        }
      ],
      "estatisticas": {
        "total_registros": 1,
        "media": 7.5,
        "maximo": 7.5,
        "minimo": 7.5
      }
    }
  ],
  "total_checklists": 5,
  "total_formulas": 1
}
```

## Como Enviar Dados do Frontend

### 1. Estrutura do Formulário
```javascript
// Exemplo de como estruturar os dados no frontend
const checklistData = {
  meta_id: 1,
  data: "2024-01-15", // Opcional
  nota: 8,
  observacao: "Bom progresso",
  respostas: {
    // Mapear pergunta_id para resposta
    "1": "Sim",           // Pergunta booleana
    "2": "Não",           // Pergunta booleana  
    "3": "8",             // Pergunta numérica
    "4": "Texto resposta", // Pergunta texto
    "5": ""                // Pergunta fórmula (vazia - será calculada)
  }
};
```

### 2. Validação no Frontend
```javascript
// Validar perguntas obrigatórias antes de enviar
function validarRespostas(perguntas, respostas) {
  const erros = [];
  
  perguntas.forEach(pergunta => {
    if (pergunta.obrigatoria && pergunta.tipo !== 'FORMULA') {
      const resposta = respostas[pergunta.id.toString()];
      if (!resposta || resposta.trim() === '') {
        erros.push(`Pergunta obrigatória não respondida: ${pergunta.texto}`);
      }
    }
  });
  
  return erros;
}
```

### 3. Envio para API
```javascript
// Função para criar checklist
async function criarChecklist(dados) {
  try {
    const response = await fetch('/checklists-diarios', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(dados)
    });
    
    if (!response.ok) {
      const erro = await response.json();
      throw new Error(erro.erro);
    }
    
    const checklist = await response.json();
    return checklist;
  } catch (error) {
    console.error('Erro ao criar checklist:', error);
    throw error;
  }
}
```

### 4. Atualização de Checklist
```javascript
// Função para atualizar checklist
async function atualizarChecklist(checklistId, dados) {
  try {
    const response = await fetch(`/checklists-diarios/${checklistId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(dados)
    });
    
    if (!response.ok) {
      const erro = await response.json();
      throw new Error(erro.erro);
    }
    
    const checklist = await response.json();
    return checklist;
  } catch (error) {
    console.error('Erro ao atualizar checklist:', error);
    throw error;
  }
}
```

## Códigos de Status HTTP

- **200**: Sucesso (GET, PUT)
- **201**: Criado com sucesso (POST)
- **400**: Dados inválidos
- **404**: Recurso não encontrado
- **500**: Erro interno do servidor

## Tratamento de Erros

### Erros Comuns

1. **Meta não encontrada (404)**
```json
{
  "erro": "Meta terapêutica não encontrada"
}
```

2. **Checklist já existe (400)**
```json
{
  "erro": "Já existe um checklist para esta meta nesta data"
}
```

3. **Perguntas obrigatórias não respondidas (400)**
```json
{
  "erro": "Perguntas obrigatórias não respondidas: Conseguiu realizar a atividade?, Qual foi a dificuldade?"
}
```

4. **Formato de data inválido (400)**
```json
{
  "erro": "Formato de data inválido. Use YYYY-MM-DD"
}
```

## Exemplo Completo de Uso

```javascript
// Exemplo completo de criação de checklist
async function exemploCompleto() {
  // 1. Buscar perguntas da meta
  const metaResponse = await fetch('/metas-terapeuticas/1');
  const meta = await metaResponse.json();
  
  // 2. Preparar dados do checklist
  const checklistData = {
    meta_id: 1,
    data: "2024-01-15",
    nota: 8,
    observacao: "Bom progresso",
    respostas: {
      "1": "Sim",      // Pergunta booleana
      "2": "Não",      // Pergunta booleana
      "3": "8",        // Pergunta numérica
      "4": "Texto",    // Pergunta texto
      "5": ""          // Pergunta fórmula (será calculada)
    }
  };
  
  // 3. Validar respostas obrigatórias
  const erros = validarRespostas(meta.formularios[0].perguntas, checklistData.respostas);
  if (erros.length > 0) {
    console.error('Erros de validação:', erros);
    return;
  }
  
  // 4. Enviar para API
  try {
    const checklist = await criarChecklist(checklistData);
    console.log('Checklist criado:', checklist);
    
    // 5. Verificar fórmulas calculadas
    if (checklist.respostas.some(r => r.eh_formula)) {
      console.log('Fórmulas calculadas:', 
        checklist.respostas.filter(r => r.eh_formula)
      );
    }
  } catch (error) {
    console.error('Erro ao criar checklist:', error);
  }
}
```

## Notas Importantes

1. **Fórmulas são calculadas automaticamente** - não envie valores para perguntas do tipo FORMULA
2. **Respostas são mapeadas por pergunta_id** - use string como chave no objeto respostas
3. **Validação obrigatória** - perguntas marcadas como obrigatórias devem ser respondidas
4. **Data opcional** - se não informada, usa a data atual
5. **Fórmulas vazias** - perguntas do tipo FORMULA devem ter resposta vazia no envio
6. **Recálculo automático** - fórmulas são recalculadas automaticamente na atualização

## Estrutura de Resposta das Fórmulas

```typescript
interface FormulaCalculada {
  pergunta_id: number;
  pergunta_texto: string;
  formula: string;
  valor_calculado: string;
  valor_numerico?: number; // null se não for numérico
}
```

Esta documentação deve ser suficiente para que seu frontend saiba exatamente como interagir com a API de checklists diários!
