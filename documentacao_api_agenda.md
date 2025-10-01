# Documentação da API de Agenda

## Visão Geral

A API de Agenda permite gerenciar agendamentos entre pacientes e profissionais, incluindo funcionalidades de CRUD completo e consultas por período.

## Modelo de Dados

### Agenda
- `id`: Identificador único (Integer, Primary Key)
- `data_hora`: Data e hora do agendamento (DateTime, obrigatório)
- `duracao_minutos`: Duração em minutos (Integer, padrão: 60)
- `observacoes`: Observações sobre o agendamento (Text, opcional)
- `status`: Status do agendamento (Enum: Agendado, Confirmado, Cancelado, Realizado, Faltou)
- `presente`: Presença do paciente (Boolean, opcional: true = presente, false = ausente, null = não informado)
- `paciente_id`: ID do paciente (Integer, Foreign Key)
- `profissional_id`: ID do profissional (Integer, Foreign Key)

### Status do Agendamento
- `AGENDADO`: Agendamento criado, aguardando confirmação
- `CONFIRMADO`: Agendamento confirmado pelo paciente/profissional
- `CANCELADO`: Agendamento cancelado
- `REALIZADO`: Sessão realizada com sucesso
- `FALTOU`: Paciente não compareceu

## Endpoints

### 1. Listar Agendamentos
**GET** `/api/agenda`

Lista todos os agendamentos com filtros opcionais.

#### Parâmetros de Query (opcionais):
- `profissional_id`: Filtrar por profissional
- `paciente_id`: Filtrar por paciente
- `status`: Filtrar por status
- `data_inicio`: Data de início (YYYY-MM-DD)
- `data_fim`: Data de fim (YYYY-MM-DD)

#### Exemplo de Resposta:
```json
[
  {
    "id": 1,
    "data_hora": "2024-01-15T14:00:00",
    "duracao_minutos": 60,
    "observacoes": "Primeira sessão",
    "status": "AGENDADO",
    "presente": null,
    "paciente_id": 1,
    "profissional_id": 1,
    "paciente": {
      "id": 1,
      "nome": "João Silva"
    },
    "profissional": {
      "id": 1,
      "nome": "Dr. Maria Santos",
      "especialidade": "Psicologia"
    }
  }
]
```

### 2. Obter Agendamento por ID
**GET** `/api/agenda/{agenda_id}`

Retorna um agendamento específico.

### 3. Criar Agendamento
**POST** `/api/agenda`

Cria um novo agendamento.

#### Corpo da Requisição:
```json
{
  "data_hora": "2024-01-15T14:00:00",
  "duracao_minutos": 60,
  "observacoes": "Primeira sessão",
  "status": "AGENDADO",
  "presente": null,
  "paciente_id": 1,
  "profissional_id": 1
}
```

#### Validações:
- `data_hora`, `paciente_id` e `profissional_id` são obrigatórios
- Verifica se paciente e profissional existem
- Verifica conflitos de horário para o profissional
- `duracao_minutos` deve ser maior que zero

### 4. Atualizar Agendamento
**PUT** `/api/agenda/{agenda_id}`

Atualiza um agendamento existente.

#### Corpo da Requisição:
```json
{
  "data_hora": "2024-01-15T15:00:00",
  "duracao_minutos": 90,
  "observacoes": "Sessão estendida",
  "status": "CONFIRMADO",
  "presente": true
}
```

### 5. Deletar Agendamento
**DELETE** `/api/agenda/{agenda_id}`

Remove um agendamento.

### 6. Agendamentos por Mês
**GET** `/api/agenda/mes/{ano}/{mes}`

Lista agendamentos de um mês específico.

#### Parâmetros de Query (opcionais):
- `profissional_id`: Filtrar por profissional
- `paciente_id`: Filtrar por paciente

#### Exemplo:
```
GET /api/agenda/mes/2024/1?profissional_id=1
```

### 7. Agendamentos por Dia
**GET** `/api/agenda/dia/{data}`

Lista agendamentos de um dia específico.

#### Parâmetros:
- `data`: Data no formato YYYY-MM-DD

#### Parâmetros de Query (opcionais):
- `profissional_id`: Filtrar por profissional
- `paciente_id`: Filtrar por paciente

#### Exemplo:
```
GET /api/agenda/dia/2024-01-15?profissional_id=1
```

### 8. Atualizar Presença
**PATCH** `/api/agenda/{agenda_id}/presenca`

Atualiza apenas a presença de um agendamento.

#### Corpo da Requisição:
```json
{
  "presente": true
}
```

#### Valores possíveis:
- `true`: Paciente presente
- `false`: Paciente ausente
- `null`: Não informado

### 9. Atualizar Status
**PATCH** `/api/agenda/{agenda_id}/status`

Atualiza apenas o status de um agendamento.

#### Corpo da Requisição:
```json
{
  "status": "CONFIRMADO"
}
```

## Códigos de Status HTTP

- `200`: Sucesso
- `201`: Criado com sucesso
- `400`: Erro de validação
- `404`: Recurso não encontrado
- `500`: Erro interno do servidor

## Exemplos de Uso

### Criar um agendamento:
```bash
curl -X POST http://localhost:5000/api/agenda \
  -H "Content-Type: application/json" \
  -d '{
    "data_hora": "2024-01-15T14:00:00",
    "duracao_minutos": 60,
    "observacoes": "Primeira sessão",
    "paciente_id": 1,
    "profissional_id": 1
  }'
```

### Listar agendamentos de um mês:
```bash
curl "http://localhost:5000/api/agenda/mes/2024/1?profissional_id=1"
```

### Atualizar presença de um agendamento:
```bash
curl -X PATCH http://localhost:5000/api/agenda/1/presenca \
  -H "Content-Type: application/json" \
  -d '{"presente": true}'
```

### Atualizar status de um agendamento:
```bash
curl -X PATCH http://localhost:5000/api/agenda/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "CONFIRMADO"}'
```

## Funcionalidades Especiais

### Verificação de Conflitos
O sistema verifica automaticamente conflitos de horário para o mesmo profissional, impedindo agendamentos sobrepostos.

### Filtros Avançados
- Por período (data_inicio/data_fim)
- Por profissional
- Por paciente
- Por status

### Relacionamentos
Cada agendamento inclui informações do paciente e profissional relacionados, facilitando a exibição no frontend.

## Migração do Banco de Dados

Para aplicar as mudanças no banco de dados:

```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Aplicar migração
python -m alembic upgrade head
```

## Estrutura da Tabela

```sql
CREATE TABLE agenda (
    id SERIAL PRIMARY KEY,
    data_hora TIMESTAMP NOT NULL,
    duracao_minutos INTEGER NOT NULL DEFAULT 60,
    observacoes TEXT,
    status statusagendamentoenum NOT NULL DEFAULT 'AGENDADO',
    presente BOOLEAN,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id),
    profissional_id INTEGER NOT NULL REFERENCES profissionais(id)
);

-- Índices para performance
CREATE INDEX idx_agenda_data_hora ON agenda(data_hora);
CREATE INDEX idx_agenda_paciente ON agenda(paciente_id);
CREATE INDEX idx_agenda_profissional ON agenda(profissional_id);
CREATE INDEX idx_agenda_status ON agenda(status);
```
