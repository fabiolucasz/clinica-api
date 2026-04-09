from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
from src.deps.user import SessionDep, CurrentUser
from src.crud import user as crud
from src.schemas.user import Token
from src.auth import security
from datetime import timedelta
from src.database.config import settings

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/login-json")
async def login_json(request: Request, db: SessionDep, login_data: LoginRequest) -> Token:
    """
    Endpoint para login via JSON (para aplicações externas)
    """
    client_ip = request.client.host
    
    # Autenticar usuário
    user = crud.authenticate(
        db=db, 
        email=login_data.email, 
        password=login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    if not security.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Gerar token
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
            "is_active": current_user.is_active
        }
    }