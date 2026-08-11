# Clinica API

API FastAPI para gestão de clínica médica com autenticação JWT, integração com Inteligência Artificial para atendimento e captação de leads, upload de arquivos via Supabase Storage / S3, métricas Prometheus e testes automatizados.

---

## Tecnologias

- **FastAPI**: Framework web moderno, assíncrono e de alta performance para construção de APIs.
- **OpenAI / AI SDK**: Integração com modelos LLM para chatbot interativo de atendimento ao paciente e extração de dados estruturados (leads).
- **SQLAlchemy**: ORM para abstração e manipulação do banco de dados (SQLite para desenvolvimento e PostgreSQL para produção).
- **Pydantic & Pydantic Settings**: Validação estrita de schemas e gerenciamento de configurações por variáveis de ambiente.
- **JWT (JSON Web Tokens)**: Autenticação segura via tokens (`python-jose`).
- **Bcrypt**: Criptografia e hash seguro de senhas (`passlib`).
- **Supabase Storage / S3**: Armazenamento e gerenciamento de arquivos (fotos de perfil, documentos em PDF).
- **Prometheus Client**: Exportação de métricas operacionais, autenticações, contagem de requisições e tempos de resposta.
- **Structlog**: System de logging estruturado em formato JSON para fácil integração com agregadores de logs.
- **Pytest & HTTPX**: Suite completa de testes unitários e de integração com suporte a requisições assíncronas.
- **uv**: Gerenciador de pacotes e ambientes virtuais Python de alta velocidade.
- **Ruff & Black**: Ferramentas de linting e formatação automática de código.
- **Docker & Docker Compose**: Containerização completa da aplicação para ambientes de desenvolvimento e produção.
- **GitHub Actions**: Pipeline de CI/CD para execução automatizada de testes, linting e checagem de qualidade.

---

## Estrutura do Projeto

```
api/
├── .github/
│   └── workflows/          # Pipelines de CI/CD do GitHub Actions
│       ├── api.yml         # Testes automatizados da API FastAPI
│       ├── web.yml         # Testes da aplicação web
│       └── lint.yml        # Verificação de linting (Ruff) e formatação (Black)
├── src/
│   ├── auth/               # Utilitários de segurança, hash e criptografia
│   ├── crud/               # Operações de banco de dados (Create, Read, Update, Delete)
│   ├── database/           # Configuração de conexão com o banco e Pydantic Settings
│   ├── deps/               # Injeção de dependências do FastAPI (Sessão DB, CurrentUser)
│   ├── logging_config/     # Configuração de logging estruturado (Structlog)
│   ├── metrics/            # Métricas expostas no formato Prometheus (/metrics)
│   ├── models/             # Modelos de dados SQLAlchemy (Tabelas)
│   ├── routes/             # Endpoints e controllers organizados por módulos
│   ├── schemas/            # Schemas de validação e serialização Pydantic
│   ├── services/           # Serviços de negócio (IA, extração de leads, etc.)
│   ├── storage/            # Serviços de integração com Supabase Storage / S3
│   ├── tests/              # Testes automatizados com Pytest
│   ├── populate_db.py      # Script para povoamento de dados iniciais do banco
│   └── main.py             # Aplicação principal FastAPI e registro de rotas
├── .env                    # Variáveis de ambiente locais
├── .env-example            # Modelo de configuração de variáveis de ambiente
├── Dockerfile              # Imagem Docker da API em Python 3.12-slim
├── docker-compose.yml      # Configuração Docker Compose para desenvolvimento local
├── docker-compose.prod.yml # Configuração Docker Compose para produção (API + PostgreSQL)
├── pyproject.toml          # Gerenciamento de dependências e configurações das ferramentas
└── README.md               # Documentação oficial da API
```

---

## Instalação e Configuração

### Pré-requisitos

- **Python 3.12+**
- **uv** (gerenciador de pacotes ultra-rápido) ou **pip**
- **Docker & Docker Compose** (opcional, para execução containerizada)

### Passos de Instalação

1. **Clone o repositório:**
   ```bash
   git clone <repository-url>
   cd clinica-api
   ```

2. **Instale as dependências com `uv`:**
   ```bash
   uv sync
   ```

3. **Configure as variáveis de ambiente:**
   Crie um arquivo `.env` na raiz do projeto com base no `.env-example`:

   ```env
   ENVIRONMENT=dev
   DOMAIN=localhost
   SECRET_KEY=sua-secret-key-super-segura
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   DATABASE_URL=sqlite:///./clinica.db

   # PostgreSQL (Para produção ou testes com Postgres)
   SCHEME=postgresql+psycopg2
   USER=postgres
   PASSWORD=postgres
   HOST=localhost
   PORT=5432
   DATABASE_NAME=clinica_db

   # Supabase Storage / S3
   SUPABASE_STORAGE_URL=https://sua-url-supabase.co
   SUPABASE_S3_ENDPOINT=https://sua-url-supabase.co/storage/v1/s3
   SUPABASE_ACCESS_KEY=sua-access-key
   SUPABASE_SECRET_KEY=sua-secret-key
   SUPABASE_REGION=sa-east-1
   SUPABASE_BUCKET=clinica-files

   # Configurações da API de IA (OpenAI / compatíveis)
   AI_API_KEY=sua-api-key-openai
   AI_BASE_URL=https://api.openai.com/v1
   AI_MODEL=gpt-4o-mini
   ```

---

## Execução

### 1. Modo Desenvolvimento (Local)

Para iniciar o servidor de desenvolvimento com reload automático:

```bash
uv run uvicorn src.main:app --reload
```

A API estará disponível em `http://localhost:8000`.

### 2. Modo Containerizado (Docker)

**Desenvolvimento:**
```bash
docker compose up --build
```
A API estará disponível em `http://localhost:8001`.

**Produção (com banco PostgreSQL):**
```bash
docker compose -f docker-compose.prod.yml up -d
```
A API estará disponível em `http://localhost:8000` conectada ao container PostgreSQL.

### Documentação Interativa das Rotas

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Inteligência Artificial & Atendimento Inteligente

A **Clinica API** possui um módulo de IA generativa integrado para otimizar o atendimento prévio de pacientes:

### Funcionalidades do Chatbot com IA

- **Conversa Fluida**: O endpoint `POST /chat` permite interação contínua mantendo o histórico da conversa por `session_id`.
- **Coleta Progressiva de Informações**: O assistente virtual solicita de forma cordial dados fundamentais para o agendamento:
  1. Nome Completo
  2. WhatsApp com DDD
  3. Data de Nascimento
  4. Especialidade médica ou área de atendimento desejada
  5. Convênio médico ou indicação de consulta Particular
- **Extração Automatizada de Leads**: Ao identificar o encerramento do diálogo de pré-agendamento, a IA extrai automaticamente os dados estruturados do paciente em formato JSON e registra um novo **Lead** no banco de dados (`POST /chat` -> `chat_crud.create_or_update_lead`).
- **Resiliência e Tolerância a Falhas**: Inclui tratamento automático de Rate Limit (HTTP 429) e retries com *exponential backoff* (`safe_chat_completion`).
- **Consulta de Leads**: Administradores e atendentes autenticados podem consultar a lista de leads gerados através da rota `GET /leads`.

---

## Catálogo Completo de Rotas da API

### Autenticação e Gestão de Usuários

| Método | Endpoint | Descrição | Requer Auth |
| :--- | :--- | :--- | :---: |
| `POST` | `/login/access-token` | Login via formulário (OAuth2 Standard Password Flow) | Não |
| `POST` | `/auth/login-json` | Login enviando credenciais via JSON | Não |
| `POST` | `/auth/validate-token` | Validação de token JWT ativo | Não |
| `POST` | `/signup` | Registro de novos usuários (pacientes) | Não |
| `GET` | `/users/me` | Retorna os dados do usuário autenticado | Sim |
| `DELETE` | `/users/{user_id}` | Exclusão de conta de usuário | Sim (Admin) |

### Atendimento com Inteligência Artificial & Leads

| Método | Endpoint | Descrição | Requer Auth |
| :--- | :--- | :--- | :---: |
| `POST` | `/chat` | Interação com o assistente virtual de IA e pré-cadastro | Não |
| `GET` | `/leads` | Listagem de pacientes/leads capturados via IA no chat | Sim |

### Dashboard & Resumo Executivo

| Método | Endpoint | Descrição | Requer Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/dashboard/resumo` | Métricas consolidadas (totais de pacientes, médicos, clínicas, consultas de hoje, consultas pendentes, gráfico mensal e cadastros recentes) | Sim (Admin) |

### Agenda & Agendamentos

| Método | Endpoint | Descrição | Requer Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/agenda-completa` | Visão unificada semanal (médicos, vagas, salas, agendamentos e datas) | Sim |
| `GET` | `/dados-agendamento` | Carrega médicos, vagas, pacientes e turnos para popular formulários | Sim |
| `POST` | `/agendar-consulta` | Endpoint otimizado para solicitar um novo agendamento | Sim |
| `GET` | `/agendamentos/` | Listagem de todos os agendamentos | Sim |
| `GET` | `/agendamentos/{id}` | Busca agendamento específico por ID | Sim |
| `POST` | `/agendamentos/` | Criação básica de agendamento | Sim |
| `PUT` | `/agendamentos/{id}` | Atualização completa de agendamento | Sim |
| `PATCH` | `/agendamentos/{id}/status` | Atualização rápida de status (`aguardando`, `confirmada`, `agendado`, `cancelada`, `realizada`) | Sim |
| `DELETE` | `/agendamentos/{id}` | Exclusão de agendamento | Sim |

### Upload & Gestão de Arquivos (Supabase Storage / S3)

| Método | Endpoint | Descrição | Requer Auth |
| :--- | :--- | :--- | :---: |
| `POST` | `/upload/profile-image/{user_id}` | Upload de imagem de perfil (PNG, JPG, JPEG - máx 5MB) | Sim |
| `POST` | `/upload/document/{user_id}` | Upload de documentos profissionais (PDF - máx 10MB) | Sim |
| `DELETE` | `/upload/file` | Exclusão de arquivo armazenado via URL | Sim |
| `GET` | `/upload/validate` | Consulta informações de limites e tipos de arquivos permitidos | Não |

### Médicos & Alocação em Salas

| Método | Endpoint | Descrição | Requer Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/medicos` | Listagem simplificada de médicos | Sim |
| `GET` | `/medicos/completo` | Listagem de médicos com especialidade, conselho e UF carregados | Sim |
| `GET` | `/medicos/{id}` | Buscar médico por ID | Sim |
| `POST` | `/medicos` | Cadastrar médico | Sim (Admin) |
| `PUT` | `/medicos/{id}` | Atualizar dados do médico | Sim (Admin) |
| `DELETE` | `/medicos/{id}` | Remover médico | Sim (Admin) |
| `GET` | `/medico-sala/optimized/{medico_id}` | Endpoint otimizado em lote para vinculação de médico a salas/vagas | Sim |
| `GET` | `/simple/{medico_id}` | Consulta simples de alocação de sala por médico | Sim |

### Clínicas, Salas & Vagas de Atendimento

| Método | Endpoint | Descrição | Requer Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/clinicas/` | Listar clínicas | Não |
| `GET` | `/clinicas/{id}` | Buscar clínica por ID | Não |
| `GET` | `/salas/` | Listar salas de atendimento | Não |
| `GET` | `/salas/{id}` | Buscar sala por ID | Não |
| `GET` | `/salas/clinica/{clinica_id}` | Listar salas de uma clínica específica | Não |
| `POST` | `/salas/` | Criar nova sala | Sim (Admin) |
| `PUT` | `/salas/{id}` | Atualizar sala | Sim (Admin) |
| `DELETE` | `/salas/{id}` | Remover sala | Sim (Admin) |
| `GET` | `/vagas` | Listar vagas/turnos de atendimento | Não |
| `GET` | `/vagas/{id}` | Buscar vaga por ID | Não |
| `GET` | `/vagas/clinica/{clinica_id}` | Listar vagas de uma clínica | Não |
| `POST` | `/vagas` | Criar vaga de atendimento | Sim (Admin) |
| `PUT` | `/vagas/{id}` | Atualizar vaga | Sim (Admin) |
| `DELETE` | `/vagas/{id}` | Remover vaga | Sim (Admin) |

### Calendário da Clínica

| Método | Endpoint | Descrição | Requer Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/calendario-clinica/` | Listar registros do calendário | Sim |
| `GET` | `/calendario-clinica/{clinica_id}` | Listar calendário por clínica | Sim |
| `GET` | `/calendario-clinica/data/{data}` | Buscar eventos por data | Sim |
| `POST` | `/calendario-clinica/` | Adicionar evento ao calendário | Sim |
| `PUT` | `/calendario-clinica/{id}` | Atualizar evento do calendário | Sim |
| `DELETE` | `/calendario-clinica/{id}` | Remover evento do calendário | Sim |

### Tabelas de Apoio (Estados, Especialidades, Tipo Conselho)

| Método | Endpoint | Descrição | Requer Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/estados/` | Listar UFs e estados | Não |
| `GET` | `/especialidades/` | Listar especialidades médicas | Não |
| `GET` | `/tipo-conselho/` | Listar tipos de conselho profissional (ex: CRM, CRO) | Não |

### Monitoramento & Métricas

| Método | Endpoint | Descrição | Requer Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/metrics` | Métricas operacionais expostas para coleta do Prometheus | Não |

---

## Autenticação e Controle de Acesso (RBAC)

A API utiliza o modelo de autenticação **JWT (Bearer Token)** e controle de acesso baseado em papéis (**Roles**):

- **administrador**: Acesso completo a todos os recursos, relatórios, cadastros e dashboard executivo.
- **medico**: Acesso às agendas, alocação de salas e prontuários/agendamentos de pacientes.
- **atendente**: Acesso às agendas, agendamentos e validação de documentos.
- **paciente**: Acesso às suas próprias informações de perfil e agendamentos.

### Exemplo de Uso com cURL

1. **Obtenção do Token de Acesso:**
   ```bash
   curl -X POST "http://localhost:8000/login/access-token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@clinica.com&password=suasenha"
   ```

2. **Requisição para Rota Protegida:**
   ```bash
   curl -X GET "http://localhost:8000/dashboard/resumo" \
     -H "Authorization: Bearer <SEU_TOKEN_JWT>"
   ```

---

## Testes Automatizados

### Executar a Suíte de Testes

```bash
uv run pytest src/tests/ -s
```

### Executar Teste Específico

```bash
uv run pytest src/tests/test_auth.py -s
```

---

## Observabilidade: Métricas e Logging

- **Prometheus Metrics (`/metrics`)**: Expõe contadores de tentativas de autenticação (`auth_attempts_total`), operações de usuários (`user_operations_total`), requisições por status (`request_duration_seconds`), número de usuários ativos e contadores de rate limit.
- **Structlog**: Logs estruturados em formato JSON com inclusão automática de timestamp ISO, nível de log e metadados contextuais da aplicação.

---

## Licença

Este projeto está sob a licença [MIT](LICENSE).
