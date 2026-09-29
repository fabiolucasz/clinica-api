"""
Rotas para integração com Google OAuth (login social)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.auth.google_oauth import GoogleOAuthManager
from src.auth.security import create_access_token
from src.crud import google_oauth as crud
from src.database.connection import get_db
from src.deps.user import CurrentUser
from src.models import models
from src.schemas.google_oauth import GoogleCredentialsResponse

router = APIRouter()


@router.get("/auth/google/login")
async def google_login():
    """
    Inicia o fluxo de login social com Google
    Não requer autenticação prévia
    """
    # Gerar state e armazenar flag de login
    authorization_url, state = GoogleOAuthManager.get_authorization_url(
        user_id=None, is_login=True
    )

    return {
        "authorization_url": authorization_url,
        "state": state,
        "message": "Use esta URL para fazer login com Google",
    }


@router.get("/auth/google/callback")
async def google_login_callback(
    code: str, state: str | None = None, db: Session = Depends(get_db)
):
    """
    Callback do Google OAuth para login social
    Verifica se o email existe no banco e faz login
    """
    if not code:
        raise HTTPException(
            status_code=400, detail="Código de autorização não fornecido"
        )

    if not state:
        raise HTTPException(status_code=400, detail="State não fornecido")

    # Recuperar info do state
    from src.auth.google_oauth import STATE_USER_IDS

    state_info = STATE_USER_IDS.get(state)

    if not state_info or not state_info.get("is_login"):
        raise HTTPException(status_code=400, detail="State inválido ou expirado")

    try:
        # Trocar código por credenciais
        credentials = GoogleOAuthManager.exchange_code_for_credentials(code, state)

        # Obter informações do usuário do Google
        from googleapiclient.discovery import build

        service = build("oauth2", "v2", credentials=credentials)
        user_info = service.userinfo().get().execute()

        google_email = user_info.get("email")
        google_name = user_info.get("name")

        if not google_email:
            raise HTTPException(
                status_code=400, detail="Não foi possível obter o email do Google"
            )

        # Verificar se existe usuário com este email
        user = db.query(models.User).filter(models.User.email == google_email).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado. Por favor, crie uma conta primeiro e vincule o Google.",
            )

        # Criar token de acesso
        from datetime import timedelta

        access_token = create_access_token(
            subject=str(user.id), expires_delta=timedelta(minutes=30)
        )

        # Limpar state
        STATE_USER_IDS.pop(state, None)

        # Retornar HTML com script para fechar o popup e enviar o token
        html_content = f"""
        <html>
        <head>
            <title>Login Google</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .message {{
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    text-align: center;
                }}
                h1 {{ color: #667eea; }}
                p {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="message">
                <h1>✅ Login Realizado com Sucesso!</h1>
                <p>Bem-vindo, {google_name}!</p>
                <p>Fechando janela...</p>
            </div>
            <script>
                if (window.opener) {{
                    window.opener.postMessage({{ type: 'GOOGLE_LOGIN_SUCCESS', token: '{access_token}' }}, '*');
                    window.close();
                }}
            </script>
        </body>
        </html>
        """

        from fastapi.responses import HTMLResponse

        return HTMLResponse(content=html_content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao fazer login com Google: {e!s}"
        )


@router.get("/google/auth/url")
async def get_google_auth_url(current_user: CurrentUser, db: Session = Depends(get_db)):
    """
    Gera URL de autorização do Google OAuth
    Usuário usa esta URL para conectar sua conta do Google (vinculação)
    """
    # Gerar state e armazenar user_id
    authorization_url, state = GoogleOAuthManager.get_authorization_url(
        user_id=current_user.id
    )

    return {
        "authorization_url": authorization_url,
        "state": state,
        "message": "Use esta URL para conectar sua conta do Google",
    }


@router.get("/google/auth/callback")
async def google_auth_callback_get(
    code: str, state: str | None = None, db: Session = Depends(get_db)
):
    """
    Callback do Google OAuth após autorização (GET)
    Recebe o código de autorização e salva as credenciais (vinculação)
    """
    if not code:
        raise HTTPException(
            status_code=400, detail="Código de autorização não fornecido"
        )

    if not state:
        raise HTTPException(status_code=400, detail="State não fornecido")

    # Recuperar user_id do state
    from src.auth.google_oauth import STATE_USER_IDS

    state_info = STATE_USER_IDS.get(state)

    if not state_info:
        raise HTTPException(status_code=400, detail="State inválido ou expirado")

    if state_info.get("is_login"):
        return await google_login_callback(code, state, db)

    user_id = state_info.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="User ID não encontrado no state")

    try:
        # Trocar código por credenciais
        credentials = GoogleOAuthManager.exchange_code_for_credentials(code, state)
        credentials_dict = GoogleOAuthManager.credentials_to_dict(credentials)

        # Salvar credenciais no banco
        existing = crud.get_google_credentials(db, user_id)
        if existing:
            crud.update_google_credentials(db, user_id, credentials_dict)
        else:
            crud.create_google_credentials(db, credentials_dict, user_id)

        # Limpar state
        STATE_USER_IDS.pop(state, None)

        # Retornar HTML com mensagem de sucesso
        html_content = """
        <html>
        <head>
            <title>Conexão Google</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .message {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    text-align: center;
                }
                h1 { color: #667eea; }
                p { color: #666; }
                button {
                    background: #667eea;
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <div class="message">
                <h1>✅ Conexão Realizada com Sucesso!</h1>
                <p>Sua conta do Google foi conectada.</p>
                <p>Você pode fechar esta janela e voltar ao frontend.</p>
                <button onclick="window.close()">Fechar Janela</button>
            </div>
        </body>
        </html>
        """

        from fastapi.responses import HTMLResponse

        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao conectar conta do Google: {e!s}"
        )


@router.get("/google/credentials", response_model=GoogleCredentialsResponse)
async def get_google_credentials(
    current_user: CurrentUser, db: Session = Depends(get_db)
):
    """
    Verifica se o usuário tem credenciais do Google conectadas
    """
    credentials = crud.get_google_credentials(db, current_user.id)

    if not credentials:
        return {
            "id": 0,
            "user_id": current_user.id,
            "is_connected": False,
            "connected_at": None,
        }

    return {
        "id": credentials.id,
        "user_id": credentials.user_id,
        "is_connected": credentials.is_connected,
        "connected_at": credentials.connected_at,
    }


@router.delete("/google/disconnect")
async def disconnect_google(current_user: CurrentUser, db: Session = Depends(get_db)):
    """
    Desconecta a conta do Google do usuário
    """
    result = crud.delete_google_credentials(db, current_user.id)

    if not result:
        raise HTTPException(status_code=404, detail="Credenciais não encontradas")

    return {"message": "Conta do Google desconectada com sucesso"}
