from datetime import datetime

from pydantic import BaseModel


class AgendamentosBase(BaseModel):
    clinica: int
    sala: int
    paciente: int
    medico: int
    data_consulta: datetime
    turno: int
    status: str = "agendado"


class AgendamentosCreate(AgendamentosBase):
    pass


class AgendamentosUpdate(BaseModel):
    status: str | None = None
    data_consulta: datetime | None = None
    turno: int | None = None
    hora_inicio: str | None = None
    hora_fim: str | None = None


class Agendamentos(AgendamentosBase):
    id: int

    model_config = {"from_attributes": True}
