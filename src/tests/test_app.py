"""App de teste isolado sem populate_database"""

from unittest.mock import MagicMock, Mock

from fastapi import FastAPI

from src.deps.user import get_current_user, get_db
from src.routes.clinicas import router as clinicas_router
from src.routes.especialidades import router as especialidades_router
from src.routes.estados import router as estados_router
from src.routes.pacientes import router as pacientes_router


def create_test_app():
    """Cria app de teste sem populate_database"""
    test_app = FastAPI()

    # Aplicar overrides antes de incluir os routers
    mock_user = Mock()
    mock_user.id = 1
    mock_user.role = "administrador"

    mock_session = MagicMock()

    def override_get_current_user(session, token):
        return mock_user

    def override_get_db():
        return mock_session

    test_app.dependency_overrides[get_current_user] = override_get_current_user
    test_app.dependency_overrides[get_db] = override_get_db

    # Incluir routers após aplicar overrides
    test_app.include_router(estados_router)
    test_app.include_router(especialidades_router)
    test_app.include_router(clinicas_router)
    test_app.include_router(pacientes_router)

    return test_app
