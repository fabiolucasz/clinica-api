from pydantic import BaseModel


class VagasBase(BaseModel):
    clinica: int
    sala: int
    status: str = "disponivel"
    turno: int
    segunda: int | None = None
    terca: int | None = None
    quarta: int | None = None
    quinta: int | None = None
    sexta: int | None = None
    max_pacientes: int = 25
    pacientes_atuais: int = 0


class VagasCreate(VagasBase):
    pass


class VagasUpdate(BaseModel):
    status: str | None = None
    segunda: int | None = None
    terca: int | None = None
    quarta: int | None = None
    quinta: int | None = None
    sexta: int | None = None
    max_pacientes: int | None = None
    pacientes_atuais: int | None = None


class Vagas(VagasBase):
    id: int

    model_config = {"from_attributes": True}
