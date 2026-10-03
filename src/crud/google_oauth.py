"""
CRUD para integração com Google OAuth (login social)
"""

import json
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.models import models


def get_google_credentials(db: Session, user_id: int):
    """Busca credenciais Google de um usuário"""
    return (
        db.query(models.GoogleCredentials)
        .filter(models.GoogleCredentials.user_id == user_id)
        .first()
    )


def create_google_credentials(db: Session, credentials: dict, user_id: int):
    """Cria credenciais Google para um usuário"""
    db_credentials = models.GoogleCredentials(
        user_id=user_id,
        google_token=credentials.get("token"),
        google_refresh_token=credentials.get("refresh_token"),
        google_token_uri=credentials.get("token_uri"),
        google_client_id=credentials.get("client_id"),
        google_client_secret=credentials.get("client_secret"),
        google_scopes=json.dumps(credentials.get("scopes", [])),
        google_expiry=(
            datetime.fromisoformat(credentials.get("expiry"))
            if credentials.get("expiry")
            else None
        ),
        is_connected=True,
    )
    db.add(db_credentials)
    db.commit()
    db.refresh(db_credentials)
    return db_credentials


def update_google_credentials(db: Session, user_id: int, credentials: dict):
    """Atualiza credenciais Google de um usuário"""
    db_credentials = get_google_credentials(db, user_id)
    if not db_credentials:
        return None

    db_credentials.google_token = credentials.get("token")
    db_credentials.google_refresh_token = credentials.get("refresh_token")
    db_credentials.google_token_uri = credentials.get("token_uri")
    db_credentials.google_client_id = credentials.get("client_id")
    db_credentials.google_client_secret = credentials.get("client_secret")
    db_credentials.google_scopes = json.dumps(credentials.get("scopes", []))
    db_credentials.google_expiry = (
        datetime.fromisoformat(credentials.get("expiry"))
        if credentials.get("expiry")
        else None
    )
    db_credentials.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(db_credentials)
    return db_credentials


def delete_google_credentials(db: Session, user_id: int):
    """Remove credenciais Google de um usuário"""
    db_credentials = get_google_credentials(db, user_id)
    if not db_credentials:
        return None

    db.delete(db_credentials)
    db.commit()
    return True


def get_credentials_dict(db: Session, user_id: int):
    """Retorna credenciais como dict para uso com Google OAuth"""
    credentials = get_google_credentials(db, user_id)
    if not credentials:
        return None

    return {
        "token": credentials.google_token,
        "refresh_token": credentials.google_refresh_token,
        "token_uri": credentials.google_token_uri,
        "client_id": credentials.google_client_id,
        "client_secret": credentials.google_client_secret,
        "scopes": json.loads(credentials.google_scopes),
        "expiry": (
            credentials.google_expiry.isoformat() if credentials.google_expiry else None
        ),
    }
