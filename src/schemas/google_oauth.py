"""
Schemas para integração com Google Calendar
"""

from datetime import datetime

from pydantic import BaseModel


class GoogleCredentialsCreate(BaseModel):
    """Schema para criar vinculação com Google"""

    user_id: int
    google_token: str
    google_refresh_token: str
    google_token_uri: str
    google_client_id: str
    google_client_secret: str
    google_scopes: list[str]
    google_expiry: str | None = None


class GoogleCredentialsResponse(BaseModel):
    """Schema para resposta de credenciais Google"""

    id: int
    user_id: int
    is_connected: bool
    connected_at: datetime | None = None

    class Config:
        from_attributes = True


class GoogleEventCreate(BaseModel):
    """Schema para criar evento no Google Calendar"""

    summary: str
    description: str | None = None
    start: dict  # {'dateTime': '2024-01-01T10:00:00-03:00'} ou {'date': '2024-01-01'}
    end: dict
    location: str | None = None
    attendees: list[dict] | None = None
    reminders: dict | None = None


class GoogleEventResponse(BaseModel):
    """Schema para resposta de evento do Google Calendar"""

    id: str
    summary: str
    description: str | None = None
    start: dict
    end: dict
    location: str | None = None
    attendees: list[dict] | None = None
    created: str | None = None
    updated: str | None = None


class GoogleSyncRequest(BaseModel):
    """Schema para sincronizar agenda"""

    medico_id: int
    start_date: str  # ISO 8601
    end_date: str  # ISO 8601
