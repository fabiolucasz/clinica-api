from fastapi import APIRouter
from src.deps.user import SessionDep

from src.crud import especialidades as crud
from src.schemas.especialidades import EspecialidadesCreate, EspecialidadesUpdate

router = APIRouter()

@router.get("/especialidades/")
async def get_especialidades(db: SessionDep):
    return crud.get_especialidades(db)

@router.get("/especialidades/{id}")
async def get_especialidade(id: int, db: SessionDep):
    return crud.get_especialidade(db, id)

@router.post("/especialidades/")
async def create_especialidade(especialidade: EspecialidadesCreate, db: SessionDep):
    return crud.create_especialidade(db, especialidade)

@router.put("/especialidades/{id}")
async def update_especialidade(id: int, especialidade: EspecialidadesUpdate, db: SessionDep):
    return crud.update_especialidade(db, id, especialidade)

@router.delete("/especialidades/{id}")
async def delete_especialidade(id: int, db: SessionDep):
    return crud.delete_especialidade(db, id)