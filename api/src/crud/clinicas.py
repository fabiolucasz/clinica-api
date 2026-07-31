from sqlalchemy.orm import Session

from src.models import models
from src.schemas.clinicas import ClinicasCreate, ClinicasUpdate


def get_clinicas(db: Session):
    try:
        results = (
            db.query(models.Clinicas, models.Estados)
            .join(models.Estados, models.Clinicas.estado == models.Estados.id)
            .all()
        )

        if not results:
            return {"message": "Nenhuma clínica encontrada", "status_code": 404}

        return [
            {
                "id": clinica.id,
                "nome": clinica.nome,
                "cep": clinica.cep,
                "rua": clinica.rua,
                "numero": clinica.numero,
                "bairro": clinica.bairro,
                "cidade": clinica.cidade,
                "estado": clinica.estado,
                "celular": clinica.celular,
                "celular2": clinica.celular2,
                "cnpj": clinica.cnpj,
                "email": clinica.email,
                "estado_nome": estado.nome,
                "estado_uf": estado.uf,
            }
            for clinica, estado in results
        ]
    except Exception as e:
        return {"message": "Erro ao buscar clínicas", "error": str(e)}


def get_clinica_by_id(db: Session, id: int):
    try:
        # Buscar clínica com estado
        clinica_estado = (
            db.query(models.Clinicas, models.Estados)
            .join(models.Estados, models.Clinicas.estado == models.Estados.id)
            .filter(models.Clinicas.id == id)
            .first()
        )

        if not clinica_estado:
            return {"message": "Clínica não encontrada", "status_code": 404}

        clinica, estado = clinica_estado

        # Buscar salas da clínica
        salas = (
            db.query(models.Salas, models.Clinicas)
            .join(models.Clinicas, models.Salas.clinica == models.Clinicas.id)
            .filter(models.Salas.clinica == id)
            .all()
        )

        return [
            {
                "id": clinica.id,
                "nome": clinica.nome,
                "cep": clinica.cep,
                "rua": clinica.rua,
                "numero": clinica.numero,
                "bairro": clinica.bairro,
                "cidade": clinica.cidade,
                "estado": clinica.estado,
                "celular": clinica.celular,
                "celular2": clinica.celular2,
                "email": clinica.email,
                "cnpj": clinica.cnpj,
                "estado_nome": estado.nome,
                "estado_uf": estado.uf,
                "salas": salas,
            }
        ]
    except Exception as e:
        return {"message": "Erro ao buscar clínica", "error": str(e)}


def create_clinica(db: Session, clinica: ClinicasCreate):
    db_clinica = models.Clinicas(**clinica.model_dump())
    db.add(db_clinica)
    db.commit()
    db.refresh(db_clinica)
    return db_clinica


def update_clinica(db: Session, id: int, clinica: ClinicasUpdate):
    db_clinica = db.query(models.Clinicas).filter(models.Clinicas.id == id).first()
    if db_clinica:
        for key, value in clinica.model_dump().items():
            setattr(db_clinica, key, value)
        db.commit()
        db.refresh(db_clinica)
    return db_clinica


def delete_clinica(db: Session, id: int):
    db_clinica = db.query(models.Clinicas).filter(models.Clinicas.id == id).first()
    if db_clinica:
        db.delete(db_clinica)
        db.commit()
    return db_clinica
