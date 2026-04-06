from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt
from passlib.context import CryptContext
from src.database.config import settings
#from src.core.crud import get_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
    
def verify_password(plain_password: str, hashed_password: str):
    # Convert to bytes and truncate to 72 bytes for consistency
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    import bcrypt
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    
# def authenticate(session: Session, email: str, password: str):
#     db_user = get_user(db=session, email=email)
#     if not db_user or not verify_password(password, db_user.hashed_password):
#         return None
#     return db_user

def get_password_hash(password: str):
    # Convert to bytes and ensure it's not longer than 72 bytes for bcrypt
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    # Use bytes directly to avoid encoding issues
    import bcrypt
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')