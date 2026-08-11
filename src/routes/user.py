import time
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth import security
from src.auth.auth_rate_limiter import (
    check_rate_limit,
    login_limiter,
    signup_limiter,
)
from src.crud import user as crud
from src.database.config import settings
from src.deps.user import CurrentUser, SessionDep
from src.logging_config.auth_user import log_user_operation
from src.metrics.auth_user import MetricsManager
from src.schemas.user import Token, User, UserCreate

router = APIRouter()
# novo
from fastapi import APIRouter

router = APIRouter()


@router.post("/login/access-token")
async def login_access_token(
    request: Request, db: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Rate limited: 5 attempts per minute per IP.
    """
    # Rate limiting check
    check_rate_limit(request, login_limiter, "login")

    # Authenticate user
    user = crud.authenticate(
        db=db, email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/auth/validate-token")
async def validate_token(current_user: CurrentUser) -> dict:
    """
    Valida token e retorna dados do usuário
    """
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "nome": current_user.nome,
            "role": current_user.role,
            "is_active": current_user.is_active,
        },
    }


# antigo


@router.post("/signup", response_model=User)
async def create_user(request: Request, db: SessionDep, user: UserCreate):

    # Verificar rate limit
    check_rate_limit(request, signup_limiter, "/signup")

    db_user = crud.get_user(db=db, email=user.email)
    if db_user:
        log_user_operation(
            operation="user_creation",
            user_id=0,
            success=False,
            details={"email": user.email, "reason": "email_exists"},
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
            details={"email": user.email},
        )
        MetricsManager.record_user_operation("create", "success")
        return created_user
    except Exception as e:
        log_user_operation(
            operation="user_creation",
            user_id=0,
            success=False,
            details={"email": user.email, "error": str(e)},
        )
        MetricsManager.record_user_operation("create", "error")
        raise HTTPException(status_code=500, detail="Internal server error")


# só pode deletar se a role for administrador
@router.delete("/users/{user_id}", response_model=User)
async def delete_user(
    request: Request, current_user: CurrentUser, db: SessionDep, user_id: int
):
    start_time = time.time()

    # Verificar se o usuário logado é administrador
    if current_user.role != "administrador":
        log_user_operation(
            operation="delete_user_profile",
            user_id=current_user.id,
            success=False,
            details={
                "error": "Unauthorized - admin role required",
                "target_user_id": user_id,
            },
        )
        MetricsManager.record_user_operation("delete", "unauthorized")
        raise HTTPException(
            status_code=403, detail="Apenas administradores podem deletar usuários"
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
            details={"deleted_user_id": user_id},
        )
        MetricsManager.record_user_operation("delete", "success")

        return db_user
    except Exception as e:
        log_user_operation(
            operation="delete_user_profile",
            user_id=current_user.id,
            success=False,
            details={"error": str(e), "target_user_id": user_id},
        )
        MetricsManager.record_user_operation("delete", "error")
        raise HTTPException(status_code=500, detail="Internal server error")
