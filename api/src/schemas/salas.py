from pydantic import BaseModel


class SalasBase(BaseModel):
    nome: str
    clinica: int


class SalasCreate(SalasBase):
    pass


class SalasUpdate(BaseModel):
    nome: str | None = None


class Salas(SalasBase):
    id: int

    model_config = {"from_attributes": True}
