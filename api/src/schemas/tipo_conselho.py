from pydantic import BaseModel

class TiposConselhoCreate(BaseModel):
    nome: str
    
class TiposConselhoUpdate(BaseModel):
    nome: str | None = None
    
class TiposConselho(BaseModel):
    id: int
    nome: str | None = None
    
    model_config = {"from_attributes": True}