# Documentação dos Relatórios com Fórmulas Calculadas

## Visão Geral

Os relatórios agora incluem dados das fórmulas calculadas automaticamente. As fórmulas são perguntas do tipo `FORMULA` que calculam valores baseados em outras respostas do checklist.

## Estrutura das Fórmulas

### Tipos de Pergunta
- `TEXTO`: Resposta em texto livre
- `NUMERO`: Resposta numérica
- `BOOLEANO`: Resposta sim/não
- `MULTIPLA`: Resposta de múltipla escolha
- `FORMULA`: **Pergunta que calcula valor baseado em outras respostas**

### Formato das Fórmulas
As fórmulas usam referências `{pergunta_id}` para outras perguntas:
```
Exemplo: ({1} + {2} + {3}) / 3
- {1}: Referência à pergunta com ID 1
- {2}: Referência à pergunta com ID 2  
- {3}: Referência à pergunta com ID 3
```

## Endpoints dos Relatórios

### 1. Dashboard Geral
**GET** `/relatorios/dashboard`

**Resposta:**
```json
{
  "resumo": {
    "total_pacientes": 25,
    "total_profissionais": 5,
    "total_metas_ativas": 15,
    "registros_hoje": 8
  },
  "distribuicao_diagnosticos": [
    {"diagnostico": "TEA", "count": 10},
    {"diagnostico": "TDAH", "count": 8}
  ],
  "distribuicao_metas": [
    {"status": "Em_Andamento", "count": 15},
    {"status": "Concluida", "count": 5}
  ]
}
```

### 2. Evolução de Meta (COM FÓRMULAS)
**GET** `/relatorios/evolucao-meta/{meta_id}?data_inicio=2024-01-01&data_fim=2024-01-31`

**Resposta:**
```json
{
  "evolucao": [
    {
      "data": "2024-01-15",
      "nota": 8,
      "observacao": "Bom progresso",
      "formulas_calculadas": [
        {
          "pergunta_id": 5,
          "pergunta_texto": "Índice de coordenação",
          "formula": "({1} + {2} + {3}) / 3",
          "valor_calculado": "7.5",
          "valor_numerico": 7.5
        },
        {
          "pergunta_id": 6,
          "pergunta_texto": "Nível de autonomia",
          "formula": "({4} * 0.6) + ({5} * 0.4)",
          "valor_calculado": "8.2",
          "valor_numerico": 8.2
        }
      ]
    }
  ],
  "estatisticas": {
    "total_registros": 15,
    "nota_media": 7.8,
    "nota_maxima": 10,
    "nota_minima": 5,
    "tendencia": "crescente"
  }
}
```

### 3. Relatório de Paciente (COM FÓRMULAS)
**GET** `/relatorios/paciente/{paciente_id}`

**Resposta:**
```json
{
  "paciente": {
    "id": 1,
    "nome": "João Silva",
    "diagnostico": "TEA"
  },
  "resumo": {
    "total_planos": 2,
    "total_metas": 5,
    "metas_ativas": 3,
    "metas_concluidas": 2,
    "registros_ultimos_30_dias": 12,
    "media_notas_recentes": 7.5
  },
  "evolucao_por_meta": {
    "1": {
      "meta_descricao": "Melhorar coordenação motora",
      "registros": [
        {
          "data": "2024-01-15",
          "nota": 8,
          "formulas_calculadas": [
            {
              "pergunta_id": 5,
              "pergunta_texto": "Índice de coordenação",
              "formula": "({1} + {2} + {3}) / 3",
              "valor_calculado": "7.5",
              "valor_numerico": 7.5
            }
          ]
        }
      ]
    }
  }
}
```

### 4. Relatório de Período (COM FÓRMULAS)
**GET** `/relatorios/periodo?data_inicio=2024-01-01&data_fim=2024-01-31`

**Resposta:**
```json
{
  "periodo": {
    "data_inicio": "2024-01-01",
    "data_fim": "2024-01-31"
  },
  "evolucao_diaria": [
    {
      "data": "2024-01-15",
      "media_notas": 7.8,
      "total_registros": 5,
      "formulas_calculadas": [
        {
          "pergunta_id": 5,
          "pergunta_texto": "Índice de coordenação",
          "formula": "({1} + {2} + {3}) / 3",
          "valor_calculado": "7.5",
          "valor_numerico": 7.5
        }
      ]
    }
  ],
  "estatisticas": {
    "total_registros": 45,
    "media_geral": 7.5,
    "nota_maxima": 10,
    "nota_minima": 4
  }
}
```

## Novos Endpoints Específicos para Fórmulas

### 5. Relatório de Fórmulas por Meta
**GET** `/relatorios/formulas/{meta_id}?data_inicio=2024-01-01&data_fim=2024-01-31`

**Resposta:**
```json
{
  "meta_id": 1,
  "meta_descricao": "Melhorar coordenação motora",
  "formulas_calculadas": [
    {
      "pergunta_id": 5,
      "pergunta_texto": "Índice de coordenação",
      "formula": "({1} + {2} + {3}) / 3",
      "valores_calculados": [
        {
          "data": "2024-01-15",
          "valor_calculado": "7.5",
          "valor_numerico": 7.5,
          "checklist_id": 10
        },
        {
          "data": "2024-01-20",
          "valor_calculado": "8.2",
          "valor_numerico": 8.2,
          "checklist_id": 15
        }
      ]
    }
  ],
  "estatisticas_formulas": {
    "total_formulas": 2,
    "formulas_com_dados": 2,
    "media_por_formula": [
      {
        "pergunta_id": 5,
        "media_valor": 7.85,
        "total_registros": 2
      }
    ]
  }
}
```

### 6. Evolução de Fórmula Específica
**GET** `/relatorios/formulas/evolucao/{pergunta_id}?data_inicio=2024-01-01&data_fim=2024-01-31`

**Resposta:**
```json
{
  "pergunta": {
    "id": 5,
    "texto": "Índice de coordenação",
    "tipo": "FORMULA",
    "formula": "({1} + {2} + {3}) / 3"
  },
  "evolucao": [
    {
      "data": "2024-01-15",
      "valor_calculado": "7.5",
      "valor_numerico": 7.5,
      "checklist_id": 10,
      "meta_id": 1,
      "meta_descricao": "Melhorar coordenação motora"
    }
  ],
  "estatisticas": {
    "total_registros": 5,
    "formula": "({1} + {2} + {3}) / 3",
    "pergunta_texto": "Índice de coordenação",
    "media": 7.8,
    "maximo": 9.0,
    "minimo": 6.5,
    "tendencia": "crescente"
  }
}
```

### 7. Fórmulas de Checklist Específico
**GET** `/checklists-diarios/{checklist_id}/formulas`

**Resposta:**
```json
{
  "checklist_id": 10,
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
      "resposta_id": 25
    }
  ],
  "total_formulas": 1
}
```

### 8. Fórmulas de Meta (Checklist Diário)
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
          "checklist_id": 10
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

## Estrutura dos Dados das Fórmulas

### Objeto Formula Calculada
```typescript
interface FormulaCalculada {
  pergunta_id: number;
  pergunta_texto: string;
  formula: string;
  valor_calculado: string;
  // Pode ser null se não foi possível converter para número
  valor_numerico?: number;
}
```

### Objeto Evolução de Fórmula
```typescript
interface EvolucaoFormula {
  data: string; // ISO format
  valor_calculado: string;
  valor_numerico?: number;
  checklist_id: number;
  meta_id?: number;
  meta_descricao?: string;
}
```

## Implementação no Frontend

### 1. Exibição de Fórmulas nos Relatórios
```javascript
// Exemplo de como exibir fórmulas em um gráfico
const evolucaoData = response.evolucao.map(item => ({
  data: item.data,
  nota: item.nota,
  formulas: item.formulas_calculadas.map(f => ({
    nome: f.pergunta_texto,
    valor: f.valor_numerico,
    formula: f.formula
  }))
}));
```

### 2. Gráficos de Evolução de Fórmulas
```javascript
// Dados para gráfico de linha das fórmulas
const formulaChartData = response.formulas_calculadas.map(formula => ({
  name: formula.pergunta_texto,
  data: formula.valores_calculados.map(v => ({
    x: v.data,
    y: v.valor_numerico
  }))
}));
```

### 3. Estatísticas das Fórmulas
```javascript
// Exibir estatísticas
const estatisticas = response.estatisticas_formulas.media_por_formula.map(stat => ({
  pergunta: stat.pergunta_id,
  media: stat.media_valor,
  registros: stat.total_registros
}));
```

## Códigos de Status HTTP

- **200**: Sucesso
- **400**: Dados inválidos (ex: data_inicio/data_fim obrigatórios)
- **404**: Recurso não encontrado (meta, paciente, etc.)
- **500**: Erro interno do servidor

## Parâmetros de Query

### Filtros de Data (Opcionais)
- `data_inicio`: Data inicial no formato YYYY-MM-DD
- `data_fim`: Data final no formato YYYY-MM-DD

### Exemplo de Uso
```
GET /relatorios/formulas/1?data_inicio=2024-01-01&data_fim=2024-01-31
```

## Notas Importantes

1. **Fórmulas são calculadas automaticamente** quando um checklist é criado/atualizado
2. **valor_numerico** pode ser `null` se o resultado da fórmula não for numérico
3. **valor_calculado** sempre contém o resultado como string
4. **Fórmulas vazias** não aparecem nos relatórios
5. **Referências inválidas** em fórmulas resultam em erro no cálculo
6. **Datas** são sempre retornadas no formato ISO (YYYY-MM-DD)

## Exemplo de Integração Frontend

```javascript
// Função para buscar evolução de meta com fórmulas
async function buscarEvolucaoMeta(metaId, dataInicio, dataFim) {
  const params = new URLSearchParams();
  if (dataInicio) params.append('data_inicio', dataInicio);
  if (dataFim) params.append('data_fim', dataFim);
  
  const response = await fetch(`/relatorios/evolucao-meta/${metaId}?${params}`);
  const data = await response.json();
  
  // Processar dados para gráficos
  const chartData = data.evolucao.map(item => ({
    data: item.data,
    nota: item.nota,
    formulas: item.formulas_calculadas
  }));
  
  return chartData;
}
```
