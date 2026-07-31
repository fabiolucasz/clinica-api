from sqlalchemy.orm import Session

from src.auth.security import get_password_hash
from src.models import models
from src.schemas.user import PacienteCreate, PacienteUpdate


# Pacientes
def get_pacientes(db: Session, skip: int = 0, limit: int = 100):
    pacientes = (
        db.query(models.User)
        .filter(models.User.role == "paciente")
        .offset(skip)
        .limit(limit)
        .all()
    )
    return pacientes


def get_paciente_by_id(db: Session, id: int):
    paciente = db.query(models.User).filter(models.User.id == id).first()
    return paciente


def create_paciente(db: Session, paciente: PacienteCreate):
    db_paciente = models.User(
        hashed_password=get_password_hash(paciente.password),
        nome=paciente.nome,
        email=paciente.email,
        celular=paciente.celular,
        cpf=paciente.cpf,
        data_nascimento=paciente.data_nascimento,
        sexo=paciente.sexo,
        cep=paciente.cep,
        rua=paciente.rua,
        numero=paciente.numero,
        bairro=paciente.bairro,
        cidade=paciente.cidade,
        estado=paciente.estado,
        role="paciente",
        foto_perfil=paciente.foto_perfil,
    )
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente


def update_paciente(db: Session, id: int, paciente: PacienteUpdate):
    db_paciente = get_paciente_by_id(db, id=id)
    if not db_paciente:
        return None
    for key, value in paciente.dict().items():
        if value is not None:
            setattr(db_paciente, key, value)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente


def delete_paciente(db: Session, id: int):
    db_paciente = get_paciente_by_id(db, id=id)
    if not db_paciente:
        return None
    db.delete(db_paciente)
    db.commit()
    return db_paciente
