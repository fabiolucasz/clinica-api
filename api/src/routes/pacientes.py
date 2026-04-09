import time
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from src.crud import pacientes as crud
from src.schemas.user import PacienteBase, MedicoBase, PacienteCreate, PacienteUpdate, PacienteResponse, MedicoCreate, MedicoUpdate, MedicoResponse, MedicoResponseCompleto, UserCreate, UserUpdate, Token, User
from src.auth import security
from src.database.config import settings
from src.database.connection import engine
from src.deps.user import CurrentUser, SessionDep
from src.logging_config.auth_user import log_auth_attempt, log_user_operation
from src.metrics.auth_user import MetricsManager
from src.auth.auth_rate_limiter import check_rate_limit, login_limiter, signup_limiter, check_brute_force, reset_failed_attempts

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
            operation="get_pacientes",
            user_id=current_user.id,
            success=True
        )
        MetricsManager.record_user_operation("read", "success")
        
        return pacientes
    except Exception as e:
        log_user_operation(
            operation="get_pacientes",
            user_id=current_user.id,
            success=False,
            details={"error": str(e)}
        )
        MetricsManager.record_user_operation("read", "error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/pacientes/{id}", response_model=PacienteResponse)
async def get_paciente_by_id(id: int, db: SessionDep):
    try:
        paciente = crud.get_paciente_by_id(db, id)
        return paciente
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.post("/pacientes", response_model=PacienteResponse)
async def create_paciente(paciente: PacienteCreate, db: SessionDep):
    try:
        paciente = crud.create_paciente(db, paciente)
        return paciente
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.put("/pacientes/{id}", response_model=PacienteUpdate)
async def update_paciente(id: int, paciente: PacienteUpdate, db: SessionDep):
    try:
        paciente = crud.update_paciente(db, id, paciente)
        return paciente
    except:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.delete("/pacientes/{id}")
async def delete_paciente(id: int, db: SessionDep):
    try:
        paciente = crud.delete_paciente(db, id)
        return paciente
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
