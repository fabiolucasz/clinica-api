"""Testes para o router de especialidades"""


def test_get_especialidades(authenticated_client):
    """Testa listagem de especialidades"""
    response = authenticated_client.get("/especialidades/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_especialidade_by_id(authenticated_client):
    """Testa buscar especialidade por ID"""
    response = authenticated_client.get("/especialidades/1")
    assert response.status_code in [200, 404]
