# Guia de Campos para Frontend - Checklist de Edição

## Estrutura Principal

```json
{
  "checklist": { ... },
  "perguntas": [ ... ]
}
```

## Campos do Checklist

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `id` | number | Sim | ID único do checklist |
| `meta_id` | number | Sim | ID da meta terapêutica |
| `meta_descricao` | string | Não | Descrição da meta (para exibição) |
| `data` | string | Sim | Data do checklist (formato ISO: YYYY-MM-DD) |
| `nota` | number | Não | Nota geral do checklist (1-10) |
| `observacao` | string | Não | Observações adicionais |

## Campos das Perguntas

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `id` | number | Sim | ID único da pergunta |
| `texto` | string | Sim | Texto da pergunta |
| `tipo` | string | Sim | Tipo da pergunta (ver tipos abaixo) |
| `obrigatoria` | boolean | Sim | Se a pergunta é obrigatória |
| `ordem` | number | Sim | Ordem de exibição |
| `formula` | string | Não | Fórmula para cálculo (apenas tipo FORMULA) |
| `resposta_atual` | string | Não | Resposta atual do usuário |
| `resposta_calculada` | string | Não | Resultado da fórmula (apenas tipo FORMULA) |

## Tipos de Pergunta

### 1. NUMERO
- **Campo de entrada**: Input numérico
- **Validação**: Apenas números
- **Exemplo**: "Como você está se sentindo hoje? (1-10)"

### 2. TEXTO
- **Campo de entrada**: Textarea ou input de texto
- **Validação**: Texto livre
- **Exemplo**: "Descreva como foi seu dia"

### 3. BOOLEANO
- **Campo de entrada**: Checkbox ou radio buttons (Sim/Não)
- **Validação**: Apenas "Sim" ou "Não"
- **Exemplo**: "Você praticou exercícios hoje?"

### 4. MULTIPLA
- **Campo de entrada**: Select dropdown ou radio buttons
- **Validação**: Uma das opções predefinidas
- **Exemplo**: "Qual seu humor predominante hoje?"

### 5. FORMULA
- **Campo de entrada**: Nenhum (calculado automaticamente)
- **Validação**: Não aplicável
- **Exemplo**: "Índice de Bem-estar Geral"
- **Comportamento**: 
  - Não deve permitir entrada manual
  - Mostrar resultado calculado
  - Atualizar automaticamente quando outras perguntas mudam

## Regras de Validação

1. **Perguntas obrigatórias**: Devem ser respondidas antes de salvar
2. **Perguntas FORMULA**: Não precisam ser respondidas manualmente
3. **Ordem**: Exibir perguntas na ordem definida pelo campo `ordem`
4. **Cálculo de fórmulas**: Atualizar automaticamente quando perguntas numéricas mudam

## Exemplo de Payload para Atualização

```json
{
  "nota": 8,
  "observacao": "Dia produtivo",
  "respostas": {
    "1": "7",    // pergunta_id: resposta
    "2": "8",
    "3": "6",
    "4": "Sim",
    "5": "Meditação, caminhada"
  }
}
```

## Notas Importantes

- Perguntas do tipo FORMULA não devem aparecer no payload de envio
- O campo `resposta_calculada` é preenchido automaticamente pelo backend
- Validar perguntas obrigatórias antes de permitir salvamento
- Atualizar fórmulas em tempo real conforme o usuário digita
