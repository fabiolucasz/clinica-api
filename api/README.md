# Clinica API

API FastAPI para gestão de clínica médica com autenticação JWT, integração com Supabase Storage e testes automatizados.

## Tecnologias

- **FastAPI**: Framework web moderno e rápido para construção de APIs
- **SQLAlchemy**: ORM para interação com banco de dados
- **Pydantic**: Validação de dados e settings
- **JWT**: Autenticação via tokens (jose)
- **Bcrypt**: Hash de senhas
- **Supabase Storage**: Armazenamento de arquivos (imagens, documentos)
- **Pytest**: Framework de testes
- **uv**: Gerenciador de pacotes Python

## Estrutura do Projeto

```
api/
├── src/
│   ├── auth/          # Autenticação e segurança
│   ├── crud/          # Operações de banco de dados
│   ├── database/      # Configuração de banco
│   ├── deps/          # Dependências do FastAPI
│   ├── models/        # Modelos SQLAlchemy
│   ├── routes/        # Rotas da API
│   ├── schemas/       # Schemas Pydantic
│   ├── tests/         # Testes automatizados
│   └── main.py        # Aplicação principal
├── .env               # Variáveis de ambiente
├── pyproject.toml     # Dependências do projeto
└── README.md          # Documentação
```

## Instalação

### Pré-requisitos

- Python 3.12+
- uv (gerenciador de pacotes)

### Passos

1. Clone o repositório:
```bash
git clone <repository-url>
cd api
```

2. Instale as dependências:
```bash
uv sync
```

3. Configure as variáveis de ambiente no arquivo `.env`:
```env
# Database
DATABASE_URL=sqlite:///./clinica.db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SUPABASE_BUCKET=your-bucket-name
```

## Execução

### Modo Desenvolvimento

```bash
uv run uvicorn src.main:app --reload
```

A API estará disponível em `http://localhost:8000`

### Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Rotas da API

### Autenticação

- `POST /signup` - Registro de usuário
- `POST /login/access-token` - Login e obtenção de token

### Estados

- `GET /estados/` - Listar estados
- `GET /estados/{id}` - Buscar estado por ID

### Clínicas

- `GET /clinicas/` - Listar clínicas
- `GET /clinicas/{id}` - Buscar clínica por ID

### Especialidades

- `GET /especialidades/` - Listar especialidades
- `GET /especialidades/{id}` - Buscar especialidade por ID

### Pacientes

- `GET /pacientes` - Listar pacientes (requer autenticação)
- `POST /pacientes` - Criar paciente (requer role administrador)
- `PUT /pacientes/{id}` - Atualizar paciente (requer role administrador)

### Agenda

- `GET /agenda-completa` - Agenda completa (requer autenticação)

## Autenticação

A API usa JWT (JSON Web Tokens) para autenticação. Para acessar rotas protegidas:

1. Faça login para obter o token:
```bash
curl -X POST "http://localhost:8000/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=seu@email.com&password=sua-senha"
```

2. Use o token no header Authorization:
```bash
curl -X GET "http://localhost:8000/pacientes" \
  -H "Authorization: Bearer <seu-token>"
```

## Roles de Usuário

- **administrador**: Acesso total, pode criar/editar pacientes e outros recursos
- **medico**: Acesso limitado a funcionalidades médicas
- **paciente**: Acesso apenas aos próprios dados

## Testes

### Executar Todos os Testes

```bash
uv run pytest src/tests/ -s
```

### Executar Teste Específico

```bash
uv run pytest src/tests/test_auth.py -s
```

### Estrutura dos Testes

Os testes usam fixtures do pytest para:
- Mock de sessão do banco de dados
- Mock de autenticação e usuários
- Cliente de teste com token de autenticação
- Dados compartilhados entre testes

## Supabase Storage

A API integra com Supabase Storage para upload de arquivos:
- Imagens de perfil de médicos e pacientes
- Documentos médicos
- Outros arquivos relacionados

## Desenvolvimento

### Adicionar Nova Rota

1. Crie o schema em `src/schemas/`
2. Adicione a função CRUD em `src/crud/`
3. Crie a rota em `src/routes/`
4. Registre a rota em `src/main.py`
5. Adicione testes em `src/tests/`

### Padrões de Código

- Use type hints em todas as funções
- Valide dados com Pydantic schemas
- Use dependency injection do FastAPI
- Escreva testes para novas funcionalidades

## Troubleshooting

### Erro de Conexão com Banco

Verifique se o `DATABASE_URL` no `.env` está correto e se o banco de dados existe.

### Erro de Autenticação

Certifique-se de que:
- O token JWT está sendo enviado no header `Authorization`
- O token não está expirado
- As credenciais estão corretas

### Erro de Permissão (403)

Verifique se o usuário tem a role necessária para acessar o recurso.

## Licença

[Adicionar licença aqui]