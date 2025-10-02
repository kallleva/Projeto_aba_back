# 🚀 Sistema de Inicialização Automática - Projeto ABA

Este documento explica como usar o sistema de inicialização automática que popula o banco de dados com dados iniciais quando o container é iniciado.

## 📋 O que foi implementado

### 1. Script de Seed Data (`src/database/seed_data.py`)
- Cria automaticamente usuários, profissionais, pacientes, planos terapêuticos e metas
- Verifica se já existem dados antes de criar novos
- Inclui credenciais de acesso para teste

### 2. Script de Inicialização (`init_db.py`)
- Aguarda o banco de dados estar disponível
- Executa migrations do Alembic
- Popula dados iniciais
- Trata erros e timeouts

### 3. Docker Compose Atualizado
- Adiciona serviço da aplicação Flask
- Configura healthcheck para o banco
- Executa inicialização automática na ordem correta
- Mapeia volumes para desenvolvimento

## 🎯 Como usar

### Iniciar o sistema completo:
```bash
docker-compose up --build
```

### Apenas o banco de dados:
```bash
docker-compose up db
```

### Executar seed data manualmente:
```bash
python src/database/seed_data.py
```

## 🔑 Credenciais de Acesso Criadas

### Profissionais:
- **Email:** `prof1@clinica.com` | **Senha:** `prof123`
- **Email:** `prof2@clinica.com` | **Senha:** `prof123`  
- **Email:** `prof3@clinica.com` | **Senha:** `prof123`

### Responsáveis:
- **Email:** `carlos.oliveira@email.com` | **Senha:** `resp123`
- **Email:** `sandra.ferreira@email.com` | **Senha:** `resp123`
- **Email:** `roberto.rodrigues@email.com` | **Senha:** `resp123`

## 📊 Dados Criados Automaticamente

- **3 Profissionais** (Dr. João Silva, Dra. Maria Santos, Dr. Pedro Costa)
- **3 Pacientes** (Ana Clara, Lucas, Sophia)
- **6 Usuários** (3 profissionais + 3 responsáveis)
- **3 Planos Terapêuticos** (um para cada paciente)
- **6 Metas Terapêuticas** (2 metas por plano)

## 🔧 Configurações

### Variáveis de Ambiente:
- `DB_USER`: usuário do banco (padrão: aba_user)
- `DB_PASS`: senha do banco (padrão: aba_pass123)
- `DB_NAME`: nome do banco (padrão: aba_postgres)
- `DB_HOST`: host do banco (padrão: db para Docker)
- `SECRET_KEY`: chave secreta do Flask

### Portas:
- **Aplicação:** `http://localhost:5000`
- **Banco:** `localhost:5432`
- **API Docs:** `http://localhost:5000/api/`

## 🛠️ Desenvolvimento

### Para desenvolvimento local (sem Docker):
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export DB_USER=aba_user
export DB_PASS=aba_pass123
export DB_NAME=aba_postgres
export DB_HOST=localhost

# Executar aplicação
python src/main.py
```

### Para resetar dados:
```python
from src.database.seed_data import clear_all_data
from src.main import app

with app.app_context():
    clear_all_data()
```

## 📝 Logs e Monitoramento

O sistema exibe logs detalhados durante a inicialização:
- ✅ Sucesso nas operações
- ⚠️ Avisos e falhas não críticas
- ❌ Erros críticos
- 📊 Resumo dos dados criados

## 🚨 Troubleshooting

### Banco não conecta:
- Verifique se o container do banco está rodando
- Confirme as credenciais nas variáveis de ambiente
- Aguarde o healthcheck do banco passar

### Seed data não executa:
- Verifique se não há dados existentes no banco
- Confirme se todas as tabelas foram criadas
- Verifique os logs para erros específicos

### Migrations falham:
- Verifique se o Alembic está configurado corretamente
- Confirme se o arquivo `alembic.ini` está correto
- Verifique se há conflitos de versão

## 🎉 Próximos Passos

Após a inicialização bem-sucedida:
1. Acesse `http://localhost:5000/api/` para ver a documentação
2. Use as credenciais criadas para fazer login
3. Teste as funcionalidades da API
4. Desenvolva novas features usando os dados de exemplo
