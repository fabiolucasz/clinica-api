"""
Configuração e autenticação Google OAuth 2.0
"""

import base64
import hashlib
import secrets

import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.database.config import settings

# Configurações do Google OAuth
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI


class GoogleOAuthError(Exception):
    """Exceção base para erros do Google OAuth"""


class CodeVerifierNotFoundError(GoogleOAuthError):
    """Exceção quando code verifier não é encontrado"""


class TokenExchangeError(GoogleOAuthError):
    """Exceção quando há erro ao trocar código por token"""


# Escopos necessários para o login social
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Armazenamento temporário de code verifiers e user_ids (em produção, usar Redis/DB)
CODE_VERIFIERS = {}
STATE_USER_IDS = {}


def generate_code_verifier() -> str:
    """Gera um code verifier aleatório para PKCE"""
    return secrets.token_urlsafe(32)


def generate_code_challenge(code_verifier: str) -> str:
    """Gera code challenge a partir do code verifier"""
    sha256_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(sha256_hash).decode("utf-8").replace("=", "")


class GoogleOAuthManager:
    """Gerenciador de autenticação Google OAuth"""

    @staticmethod
    def get_flow() -> Flow:
        """Cria o flow de autenticação Google OAuth"""
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI],
                }
            },
            scopes=SCOPES,
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        flow.enable_code_verifier = False  # Desabilitar PKCE
        return flow

    @staticmethod
    def get_authorization_url(
        state: str | None = None, user_id: int | None = None, is_login: bool = False
    ) -> tuple[str, str]:
        """
        Gera a URL de autorização do Google com PKCE
        Retorna: (authorization_url, state)

        Args:
            state: State opcional
            user_id: ID do usuário para vinculação
            is_login: Se True, indica que é fluxo de login social (não vinculação)
        """
        # Gerar code verifier e challenge
        code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(code_verifier)

        # Armazenar code verifier usando state como chave
        if not state:
            state = secrets.token_urlsafe(16)

        CODE_VERIFIERS[state] = code_verifier

        # Armazenar info no state
        if is_login:
            STATE_USER_IDS[state] = {"is_login": True}
        elif user_id:
            STATE_USER_IDS[state] = {"user_id": user_id, "is_login": False}

        # Construir URL de autorização manualmente
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={GOOGLE_CLIENT_ID}&"
            f"redirect_uri={GOOGLE_REDIRECT_URI}&"
            f"scope={' '.join(SCOPES)}&"
            f"response_type=code&"
            f"state={state}&"
            f"code_challenge={code_challenge}&"
            f"code_challenge_method=S256&"
            f"access_type=offline&"
            f"prompt=consent"
        )

        return auth_url, state

    @staticmethod
    def exchange_code_for_credentials(code: str, state: str) -> Credentials:
        """
        Troca o código de autorização por credenciais usando requests manual com PKCE
        """
        token_url = "https://oauth2.googleapis.com/token"

        # Recuperar code verifier do state
        code_verifier = CODE_VERIFIERS.get(state)
        if not code_verifier:
            raise CodeVerifierNotFoundError(
                "Code verifier não encontrado para o state fornecido"
            )

        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
        }

        response = requests.post(token_url, data=data)

        if response.status_code != 200:
            raise TokenExchangeError(
                f"Erro ao trocar código por token: {response.text}"
            )

        token_data = response.json()

        # Limpar code verifier após uso
        CODE_VERIFIERS.pop(state, None)

        # Criar credenciais a partir do token
        credentials = Credentials(
            token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=SCOPES,
        )

        return credentials

    @staticmethod
    def credentials_to_dict(credentials: Credentials) -> dict:
        """Converte credenciais para dicionário para salvar no banco"""
        return {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
        }

    @staticmethod
    def dict_to_credentials(cred_dict: dict) -> Credentials:
        """Converte dicionário de volta para Credentials com refresh automático"""

        credentials = Credentials(
            token=cred_dict.get("token"),
            refresh_token=cred_dict.get("refresh_token"),
            token_uri=cred_dict.get("token_uri"),
            client_id=cred_dict.get("client_id"),
            client_secret=cred_dict.get("client_secret"),
            scopes=cred_dict.get("scopes"),
            expiry=cred_dict.get("expiry"),
        )

        # Verificar se o token expirou e refresh automaticamente
        if credentials.expired and credentials.refresh_token:
            print("Token expirado, fazendo refresh...")
            credentials.refresh(requests.Request())
            print("Token refresh realizado com sucesso")

        return credentials


class GoogleCalendarService:
    """Serviço para interagir com Google Calendar"""

    @staticmethod
    def get_service(credentials: Credentials):
        """Cria o serviço do Google Calendar"""
        return build("calendar", "v3", credentials=credentials)

    @staticmethod
    def get_freebusy(
        credentials: Credentials,
        time_min: str,
        time_max: str,
        calendar_id: str = "primary",
    ):
        """
        Verifica disponibilidade usando FreeBusy
        Retorna horários ocupados
        """
        service = GoogleCalendarService.get_service(credentials)

        freebusy_body = {
            "timeMin": time_min,
            "timeMax": time_max,
            "items": [{"id": calendar_id}],
        }

        freebusy = service.freebusy().query(body=freebusy_body).execute()
        return freebusy.get("calendars", {}).get(calendar_id, {}).get("busy", [])

    @staticmethod
    def get_events(
        credentials: Credentials,
        calendar_id: str = "primary",
        time_min: str | None = None,
        time_max: str | None = None,
        max_results: int = 10,
    ) -> list:
        """
        Busca eventos do Google Calendar
        time_min: formato ISO 8601 (ex: 2024-01-01T00:00:00-03:00)
        time_max: formato ISO 8601
        """
        try:
            service = GoogleCalendarService.get_service(credentials)

            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])
            return events
        except HttpError as error:
            print(f"Erro ao buscar eventos: {error}")
            return []

    @staticmethod
    def create_event(
        credentials: Credentials, event: dict, calendar_id: str = "primary"
    ) -> dict:
        """
        Cria um evento no Google Calendar
        event: dicionário com os dados do evento
        """
        try:
            service = GoogleCalendarService.get_service(credentials)
            event_result = (
                service.events().insert(calendarId=calendar_id, body=event).execute()
            )
            return event_result
        except HttpError as error:
            print(f"Erro ao criar evento: {error}")
            return None

    @staticmethod
    def update_event(
        credentials: Credentials,
        event_id: str,
        event: dict,
        calendar_id: str = "primary",
    ) -> dict:
        """
        Atualiza um evento no Google Calendar
        """
        try:
            service = GoogleCalendarService.get_service(credentials)
            event_result = (
                service.events()
                .update(calendarId=calendar_id, eventId=event_id, body=event)
                .execute()
            )
            return event_result
        except HttpError as error:
            print(f"Erro ao atualizar evento: {error}")
            return None

    @staticmethod
    def delete_event(
        credentials: Credentials, event_id: str, calendar_id: str = "primary"
    ) -> bool:
        """
        Deleta um evento do Google Calendar
        """
        try:
            service = GoogleCalendarService.get_service(credentials)
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            return True
        except HttpError as error:
            print(f"Erro ao deletar evento: {error}")
            return False

    @staticmethod
    def get_free_busy(
        credentials: Credentials, calendar_ids: list[str], time_min: str, time_max: str
    ) -> dict:
        """
        Busca horários livres/ocupados
        """
        try:
            service = GoogleCalendarService.get_service(credentials)

            body = {
                "timeMin": time_min,
                "timeMax": time_max,
                "items": [{"id": cal_id} for cal_id in calendar_ids],
            }

            free_busy = service.freebusy().query(body=body).execute()
            return free_busy
        except HttpError as error:
            print(f"Erro ao buscar free/busy: {error}")
            return {}
