from fastapi import APIRouter
from src.deps.user import SessionDep
from src.crud import vagas
from src.schemas.vagas import VagasCreate, VagasUpdate
    
router = APIRouter()

@router.get("/vagas")
async def get_vagas(db: SessionDep):
    return vagas.get_vagas(db)

@router.get("/vagas/{id}")
async def get_vaga(id: int, db: SessionDep):
    return vagas.get_vaga(db, id)

@router.get("/vagas/clinica/{clinica_id}")
async def get_vaga_by_clinica_id(clinica_id: int, db: SessionDep):
    return vagas.get_vaga_by_clinica_id(db, clinica_id)

@router.post("/vagas")
async def create_vaga(vaga: VagasCreate, db: SessionDep):
    return vagas.create_vaga(db, vaga)

@router.put("/vagas/{id}")
async def update_vaga(id: int, vaga: VagasUpdate, db: SessionDep):
    return vagas.update_vaga(db, id, vaga)

@router.delete("/vagas/{id}")
async def delete_vaga(id: int, db: SessionDep):
    return vagas.delete_vaga(db, id)
