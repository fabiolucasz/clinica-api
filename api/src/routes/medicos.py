import time
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from src.crud import medicos as crud
from src.crud.user import get_user
from src.schemas.user import MedicoCreate, MedicoUpdate, MedicoResponse, MedicoResponseCompleto
from src.auth import security
from src.deps.user import CurrentUser, SessionDep
from src.logging_config.auth_user import log_auth_attempt, log_user_operation
from src.metrics.auth_user import MetricsManager
from src.auth.auth_rate_limiter import check_rate_limit, login_limiter, signup_limiter, check_brute_force, reset_failed_attempts

router = APIRouter()

# Médicos - CRUD Completo


@router.get("/medicos", response_model=list[MedicoResponse])
async def get_medicos(request: Request, current_user: CurrentUser, db: SessionDep):
    # Verificar se o usuário é admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem acessar este recurso.")
    
    start_time = time.time()
    
    try:
        medicos = crud.get_medicos(db)
        
        # Registra métricas de validação de token
        validation_time = time.time() - start_time
        MetricsManager.record_token_validation_time(validation_time)
        
        log_user_operation(
            operation="get_medicos",
            user_id=current_user.id,
            success=True
        )
        MetricsManager.record_user_operation("read", "success")
        
        return medicos
    except Exception as e:
        log_user_operation(
            operation="get_medicos",
            user_id=current_user.id,
            success=False,
            details={"error": str(e)}
        )
        MetricsManager.record_user_operation("read", "error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/medicos/completo", response_model=list[MedicoResponseCompleto])
async def get_medicos_completo(request: Request, current_user: CurrentUser, db: SessionDep):
    # Verificar se o usuário é admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem acessar este recurso.")
    
    start_time = time.time()
    
    try:
        medicos = crud.get_medicos_completo(db)
        
        # Registra métricas de validação de token
        validation_time = time.time() - start_time
        MetricsManager.record_token_validation_time(validation_time)
        
        log_user_operation(
            operation="get_medicos_completo",
            user_id=current_user.id,
            success=True
        )
        MetricsManager.record_user_operation("read", "success")
        
        return medicos
    except Exception as e:
        log_user_operation(
            operation="get_medicos_completo",
            user_id=current_user.id,
            success=False,
            details={"error": str(e)}
        )
        MetricsManager.record_user_operation("read", "error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )



@router.get("/medicos/{id}", response_model=MedicoResponse)
async def get_medico_by_id(id: int, current_user: CurrentUser, db: SessionDep):
    # Verificar se o usuário é admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem acessar este recurso.")
    
    try:
        medico = crud.get_medico_by_id(db, id)
        if not medico:
            raise HTTPException(status_code=404, detail="Médico não encontrado")
        return medico
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.post("/medicos", response_model=MedicoResponse)
async def create_medico(medico: MedicoCreate, current_user: CurrentUser, db: SessionDep):
    # Verificar se o usuário é admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem cadastrar médicos.")
    
    try:
        # Verificar se email já existe
        existing_user = get_user(db=db, email=medico.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        created_medico = crud.create_medico(db, medico)
        return created_medico
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.put("/medicos/{id}", response_model=MedicoResponse)
async def update_medico(id: int, medico: MedicoUpdate, current_user: CurrentUser, db: SessionDep):
    # Verificar se o usuário é admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem editar médicos.")
    
    try:
        updated_medico = crud.update_medico(db, id=id, medico=medico)
        if not updated_medico:
            raise HTTPException(status_code=404, detail="Médico não encontrado")
        return updated_medico
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.delete("/medicos/{id}")
async def delete_medico(id: int, current_user: CurrentUser, db: SessionDep):
    # Verificar se o usuário é admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem excluir médicos.")
    
    try:
        deleted_medico = crud.delete_medico(db, id=id)
        if not deleted_medico:
            raise HTTPException(status_code=404, detail="Médico não encontrado")
        return {"message": "Médico excluído com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
