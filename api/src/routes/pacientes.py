import time

from fastapi import APIRouter, HTTPException, Request

from src.crud import pacientes as crud
from src.deps.user import CurrentUser, SessionDep
from src.logging_config.auth_user import log_user_operation
from src.metrics.auth_user import MetricsManager
from src.schemas.user import (
    PacienteCreate,
    PacienteResponse,
    PacienteUpdate,
)

router = APIRouter()

# Pacientes


@router.get("/pacientes", response_model=list[PacienteResponse])
async def get_pacientes(request: Request, current_user: CurrentUser, db: SessionDep):
    start_time = time.time()

    try:
        pacientes = crud.get_pacientes(db)

        # Registra métricas de validação de token
        validation_time = time.time() - start_time
        MetricsManager.record_token_validation_time(validation_time)

        log_user_operation(
            operation="get_pacientes", user_id=current_user.id, success=True
        )
        MetricsManager.record_user_operation("read", "success")

        return pacientes
    except Exception as e:
        log_user_operation(
            operation="get_pacientes",
            user_id=current_user.id,
            success=False,
            details={"error": str(e)},
        )
        MetricsManager.record_user_operation("read", "error")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/pacientes/{id}", response_model=PacienteResponse)
async def get_paciente_by_id(id: int, current_user: CurrentUser, db: SessionDep):
    # Verificar se o usuário é admin
    if current_user.role != "administrador":
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas administradores podem acessar este recurso.",
        )

    try:
        paciente = crud.get_paciente_by_id(db, id)
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        return paciente
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/pacientes", response_model=PacienteResponse)
async def create_paciente(
    paciente: PacienteCreate, current_user: CurrentUser, db: SessionDep
):
    # Verificar se o usuário é admin
    if current_user.role != "administrador":
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas administradores podem cadastrar pacientes.",
        )

    try:
        created_paciente = crud.create_paciente(db, paciente)
        return created_paciente
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/pacientes/{id}", response_model=PacienteUpdate)
async def update_paciente(
    id: int, paciente: PacienteUpdate, current_user: CurrentUser, db: SessionDep
):
    # Verificar se o usuário é admin
    if current_user.role != "administrador":
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas administradores podem editar pacientes.",
        )

    try:
        updated_paciente = crud.update_paciente(db, id, paciente)
        if not updated_paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        return updated_paciente
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/pacientes/{id}")
async def delete_paciente(id: int, current_user: CurrentUser, db: SessionDep):
    # Verificar se o usuário é admin
    if current_user.role != "administrador":
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas administradores podem excluir pacientes.",
        )

    try:
        deleted_paciente = crud.delete_paciente(db, id)
        if not deleted_paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        return {"message": "Paciente excluído com sucesso"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
