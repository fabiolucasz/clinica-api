from pydantic import BaseModel

class Especialidades(BaseModel):
    id: int
    nome: str
    
    model_config = {"from_attributes": True}
    
class EspecialidadesCreate(BaseModel):
    nome: str
    
class EspecialidadesUpdate(BaseModel):
    nome: str
    