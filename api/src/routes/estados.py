from fastapi import APIRouter

from src.crud import estados as crud
from src.deps.user import CurrentUser, SessionDep
from src.schemas.estados import EstadoCreate, Estados, EstadoUpdate

router = APIRouter()


@router.get("/estados/", response_model=list[Estados])
async def get_estados(current_user: CurrentUser, db: SessionDep):
    return crud.get_estados(db)


@router.get("/estados/{id}", response_model=Estados)
async def get_estado(id: int, current_user: CurrentUser, db: SessionDep):
    return crud.get_estado(db, id)


@router.post("/estados/", response_model=Estados)
async def create_estado(
    estado: EstadoCreate, current_user: CurrentUser, db: SessionDep
):
    return crud.create_estado(db, estado)


@router.put("/estados/{id}", response_model=Estados)
async def update_estado(
    id: int, estado: EstadoUpdate, current_user: CurrentUser, db: SessionDep
):
    return crud.update_estado(db, id, estado)


@router.delete("/estados/{id}")
async def delete_estado(id: int, current_user: CurrentUser, db: SessionDep):
    return crud.delete_estado(db, id)
