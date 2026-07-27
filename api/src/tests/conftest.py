"""Fixtures compartilhados para os testes"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock, patch
from src.main import app
from src.deps.user import get_db, get_current_user
from sqlalchemy.orm import Session

mock_session = MagicMock()

# Configurar mock para retornar dados válidos
mock_estado = MagicMock()
mock_estado.id = 1
mock_estado.nome = "São Paulo"
mock_estado.uf = "SP"

# Mock usuário para login e autenticação
mock_db_user = Mock()
mock_db_user.id = 1
mock_db_user.email = "admin@novo.com"
mock_db_user.nome = "admin novo"
mock_db_user.role = "administrador"
mock_db_user.is_active = True
# Hash bcrypt real para "adminnovo"
mock_db_user.hashed_password = "$2b$12$yrwlr3LV767hXAlcvFRh6ugbhHhFN.y9jb6413XbhNociGMrk4N0i"

# Mock paciente para resposta
mock_paciente = Mock()
mock_paciente.id = 1
mock_paciente.nome = "teste"
mock_paciente.email = "user@example.com"
mock_paciente.role = "paciente"

# Configurar query para retornar dados apropriados
def mock_query(*args, **kwargs):
    query = MagicMock()
    # Detectar se é query de User pelo argumento
    if args and hasattr(args[0], '__name__') and 'User' in str(args[0]):
        query.filter.return_value.first.return_value = mock_db_user
    else:
        # Para outras queries, retornar lista vazia por padrão
        query.all.return_value = []
        # Para busca por ID, retornar estado mockado
        query.filter.return_value.first.return_value = mock_estado
    return query

mock_session.query = mock_query
mock_session.get = lambda model, id: mock_db_user if hasattr(model, '__name__') and 'User' in str(model) else None
mock_session.commit = lambda: None

# Variável para armazenar o último objeto adicionado
last_added_obj = None
def mock_add(obj):
    global last_added_obj
    last_added_obj = obj
    setattr(obj, 'id', 1)
def mock_refresh(obj):
    global last_added_obj
    # Copiar atributos do objeto adicionado para o objeto passado
    if last_added_obj:
        for attr in ['id', 'nome', 'email', 'role']:
            if hasattr(last_added_obj, attr):
                setattr(obj, attr, getattr(last_added_obj, attr))

mock_session.add = mock_add
mock_session.refresh = mock_refresh

def override_get_db():
    try:
        yield mock_session
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def mock_db_session():
    """Mock de sessão do banco de dados"""
    return mock_session

@pytest.fixture(scope="session")
def shared_user_data():
    """Fixture para compartilhar dados entre testes"""
    return {}

@pytest.fixture(scope="session")
def auth_token():
    """Faz login e retorna o token de acesso (escopo de sessão para evitar rate limit)"""
    client = TestClient(app)
    
    response = client.post(
        "/login/access-token",
        data={"username": "admin@novo.com", "password": "adminnovo"}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    return None

@pytest.fixture
def authenticated_client(auth_token):
    """Cliente com header de autenticação usando token real"""
    client = TestClient(app)
    if auth_token:
        client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return client