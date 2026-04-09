from fastapi import APIRouter
from src.deps.user import SessionDep, CurrentUser
from src.crud import agendamentos as crud
from src.schemas.agendamentos import AgendamentosCreate, AgendamentosUpdate

router = APIRouter()

@router.get("/agendamentos/")
async def get_agendamentos(current_user: CurrentUser, db: SessionDep):
    return crud.get_agendamentos(db)

@router.get("/agendamentos/{id}")
async def get_agendamento(id: int, current_user: CurrentUser, db: SessionDep):
    return crud.get_agendamento(db, id)

@router.post("/agendamentos/")
async def create_agendamento(agendamento: AgendamentosCreate, current_user: CurrentUser, db: SessionDep):
    return crud.create_agendamento(db, agendamento)

@router.put("/agendamentos/{id}")
async def update_agendamento(id: int, agendamento: AgendamentosUpdate, current_user: CurrentUser, db: SessionDep):
    return crud.update_agendamento(db, id, agendamento)

@router.delete("/agendamentos/{id}")
async def delete_agendamento(id: int, current_user: CurrentUser, db: SessionDep):
    return crud.delete_agendamento(db, id)
