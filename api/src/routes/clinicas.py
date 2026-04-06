from fastapi import APIRouter
from src.deps.user import SessionDep

from src.crud import clinicas as crud
from src.schemas.clinicas import ClinicasCreate, ClinicasUpdate

router = APIRouter()

@router.get("/clinicas/")
async def get_clinicas(db: SessionDep):
    return crud.get_clinicas(db)

@router.get("/clinicas/{id}")
async def get_clinica(id: int, db: SessionDep):
    return crud.get_clinica_by_id(db, id)

@router.post("/clinicas/")
async def create_clinica(clinica: ClinicasCreate, db: SessionDep):
    return crud.create_clinica(db, clinica)

@router.put("/clinicas/{id}")
async def update_clinica(id: int, clinica: ClinicasUpdate, db: SessionDep):
    return crud.update_clinica(db, id, clinica)

@router.delete("/clinicas/{id}")
async def delete_clinica(id: int, db: SessionDep):
    return crud.delete_clinica(db, id)
