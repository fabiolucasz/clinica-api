"""Testes para o router de agenda"""


def test_agenda_completa(authenticated_client):
    """Testa agenda completa"""
    response = authenticated_client.get("/agenda-completa")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
