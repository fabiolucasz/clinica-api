from sqlalchemy.orm import Session

from src.models import models
from src.schemas.vagas import VagasCreate, VagasUpdate


def get_vagas(db: Session):
    return db.query(models.Vagas).all()


def get_vaga(db: Session, id: int):
    return db.query(models.Vagas).filter(models.Vagas.id == id).first()


def get_vaga_by_clinica_id(db: Session, clinica_id: int):
    return db.query(models.Vagas).filter(models.Vagas.clinica == clinica_id).all()


def create_vaga(db: Session, vaga: VagasCreate):
    db_vaga = models.Vagas(**vaga.model_dump())
    db.add(db_vaga)
    db.commit()
    db.refresh(db_vaga)
    return db_vaga


def update_vaga(db: Session, id: int, vaga: VagasUpdate):
    db_vaga = db.query(models.Vagas).filter(models.Vagas.id == id).first()
    if db_vaga:
        for key, value in vaga.model_dump().items():
            setattr(db_vaga, key, value)
        db.commit()
        db.refresh(db_vaga)
    return db_vaga


def delete_vaga(db: Session, id: int):
    db_vaga = db.query(models.Vagas).filter(models.Vagas.id == id).first()
    if db_vaga:
        db.delete(db_vaga)
        db.commit()
    return db_vaga
