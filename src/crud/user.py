from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session

from src.auth.security import get_password_hash, verify_password
from src.models import models
from src.schemas.user import UserCreate, UserUpdate


def get_user(
    db: Session,
    user_id: int | None = None,
    email: str | None = None,
):
    if not any([user_id, email]):
        raise ArgumentError("Either user_id or email must be provided")
    query = db.query(models.User)
    if user_id:
        query = query.filter(models.User.id == user_id)
    if email:
        query = query.filter(models.User.email == email)
    user = query.first()
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


def create_user(db: Session, user: UserCreate):
    db_user = models.User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        # Identificação
        nome=user.nome,
        celular=user.celular,
        cpf=user.cpf,
        data_nascimento=user.data_nascimento,
        sexo=user.sexo,
        cep=user.cep,
        rua=user.rua,
        numero=user.numero,
        bairro=user.bairro,
        cidade=user.cidade,
        estado=user.estado,
        role=user.role,
        # Perfil
        foto_perfil=user.foto_perfil,
        especialidade=user.especialidade,
        rqe=user.rqe,
        valor_consulta=user.valor_consulta,
        # Documentos
        tipo_conselho=user.tipo_conselho,
        uf_conselho=user.uf_conselho,
        numero_conselho=user.numero_conselho,
        upload_arquivo=user.upload_arquivo,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        return None
    for key, value in user.dict().items():
        if value is not None:
            setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user


def authenticate(db: Session, email: str, password: str):
    db_user = get_user(db, email=email)
    if not db_user or not verify_password(password, db_user.hashed_password):
        return None
    return db_user


# ADM
