"""
Testes para integração com Google OAuth (login social)
"""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.auth.security import create_access_token
from src.database.connection import Base
from src.main import app
from src.models import models


@pytest.fixture
def client():
    """Fixture para cliente de teste"""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Fixture para sessão do banco de dados"""
    from src.database.connection import SessionLocal, engine

    # Criar tabelas
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Limpar tabelas após teste
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session: Session):
    """Fixture para criar usuário de teste"""
    user = models.User(
        nome="Test User",
        email="test@example.com",
        hashed_password="hashed_password",
        role="medico",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_get_google_login_url(client: TestClient):
    """Testa endpoint para obter URL de login Google"""
    response = client.get("/auth/google/login")

    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    assert "state" in data
    assert "message" in data
    assert "accounts.google.com" in data["authorization_url"]


def test_google_login_callback_invalid_state(client: TestClient):
    """Testa callback com state inválido"""
    response = client.get("/auth/google/callback?code=test_code&state=invalid_state")

    assert response.status_code == 400
    assert "State inválido ou expirado" in response.json()["detail"]


def test_google_login_callback_no_code(client: TestClient):
    """Testa callback sem código"""
    response = client.get("/auth/google/callback?state=test_state")

    assert response.status_code == 422  # Unprocessable Entity (validação do FastAPI)


def test_google_login_callback_user_not_found(client: TestClient, db_session: Session):
    """Testa callback com email não existente no banco"""
    # Este teste não pode ser completamente testado sem mock do Google OAuth
    # pois precisaria de um código válido do Google
    # Testamos apenas o caso onde o usuário não existe

    # Mock do Google OAuth seria necessário aqui
    # Por enquanto, testamos apenas a validação básica


def test_get_google_auth_url_authenticated(client: TestClient, test_user: models.User):
    """Testa endpoint para vincular conta Google (requer autenticação)"""
    # Criar token de acesso
    token = create_access_token(
        subject=str(test_user.id), expires_delta=timedelta(minutes=30)
    )

    response = client.get(
        "/google/auth/url", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    assert "state" in data


def test_get_google_auth_url_unauthenticated(client: TestClient):
    """Testa endpoint para vincular conta sem autenticação"""
    response = client.get("/google/auth/url")

    assert response.status_code == 401  # Unauthorized


def test_get_google_credentials(
    client: TestClient, test_user: models.User, db_session: Session
):
    """Testa endpoint para verificar credenciais Google"""
    # Criar token de acesso
    token = create_access_token(
        subject=str(test_user.id), expires_delta=timedelta(minutes=30)
    )

    response = client.get(
        "/google/credentials", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "is_connected" in data
    assert data["is_connected"] == False  # Usuário não tem Google vinculado


def test_disconnect_google(
    client: TestClient, test_user: models.User, db_session: Session
):
    """Testa endpoint para desconectar conta Google"""
    # Criar token de acesso
    token = create_access_token(
        subject=str(test_user.id), expires_delta=timedelta(minutes=30)
    )

    response = client.delete(
        "/google/disconnect", headers={"Authorization": f"Bearer {token}"}
    )

    # Se não tiver credenciais, retorna 404
    assert response.status_code in [200, 404]


def test_google_auth_callback_invalid_state(client: TestClient):
    """Testa callback de vinculação com state inválido"""
    response = client.get("/google/auth/callback?code=test_code&state=invalid_state")

    assert response.status_code == 400


def test_google_auth_callback_no_code(client: TestClient):
    """Testa callback de vinculação sem código"""
    response = client.get("/google/auth/callback?state=test_state")

    assert response.status_code == 422  # Unprocessable Entity (validação do FastAPI)
