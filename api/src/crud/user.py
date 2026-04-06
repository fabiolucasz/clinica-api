from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session
from src.models import models
from src.schemas.user import MedicoBase, MedicoCreate, MedicoUpdate, MedicoResponse, PacienteBase, PacienteCreate, PacienteUpdate, UserCreate, UserUpdate
from src.auth.security import verify_password, get_password_hash

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
        upload_arquivo=user.upload_arquivo
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


#Pacientes
def get_pacientes(db: Session, skip: int = 0, limit: int = 100):
    pacientes = db.query(models.User).filter(models.User.role == "paciente").offset(skip).limit(limit).all()
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
        foto_perfil=paciente.foto_perfil
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

#Medicos
def get_medicos(db: Session, skip: int = 0, limit: int = 100):
    medicos = db.query(models.User).filter(models.User.role == "medico").offset(skip).limit(limit).all()
    return medicos

def get_medico_by_id(db: Session, id: int):
    medico = db.query(models.User).filter(models.User.id == id, models.User.role == "medico").first()
    return medico

def create_medico(db: Session, medico: MedicoCreate):
    db_medico = models.User(
        hashed_password=get_password_hash(medico.password),
        nome=medico.nome,
        email=medico.email,
        celular=medico.celular,
        cpf=medico.cpf,
        data_nascimento=medico.data_nascimento,
        sexo=medico.sexo,
        rua=medico.rua,
        numero=medico.numero,
        bairro=medico.bairro,
        cidade=medico.cidade,
        estado=medico.estado,
        cep=medico.cep,
        role="medico",
        foto_perfil=medico.foto_perfil,
        especialidade=medico.especialidade,
        rqe=medico.rqe,
        valor_consulta=medico.valor_consulta,
        tipo_conselho=medico.tipo_conselho,
        uf_conselho=medico.uf_conselho,
        numero_conselho=medico.numero_conselho,
        upload_arquivo=medico.upload_arquivo
    )
    db.add(db_medico)
    db.commit()
    db.refresh(db_medico)
    return db_medico

def update_medico(db: Session, id: int, medico: MedicoUpdate):
    db_medico = get_medico_by_id(db, id=id)
    if not db_medico:
        return None
    for key, value in medico.model_dump().items():
        if value is not None:
            setattr(db_medico, key, value)
    db.commit()
    db.refresh(db_medico)
    return db_medico

def delete_medico(db: Session, id: int):
    db_medico = get_medico_by_id(db, id=id)
    if not db_medico:
        return None
    db.delete(db_medico)
    db.commit()
    return db_medico

#ADM