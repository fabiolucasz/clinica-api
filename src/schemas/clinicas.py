from datetime import datetime

from pydantic import BaseModel, EmailStr


class ClinicasBase(BaseModel):
    nome: str
    cnpj: str = "00.000.000/0000-00"
    email: EmailStr
    celular: str
    celular2: str | None = None
    cep: str
    rua: str
    numero: str
    bairro: str
    cidade: str
    estado: int


class ClinicasCreate(ClinicasBase):
    pass


class ClinicasUpdate(BaseModel):
    nome: str | None = None
    cnpj: str | None = None
    email: EmailStr | None = None
    celular: str | None = None
    celular2: str | None = None
    cep: str | None = None
    rua: str | None = None
    numero: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    estado: int | None = None


class Clinicas(ClinicasBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
