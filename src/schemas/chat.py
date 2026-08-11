from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    response: str


class LeadCreate(BaseModel):
    name: str
    whatsapp: str
    birth_date: str | None = None
    desired_specialty: str | None = None
    insurance: str | None = None
    status: str = "aguardando"


class LeadResponse(BaseModel):
    id: int
    name: str
    whatsapp: str
    birth_date: str | None
    desired_specialty: str | None
    insurance: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
