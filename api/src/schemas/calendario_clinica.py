from pydantic import BaseModel

class CalendarioClinica(BaseModel):
    id: int
    clinica_id: int
    data_feriado: int
    nome_feriado: str
    aberta: bool = True
    
    model_config = {"from_attributes": True}

class CalendarioClinicaCreate(BaseModel):
    clinica_id: int
    data_feriado: int
    nome_feriado: str

class CalendarioClinicaUpdate(BaseModel):
    clinica_id: int
    data_feriado: int
    nome_feriado: str
