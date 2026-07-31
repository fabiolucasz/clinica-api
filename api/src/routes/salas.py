from fastapi import APIRouter

from src.crud import salas as crud
from src.deps.user import CurrentUser, SessionDep
from src.schemas.salas import SalasCreate, SalasUpdate

router = APIRouter()


@router.get("/salas/")
async def get_salas(current_user: CurrentUser, db: SessionDep):
    return crud.get_salas(db)


@router.get("/salas/{id}")
async def get_sala(id: int, current_user: CurrentUser, db: SessionDep):
    return crud.get_sala(db, id)


@router.get("/salas/clinica/{clinica_id}")
async def get_sala_by_clinica_id(
    clinica_id: int, current_user: CurrentUser, db: SessionDep
):
    return crud.get_sala_by_clinica_id(db, clinica_id)


@router.post("/salas/")
async def create_sala(sala: SalasCreate, current_user: CurrentUser, db: SessionDep):
    return crud.create_sala(db, sala)


@router.put("/salas/{id}")
async def update_sala(
    id: int, sala: SalasUpdate, current_user: CurrentUser, db: SessionDep
):
    return crud.update_sala(db, id, sala)


@router.delete("/salas/{id}")
async def delete_sala(id: int, current_user: CurrentUser, db: SessionDep):
    return crud.delete_sala(db, id)
