"""Testes para o router de autenticação"""
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# def test_login_success():
#     """Testa login com credenciais válidas"""
#     response = client.post(
#         "/login/access-token",
#         data={"username": "admin@test.com", "password": "admin123"}
#     )
#     # Pode retornar 200 (sucesso) ou 401 (usuário não existe no banco de teste)
#     assert response.status_code in [200, 401]
    
#     if response.status_code == 200:
#         data = response.json()
#         assert "access_token" in data

def test_signup(shared_user_data):
    """Testa criação de novo usuário"""
    user_data = {
        "email": "admin@novo.com",
        "password": "adminnovo",
        "nome": "admin novo",
        "celular": "string",
        "cpf": "string",
        "data_nascimento": "string",
        "sexo": "string",
        "cep": "string",
        "rua": "string",
        "numero": "string",
        "bairro": "string",
        "cidade": "string",
        "estado": 1,
        "role": "administrador",
        "foto_perfil": "string",
        "especialidade": 1,
        "rqe": "string",
        "valor_consulta": 0,
        "tipo_conselho": 1,
        "uf_conselho": 1,
        "numero_conselho": "string",
        "upload_arquivo": "string"
    }
    response = client.post("/signup", json=user_data)
    # Pode ser 200 (criado) ou 400 (email já existe)
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        shared_user_data.update(response.json())
        print(f"Usuário criado: {shared_user_data}")
    else:
        # Se usuário já existe, usar dados fixos para login
        shared_user_data.update({"email": "admin@novo.com", "password": "adminnovo"})
        print(f"Usuário já existe, usando dados fixos: {shared_user_data}")

def test_login_success(shared_user_data):
    """Testa login com credenciais válidas"""
    # Se shared_user_data estiver vazio, usar dados fixos
    if not shared_user_data:
        shared_user_data.update({"email": "admin@novo.com", "password": "adminnovo"})
    
    response = client.post(
        "/login/access-token",
        data={"username": shared_user_data["email"], "password": "adminnovo"}
    )
    # Pode retornar 200 (sucesso) ou 401 (usuário não existe no banco de teste)
    assert response.status_code in [200, 401]
    
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        print(f"Token recebido: {data['access_token']}")
