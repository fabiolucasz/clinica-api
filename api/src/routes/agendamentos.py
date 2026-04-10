from fastapi import APIRouter, HTTPException, status
from src.deps.user import SessionDep, CurrentUser
from src.crud import agendamentos as crud
from src.schemas.agendamentos import AgendamentosCreate, AgendamentosUpdate
from pydantic import BaseModel

router = APIRouter()

# Status válidos para agendamentos
STATUS_VALIDOS = ['aguardando', 'confirmada', 'agendado', 'cancelada', 'realizada']

class StatusUpdate(BaseModel):
    status: str

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

@router.patch("/agendamentos/{id}/status")
async def update_agendamento_status(id: int, status_update: StatusUpdate, current_user: CurrentUser, db: SessionDep):
    """Atualiza apenas o status de um agendamento."""
    # Validar status
    if status_update.status not in STATUS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Status permitidos: {', '.join(STATUS_VALIDOS)}"
        )
    
    # Buscar agendamento
    agendamento = crud.get_agendamento(db, id)
    if not agendamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    # Atualizar status
    agendamento.status = status_update.status
    db.commit()
    db.refresh(agendamento)
    
    return agendamento
