from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app


def test_chat_endpoint():
    client = TestClient(app)

    with patch("src.routes.chat.get_assistant_response") as mock_get_resp:
        mock_get_resp.return_value = "Olá! Como posso ajudar?"

        response = client.post(
            "/chat",
            json={"message": "Olá", "session_id": "test-session-123"},
        )

        assert response.status_code == 200
        assert response.json()["response"] == "Olá! Como posso ajudar?"
