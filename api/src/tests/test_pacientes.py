"""Testes para o router de pacientes"""
from fastapi.testclient import TestClient

def test_get_pacientes(authenticated_client):
    """Testa listagem de pacientes"""
    response = authenticated_client.get("/pacientes")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_create_paciente(authenticated_client):
    """Testa criação de paciente"""
    paciente_data = {
        "nome": "teste",
        "email": "user@example.com",
        "celular": "string",
        "cpf": "string",
        "data_nascimento": "string",
        "sexo": "string",
        "cep": "string",
        "rua": "string",
        "numero": "string",
        "bairro": "string",
        "cidade": "string",
        "estado": 0,
        "role": "paciente",
        "foto_perfil": "string",
        "password": "string"
    }
    
    response = authenticated_client.post("/pacientes", json=paciente_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code in [200, 400]  # 200 criado, 400 se já existir
