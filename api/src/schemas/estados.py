from pydantic import BaseModel


# Schemas básicos
class Estados(BaseModel):
    id: int
    nome: str
    uf: str
    
    model_config = {"from_attributes": True}

class EstadoCreate(BaseModel):
    nome: str
    uf: str

class EstadoUpdate(BaseModel):
    nome: str | None = None
    uf: str | None = None