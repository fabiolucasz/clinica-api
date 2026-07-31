from sqlalchemy.orm import Session, joinedload

from src.auth.security import get_password_hash
from src.models import models
from src.schemas.user import MedicoCreate, MedicoUpdate


# Medicos
def get_medicos(db: Session, skip: int = 0, limit: int = 100):
    medicos = (
        db.query(models.User)
        .filter(models.User.role == "medico")
        .offset(skip)
        .limit(limit)
        .all()
    )
    return medicos


def get_medicos_completo(db: Session, skip: int = 0, limit: int = 100):
    medicos = (
        db.query(models.User)
        .options(
            joinedload(models.User.especialidade_rel),
            joinedload(models.User.tipo_conselho_rel),
            joinedload(models.User.estado_rel),
        )
        .filter(models.User.role == "medico")
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Construir resposta com nomes relacionados
    medicos_completos = []
    for medico in medicos:
        medico_dict = {
            "id": medico.id,
            "nome": medico.nome,
            "email": medico.email,
            "celular": medico.celular,
            "cpf": medico.cpf,
            "data_nascimento": str(medico.data_nascimento),
            "sexo": medico.sexo,
            "cep": medico.cep,
            "rua": medico.rua,
            "numero": medico.numero,
            "bairro": medico.bairro,
            "cidade": medico.cidade,
            "estado": medico.estado,
            "estado_nome": medico.estado_rel.uf if medico.estado_rel else None,
            "role": medico.role,
            "foto_perfil": medico.foto_perfil,
            "especialidade": medico.especialidade,
            "especialidade_nome": (
                medico.especialidade_rel.nome if medico.especialidade_rel else None
            ),
            "rqe": medico.rqe,
            "valor_consulta": medico.valor_consulta,
            "tipo_conselho": medico.tipo_conselho,
            "tipo_conselho_nome": (
                medico.tipo_conselho_rel.nome if medico.tipo_conselho_rel else None
            ),
            "uf_conselho": medico.uf_conselho,
            "uf_conselho_nome": (
                medico.estado_rel.uf
                if medico.estado_rel and medico.uf_conselho
                else None
            ),
            "numero_conselho": medico.numero_conselho,
            "upload_arquivo": medico.upload_arquivo,
            "created_at": medico.created_at,
            "updated_at": medico.updated_at,
        }
        medicos_completos.append(medico_dict)

    return medicos_completos


def get_medico_by_id(db: Session, id: int):
    medico = (
        db.query(models.User)
        .filter(models.User.id == id, models.User.role == "medico")
        .first()
    )
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
        upload_arquivo=medico.upload_arquivo,
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
