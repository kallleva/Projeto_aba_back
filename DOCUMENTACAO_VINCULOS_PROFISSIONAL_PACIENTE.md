# 📋 Documentação - Sistema de Vínculos Profissional-Paciente

## 🎯 Visão Geral

O sistema de vínculos permite que múltiplos profissionais atendam um paciente e que um profissional atenda múltiplos pacientes. Cada vínculo representa uma relação terapêutica específica com tipo de atendimento, frequência e configurações próprias.

## 📊 Estrutura do Banco de Dados

### Tabela: `profissional_paciente`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer | ID único do vínculo |
| `profissional_id` | Integer | ID do profissional (FK) |
| `paciente_id` | Integer | ID do paciente (FK) |
| `data_inicio` | Date | Data de início do atendimento |
| `data_fim` | Date | Data de fim do atendimento (opcional) |
| `status` | Enum | Status do vínculo (ATIVO, INATIVO, SUSPENSO) |
| `tipo_atendimento` | Enum | Tipo de terapia/atendimento |
| `frequencia_semanal` | Integer | Número de sessões por semana |
| `duracao_sessao` | Integer | Duração da sessão em minutos |
| `observacoes` | Text | Observações sobre o atendimento |
| `data_criacao` | Date | Data de criação do registro |
| `criado_por` | Integer | ID do usuário que criou (FK) |

### Enums Disponíveis

#### StatusVinculoEnum
- `ATIVO` - Vínculo ativo
- `INATIVO` - Vínculo encerrado
- `SUSPENSO` - Vínculo temporariamente suspenso

#### TipoAtendimentoEnum
- `Terapia ABA` - Análise do Comportamento Aplicada
- `Psicologia` - Atendimento psicológico
- `Fonoaudiologia` - Terapia da fala
- `Terapia Ocupacional` - Terapia ocupacional
- `Fisioterapia` - Fisioterapia
- `Psicopedagogia` - Psicopedagogia
- `Outro` - Outros tipos de atendimento

## 🔗 Endpoints da API

### 1. Listar Vínculos
```http
GET /api/vinculos
```

**Parâmetros de Query:**
- `status` (opcional): Filtrar por status (ATIVO, INATIVO, SUSPENSO)
- `profissional_id` (opcional): Filtrar por ID do profissional
- `paciente_id` (opcional): Filtrar por ID do paciente
- `tipo_atendimento` (opcional): Filtrar por tipo de atendimento

**Exemplo de Resposta:**
```json
[
  {
    "id": 1,
    "profissional": {
      "id": 1,
      "nome": "Dr. João Silva",
      "especialidade": "Terapia ABA",
      "email": "joao.silva@clinica.com",
      "telefone": "(11) 99999-1111"
    },
    "paciente": {
      "id": 1,
      "nome": "Ana Clara Oliveira",
      "data_nascimento": "2018-05-15",
      "idade": 6,
      "responsavel": "Carlos Oliveira",
      "contato": "(11) 99999-4444",
      "diagnostico": "TEA"
    },
    "data_inicio": "2024-09-02",
    "data_fim": null,
    "status": "ATIVO",
    "tipo_atendimento": "Terapia ABA",
    "frequencia_semanal": 3,
    "duracao_sessao": 60,
    "observacoes": "Paciente com boa evolução na comunicação",
    "data_criacao": "2024-10-02",
    "criado_por": 7
  }
]
```

### 2. Obter Vínculo Específico
```http
GET /api/vinculos/{vinculo_id}
```

**Exemplo de Resposta:**
```json
{
  "id": 1,
  "profissional": {
    "id": 1,
    "nome": "Dr. João Silva",
    "especialidade": "Terapia ABA",
    "email": "joao.silva@clinica.com",
    "telefone": "(11) 99999-1111"
  },
  "paciente": {
    "id": 1,
    "nome": "Ana Clara Oliveira",
    "data_nascimento": "2018-05-15",
    "idade": 6,
    "responsavel": "Carlos Oliveira",
    "contato": "(11) 99999-4444",
    "diagnostico": "TEA"
  },
  "data_inicio": "2024-09-02",
  "data_fim": null,
  "status": "ATIVO",
  "tipo_atendimento": "Terapia ABA",
  "frequencia_semanal": 3,
  "duracao_sessao": 60,
  "observacoes": "Paciente com boa evolução na comunicação",
  "data_criacao": "2024-10-02",
  "criado_por": 7
}
```

### 3. Criar Novo Vínculo
```http
POST /api/vinculos
```

**Payload de Exemplo:**
```json
{
  "profissional_id": 1,
  "paciente_id": 2,
  "tipo_atendimento": "Psicologia",
  "data_inicio": "2024-10-02",
  "frequencia_semanal": 2,
  "duracao_sessao": 45,
  "observacoes": "Foco em habilidades sociais e comunicação",
  "criado_por": 7
}
```

**Resposta de Sucesso (201):**
```json
{
  "id": 8,
  "profissional": {
    "id": 1,
    "nome": "Dr. João Silva",
    "especialidade": "Terapia ABA",
    "email": "joao.silva@clinica.com",
    "telefone": "(11) 99999-1111"
  },
  "paciente": {
    "id": 2,
    "nome": "Lucas Ferreira",
    "data_nascimento": "2017-08-22",
    "idade": 7,
    "responsavel": "Sandra Ferreira",
    "contato": "(11) 99999-5555",
    "diagnostico": "TEA"
  },
  "data_inicio": "2024-10-02",
  "data_fim": null,
  "status": "ATIVO",
  "tipo_atendimento": "Psicologia",
  "frequencia_semanal": 2,
  "duracao_sessao": 45,
  "observacoes": "Foco em habilidades sociais e comunicação",
  "data_criacao": "2024-10-02",
  "criado_por": 7
}
```

### 4. Atualizar Vínculo
```http
PUT /api/vinculos/{vinculo_id}
```

**Payload de Exemplo:**
```json
{
  "status": "SUSPENSO",
  "frequencia_semanal": 1,
  "observacoes": "Atendimento suspenso temporariamente por motivos familiares"
}
```

### 5. Ativar Vínculo
```http
POST /api/vinculos/{vinculo_id}/ativar
```

### 6. Inativar Vínculo
```http
POST /api/vinculos/{vinculo_id}/inativar
```

**Payload Opcional:**
```json
{
  "data_fim": "2024-12-31"
}
```

### 7. Suspender Vínculo
```http
POST /api/vinculos/{vinculo_id}/suspender
```

### 8. Listar Pacientes de um Profissional
```http
GET /api/profissionais/{profissional_id}/pacientes
```

**Parâmetros de Query:**
- `apenas_ativos` (opcional): true/false (padrão: true)

**Exemplo de Resposta:**
```json
[
  {
    "id": 1,
    "profissional": {
      "id": 1,
      "nome": "Dr. João Silva",
      "especialidade": "Terapia ABA",
      "email": "joao.silva@clinica.com",
      "telefone": "(11) 99999-1111"
    },
    "paciente": {
      "id": 1,
      "nome": "Ana Clara Oliveira",
      "data_nascimento": "2018-05-15",
      "idade": 6,
      "responsavel": "Carlos Oliveira",
      "contato": "(11) 99999-4444",
      "diagnostico": "TEA"
    },
    "data_inicio": "2024-09-02",
    "data_fim": null,
    "status": "ATIVO",
    "tipo_atendimento": "Terapia ABA",
    "frequencia_semanal": 3,
    "duracao_sessao": 60,
    "observacoes": "Paciente com boa evolução na comunicação",
    "data_criacao": "2024-10-02",
    "criado_por": 7
  },
  {
    "id": 5,
    "profissional": {
      "id": 1,
      "nome": "Dr. João Silva",
      "especialidade": "Terapia ABA",
      "email": "joao.silva@clinica.com",
      "telefone": "(11) 99999-1111"
    },
    "paciente": {
      "id": 3,
      "nome": "Sophia Rodrigues",
      "data_nascimento": "2019-03-10",
      "idade": 5,
      "responsavel": "Roberto Rodrigues",
      "contato": "(11) 99999-6666",
      "diagnostico": "TEA"
    },
    "data_inicio": "2024-09-22",
    "data_fim": null,
    "status": "ATIVO",
    "tipo_atendimento": "Terapia ABA",
    "frequencia_semanal": 4,
    "duracao_sessao": 45,
    "observacoes": "Paciente iniciante, adaptação ao ambiente",
    "data_criacao": "2024-10-02",
    "criado_por": 7
  }
]
```

### 9. Listar Profissionais de um Paciente
```http
GET /api/pacientes/{paciente_id}/profissionais
```

**Parâmetros de Query:**
- `apenas_ativos` (opcional): true/false (padrão: true)

**Exemplo de Resposta:**
```json
[
  {
    "id": 1,
    "profissional": {
      "id": 1,
      "nome": "Dr. João Silva",
      "especialidade": "Terapia ABA",
      "email": "joao.silva@clinica.com",
      "telefone": "(11) 99999-1111"
    },
    "paciente": {
      "id": 1,
      "nome": "Ana Clara Oliveira",
      "data_nascimento": "2018-05-15",
      "idade": 6,
      "responsavel": "Carlos Oliveira",
      "contato": "(11) 99999-4444",
      "diagnostico": "TEA"
    },
    "data_inicio": "2024-09-02",
    "data_fim": null,
    "status": "ATIVO",
    "tipo_atendimento": "Terapia ABA",
    "frequencia_semanal": 3,
    "duracao_sessao": 60,
    "observacoes": "Paciente com boa evolução na comunicação",
    "data_criacao": "2024-10-02",
    "criado_por": 7
  },
  {
    "id": 2,
    "profissional": {
      "id": 2,
      "nome": "Dra. Maria Santos",
      "especialidade": "Psicologia Comportamental",
      "email": "maria.santos@clinica.com",
      "telefone": "(11) 99999-2222"
    },
    "paciente": {
      "id": 1,
      "nome": "Ana Clara Oliveira",
      "data_nascimento": "2018-05-15",
      "idade": 6,
      "responsavel": "Carlos Oliveira",
      "contato": "(11) 99999-4444",
      "diagnostico": "TEA"
    },
    "data_inicio": "2024-09-12",
    "data_fim": null,
    "status": "ATIVO",
    "tipo_atendimento": "Psicologia",
    "frequencia_semanal": 2,
    "duracao_sessao": 45,
    "observacoes": "Trabalho focado em habilidades sociais",
    "data_criacao": "2024-10-02",
    "criado_por": 7
  }
]
```

## 🎨 Exemplos para Frontend

### 1. Componente de Lista de Vínculos

```javascript
// Buscar vínculos de um paciente
const fetchVinculosPaciente = async (pacienteId) => {
  try {
    const response = await fetch(`/api/pacientes/${pacienteId}/profissionais`);
    const vinculos = await response.json();
    return vinculos;
  } catch (error) {
    console.error('Erro ao buscar vínculos:', error);
  }
};

// Exemplo de uso no React
const VinculosPaciente = ({ pacienteId }) => {
  const [vinculos, setVinculos] = useState([]);
  
  useEffect(() => {
    fetchVinculosPaciente(pacienteId).then(setVinculos);
  }, [pacienteId]);
  
  return (
    <div className="vinculos-container">
      <h3>Profissionais Vinculados</h3>
      {vinculos.map(vinculo => (
        <div key={vinculo.id} className="vinculo-card">
          <h4>{vinculo.profissional.nome}</h4>
          <p><strong>Especialidade:</strong> {vinculo.profissional.especialidade}</p>
          <p><strong>Tipo de Atendimento:</strong> {vinculo.tipo_atendimento}</p>
          <p><strong>Frequência:</strong> {vinculo.frequencia_semanal}x por semana</p>
          <p><strong>Duração:</strong> {vinculo.duracao_sessao} minutos</p>
          <p><strong>Status:</strong> 
            <span className={`status ${vinculo.status.toLowerCase()}`}>
              {vinculo.status}
            </span>
          </p>
          {vinculo.observacoes && (
            <p><strong>Observações:</strong> {vinculo.observacoes}</p>
          )}
        </div>
      ))}
    </div>
  );
};
```

### 2. Formulário de Criação de Vínculo

```javascript
const FormularioVinculo = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    profissional_id: '',
    paciente_id: '',
    tipo_atendimento: '',
    data_inicio: new Date().toISOString().split('T')[0],
    frequencia_semanal: 1,
    duracao_sessao: 45,
    observacoes: ''
  });
  
  const tiposAtendimento = [
    'Terapia ABA',
    'Psicologia',
    'Fonoaudiologia',
    'Terapia Ocupacional',
    'Fisioterapia',
    'Psicopedagogia',
    'Outro'
  ];
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('/api/vinculos', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        const novoVinculo = await response.json();
        onSuccess(novoVinculo);
        // Reset form
        setFormData({
          profissional_id: '',
          paciente_id: '',
          tipo_atendimento: '',
          data_inicio: new Date().toISOString().split('T')[0],
          frequencia_semanal: 1,
          duracao_sessao: 45,
          observacoes: ''
        });
      } else {
        const error = await response.json();
        alert(`Erro: ${error.erro}`);
      }
    } catch (error) {
      console.error('Erro ao criar vínculo:', error);
      alert('Erro ao criar vínculo');
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="formulario-vinculo">
      <h3>Criar Novo Vínculo</h3>
      
      <div className="form-group">
        <label>Profissional:</label>
        <select 
          value={formData.profissional_id}
          onChange={(e) => setFormData({...formData, profissional_id: e.target.value})}
          required
        >
          <option value="">Selecione um profissional</option>
          {/* Carregar profissionais dinamicamente */}
        </select>
      </div>
      
      <div className="form-group">
        <label>Paciente:</label>
        <select 
          value={formData.paciente_id}
          onChange={(e) => setFormData({...formData, paciente_id: e.target.value})}
          required
        >
          <option value="">Selecione um paciente</option>
          {/* Carregar pacientes dinamicamente */}
        </select>
      </div>
      
      <div className="form-group">
        <label>Tipo de Atendimento:</label>
        <select 
          value={formData.tipo_atendimento}
          onChange={(e) => setFormData({...formData, tipo_atendimento: e.target.value})}
          required
        >
          <option value="">Selecione o tipo</option>
          {tiposAtendimento.map(tipo => (
            <option key={tipo} value={tipo}>{tipo}</option>
          ))}
        </select>
      </div>
      
      <div className="form-group">
        <label>Data de Início:</label>
        <input 
          type="date"
          value={formData.data_inicio}
          onChange={(e) => setFormData({...formData, data_inicio: e.target.value})}
          required
        />
      </div>
      
      <div className="form-row">
        <div className="form-group">
          <label>Frequência Semanal:</label>
          <input 
            type="number"
            min="1"
            max="7"
            value={formData.frequencia_semanal}
            onChange={(e) => setFormData({...formData, frequencia_semanal: parseInt(e.target.value)})}
          />
        </div>
        
        <div className="form-group">
          <label>Duração da Sessão (min):</label>
          <input 
            type="number"
            min="15"
            max="180"
            step="15"
            value={formData.duracao_sessao}
            onChange={(e) => setFormData({...formData, duracao_sessao: parseInt(e.target.value)})}
          />
        </div>
      </div>
      
      <div className="form-group">
        <label>Observações:</label>
        <textarea 
          value={formData.observacoes}
          onChange={(e) => setFormData({...formData, observacoes: e.target.value})}
          rows="3"
          placeholder="Observações sobre o atendimento..."
        />
      </div>
      
      <button type="submit" className="btn-primary">
        Criar Vínculo
      </button>
    </form>
  );
};
```

### 3. Dashboard de Profissional

```javascript
const DashboardProfissional = ({ profissionalId }) => {
  const [pacientes, setPacientes] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchPacientes = async () => {
      try {
        const response = await fetch(`/api/profissionais/${profissionalId}/pacientes`);
        const data = await response.json();
        setPacientes(data);
      } catch (error) {
        console.error('Erro ao carregar pacientes:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchPacientes();
  }, [profissionalId]);
  
  if (loading) return <div>Carregando...</div>;
  
  return (
    <div className="dashboard-profissional">
      <h2>Meus Pacientes</h2>
      
      <div className="estatisticas">
        <div className="stat-card">
          <h3>{pacientes.length}</h3>
          <p>Pacientes Ativos</p>
        </div>
        <div className="stat-card">
          <h3>{pacientes.reduce((sum, p) => sum + p.frequencia_semanal, 0)}</h3>
          <p>Sessões por Semana</p>
        </div>
      </div>
      
      <div className="pacientes-grid">
        {pacientes.map(vinculo => (
          <div key={vinculo.id} className="paciente-card">
            <h4>{vinculo.paciente.nome}</h4>
            <p><strong>Idade:</strong> {vinculo.paciente.idade} anos</p>
            <p><strong>Diagnóstico:</strong> {vinculo.paciente.diagnostico}</p>
            <p><strong>Tipo:</strong> {vinculo.tipo_atendimento}</p>
            <p><strong>Frequência:</strong> {vinculo.frequencia_semanal}x/semana</p>
            <p><strong>Duração:</strong> {vinculo.duracao_sessao}min</p>
            
            <div className="acoes">
              <button onClick={() => editarVinculo(vinculo.id)}>
                Editar
              </button>
              <button onClick={() => verDetalhes(vinculo.paciente.id)}>
                Ver Detalhes
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## 🔒 Validações e Regras de Negócio

### Validações Automáticas:
1. **Unicidade**: Não pode haver dois vínculos ativos do mesmo tipo entre o mesmo profissional e paciente
2. **Profissional Existente**: O profissional deve existir no sistema
3. **Paciente Existente**: O paciente deve existir no sistema
4. **Tipo de Atendimento**: Deve ser um dos valores válidos do enum
5. **Data de Início**: Não pode ser no futuro (opcional)
6. **Frequência**: Deve ser entre 1 e 7 sessões por semana
7. **Duração**: Deve ser entre 15 e 180 minutos

### Regras de Status:
- **ATIVO**: Vínculo em funcionamento normal
- **SUSPENSO**: Temporariamente interrompido, pode ser reativado
- **INATIVO**: Encerrado definitivamente, requer data_fim

## 🚀 Como Implementar no Frontend

### 1. Instalar dependências (se usando React)
```bash
npm install axios react-query
```

### 2. Criar serviço de API
```javascript
// services/vinculosAPI.js
import axios from 'axios';

const API_BASE = '/api';

export const vinculosAPI = {
  listar: (filtros = {}) => 
    axios.get(`${API_BASE}/vinculos`, { params: filtros }),
    
  obter: (id) => 
    axios.get(`${API_BASE}/vinculos/${id}`),
    
  criar: (dados) => 
    axios.post(`${API_BASE}/vinculos`, dados),
    
  atualizar: (id, dados) => 
    axios.put(`${API_BASE}/vinculos/${id}`, dados),
    
  ativar: (id) => 
    axios.post(`${API_BASE}/vinculos/${id}/ativar`),
    
  inativar: (id, dataFim = null) => 
    axios.post(`${API_BASE}/vinculos/${id}/inativar`, { data_fim: dataFim }),
    
  suspender: (id) => 
    axios.post(`${API_BASE}/vinculos/${id}/suspender`),
    
  pacientesProfissional: (profissionalId, apenasAtivos = true) => 
    axios.get(`${API_BASE}/profissionais/${profissionalId}/pacientes`, {
      params: { apenas_ativos: apenasAtivos }
    }),
    
  profissionaisPaciente: (pacienteId, apenasAtivos = true) => 
    axios.get(`${API_BASE}/pacientes/${pacienteId}/profissionais`, {
      params: { apenas_ativos: apenasAtivos }
    })
};
```

### 3. Implementar no seu sistema
1. Copie os exemplos de componentes acima
2. Adapte o CSS conforme seu design system
3. Integre com seu sistema de autenticação
4. Adicione validações de permissão conforme necessário
5. Implemente notificações de sucesso/erro

## 📱 Considerações para Mobile

Para aplicações mobile, considere:
- Usar cards compactos para listar vínculos
- Implementar pull-to-refresh
- Adicionar filtros rápidos (status, tipo)
- Usar modais para formulários
- Implementar busca por nome do paciente/profissional

## 🎯 Próximos Passos

1. **Implementar no Frontend**: Use os exemplos fornecidos
2. **Testar Endpoints**: Use o Swagger UI em `/api/`
3. **Configurar Permissões**: Integre com sistema de autenticação
4. **Adicionar Notificações**: Implemente alertas para mudanças de status
5. **Relatórios**: Crie dashboards com estatísticas dos vínculos

---

**📞 Suporte**: Para dúvidas sobre implementação, consulte a documentação da API em `/api/` ou entre em contato com a equipe de desenvolvimento.
