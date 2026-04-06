from fastapi import APIRouter
from src.deps.user import SessionDep

from src.crud import calendario_clinica as crud
from src.schemas.calendario_clinica import CalendarioClinicaCreate, CalendarioClinicaUpdate

router = APIRouter()

@router.get("/calendario-clinica/")
async def get_calendario_clinica(db: SessionDep):
    return crud.get_calendario_clinica(db)

@router.get("/calendario-clinica/{clinica_id}")
async def get_calendario_clinica_by_clinica(clinica_id: int, db: SessionDep):
    return crud.get_calendario_clinica_by_clinica(db, clinica_id)

@router.get("/calendario-clinica/data/{data}")
async def get_calendario_clinica_by_data(data: str, db: SessionDep):
    return crud.get_calendario_clinica_by_data(db, data)


@router.post("/calendario-clinica/")
async def create_calendario_clinica(calendario_clinica: CalendarioClinicaCreate, db: SessionDep):
    return crud.create_calendario_clinica(db, calendario_clinica)

@router.put("/calendario-clinica/{id}")
async def update_calendario_clinica(id: int, calendario_clinica: CalendarioClinicaUpdate, db: SessionDep):
    return crud.update_calendario_clinica(db, id, calendario_clinica)

@router.delete("/calendario-clinica/{id}")
async def delete_calendario_clinica(id: int, db: SessionDep):
    return crud.delete_calendario_clinica(db, id)

