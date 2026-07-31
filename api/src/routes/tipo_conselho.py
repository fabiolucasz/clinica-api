from fastapi import APIRouter

from src.crud import tipo_conselho as crud
from src.deps.user import CurrentUser, SessionDep
from src.schemas.tipo_conselho import TiposConselhoCreate, TiposConselhoUpdate

router = APIRouter()


@router.get("/tipo-conselho/")
async def get_tipo_conselho(current_user: CurrentUser, db: SessionDep):
    return crud.get_tipo_conselho(db)


@router.get("/tipo-conselho/{id}")
async def get_tipo_conselho_by_id(id: int, current_user: CurrentUser, db: SessionDep):
    return crud.get_tipo_conselho_by_id(db, id)


@router.post("/tipo-conselho/")
async def create_tipo_conselho(
    tipo_conselho: TiposConselhoCreate, current_user: CurrentUser, db: SessionDep
):
    return crud.create_tipo_conselho(db, tipo_conselho)


@router.put("/tipo-conselho/{id}")
async def update_tipo_conselho(
    id: int,
    tipo_conselho: TiposConselhoUpdate,
    current_user: CurrentUser,
    db: SessionDep,
):
    return crud.update_tipo_conselho(db, id, tipo_conselho)


@router.delete("/tipo-conselho/{id}")
async def delete_tipo_conselho(id: int, current_user: CurrentUser, db: SessionDep):
    return crud.delete_tipo_conselho(db, id)
