import time
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from src.crud import user as crud
from src.schemas.user import UserCreate,Token, User
from src.auth import security
from src.database.config import settings
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
