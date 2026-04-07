import time
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from src.crud import user as crud
from src.models import models
from src.schemas.user import PacienteBase, MedicoBase, PacienteCreate, PacienteUpdate, PacienteResponse, MedicoCreate, MedicoUpdate, MedicoResponse, MedicoResponseCompleto, UserCreate, UserUpdate, Token, User
from src.auth import security
from src.database.config import settings
from src.database.connection import engine
from src.deps.user import CurrentUser, SessionDep
from src.logging_config.auth_user import log_auth_attempt, log_user_operation
from src.metrics.auth_user import MetricsManager
from src.auth.auth_rate_limiter import check_rate_limit, login_limiter, signup_limiter, check_brute_force, reset_failed_attempts




router = APIRouter()

@router.post("/login/access-token")
async def login(request: Request, db: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
          ) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    client_ip = request.client.host
    
    # Verificar rate limit
    check_rate_limit(request, login_limiter, "/login/access-token")
    
    # Verificar brute force
    if check_brute_force(client_ip, form_data.username):
        log_auth_attempt(
            email=form_data.username,
            ip=client_ip,
            success=False,
            reason="brute_force_detected",
            endpoint="/login/access-token"
        )
        MetricsManager.record_auth_attempt("blocked", client_ip, "/login/access-token")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please try again later."
        )
    
    user = crud.authenticate(
        db=db, 
        email=form_data.username, 
        password=form_data.password
    )
    
    if not user:
        log_auth_attempt(
            email=form_data.username,
            ip=client_ip,
            success=False,
            reason="invalid_credentials",
            endpoint="/login/access-token"
        )
        MetricsManager.record_auth_attempt("failed", client_ip, "/login/access-token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not security.verify_password(form_data.password, user.hashed_password):
        log_auth_attempt(
            email=form_data.username,
            ip=client_ip,
            success=False,
            reason="invalid_password",
            endpoint="/login/access-token"
        )
        MetricsManager.record_auth_attempt("failed", client_ip, "/login/access-token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Login bem-sucedido
    reset_failed_attempts(client_ip, form_data.username)
    log_auth_attempt(
        email=form_data.username,
        ip=client_ip,
        success=True,
        endpoint="/login/access-token"
    )
    MetricsManager.record_auth_attempt("success", client_ip, "/login/access-token")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )
    
@router.post("/signup", response_model=User)
async def create_user(request: Request, db: SessionDep, user: UserCreate):
    client_ip = request.client.host
    
    # Verificar rate limit
    check_rate_limit(request, signup_limiter, "/signup")
    
    db_user = crud.get_user(db=db, email=user.email)
    if db_user:
        log_user_operation(
            operation="user_creation",
            user_id=0,
            success=False,
            details={"email": user.email, "reason": "email_exists"}
        )
        MetricsManager.record_user_operation("create", "failed")
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    
    try:
        created_user = crud.create_user(db, user)
        log_user_operation(
            operation="user_creation",
            user_id=created_user.id,
            success=True,
            details={"email": user.email}
        )
        MetricsManager.record_user_operation("create", "success")
        return created_user
    except Exception as e:
        log_user_operation(
            operation="user_creation",
            user_id=0,
            success=False,
            details={"email": user.email, "error": str(e)}
        )
        MetricsManager.record_user_operation("create", "error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/users/me", response_model=User)
async def read_users_me(request: Request, current_user: CurrentUser, db: SessionDep):
    start_time = time.time()
    
    try:
        db_user = crud.get_user(db, user_id=current_user.id)
        
        # Registra métricas de validação de token
        validation_time = time.time() - start_time
        MetricsManager.record_token_validation_time(validation_time)
        
        log_user_operation(
            operation="get_user_profile",
            user_id=current_user.id,
            success=True
        )
        MetricsManager.record_user_operation("read", "success")
        
        return db_user
    except Exception as e:
        log_user_operation(
            operation="get_user_profile",
            user_id=current_user.id,
            success=False,
            details={"error": str(e)}
        )
        MetricsManager.record_user_operation("read", "error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/medicos", response_model=list[MedicoResponse])
async def get_medicos(request: Request, current_user: CurrentUser, db: SessionDep):
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


@router.put("/users/{user_id}", response_model=User)
async def update_user(request: Request, current_user: CurrentUser, db: SessionDep, user: UserUpdate, user_id: int):
    start_time = time.time()
    
    try:
        db_user = crud.update_user(db, user_id=user_id, user=user)
        
        # Registra métricas de validação de token
        validation_time = time.time() - start_time
        MetricsManager.record_token_validation_time(validation_time)
        
        log_user_operation(
            operation="update_user_profile",
            user_id=current_user.id,
            success=True
        )
        MetricsManager.record_user_operation("update", "success")
        
        return db_user
    except Exception as e:
        log_user_operation(
            operation="update_user_profile",
            user_id=current_user.id,
            success=False,
            details={"error": str(e)}
        )
        MetricsManager.record_user_operation("update", "error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

# só pode deletar se a role for administrador
@router.delete("/users/{user_id}", response_model=User)
async def delete_user(request: Request, current_user: CurrentUser, db: SessionDep, user_id: int):
    start_time = time.time()
    
    # Verificar se o usuário logado é administrador
    if current_user.role != "administrador":
        log_user_operation(
            operation="delete_user_profile",
            user_id=current_user.id,
            success=False,
            details={"error": "Unauthorized - admin role required", "target_user_id": user_id}
        )
        MetricsManager.record_user_operation("delete", "unauthorized")
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem deletar usuários"
        )
    
    try:
        db_user = crud.delete_user(db, user_id=user_id)
        
        # Registra métricas de validação de token
        validation_time = time.time() - start_time
        MetricsManager.record_token_validation_time(validation_time)
        
        log_user_operation(
            operation="delete_user_profile",
            user_id=current_user.id,
            success=True,
            details={"deleted_user_id": user_id}
        )
        MetricsManager.record_user_operation("delete", "success")
        
        return db_user
    except Exception as e:
        log_user_operation(
            operation="delete_user_profile",
            user_id=current_user.id,
            success=False,
            details={"error": str(e), "target_user_id": user_id}
        )
        MetricsManager.record_user_operation("delete", "error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


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


# Médicos - CRUD Completo

@router.get("/medicos/{id}", response_model=MedicoResponse)
async def get_medico_by_id(id: int, db: SessionDep):
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
async def create_medico(medico: MedicoCreate, db: SessionDep):
    try:
        # Verificar se email já existe
        existing_user = crud.get_user(db=db, email=medico.email)
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
async def update_medico(id: int, medico: MedicoUpdate, db: SessionDep):
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
async def delete_medico(id: int, db: SessionDep):
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
