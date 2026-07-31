from sqlalchemy.orm import Session

from src.models import models
from src.schemas.salas import SalasCreate, SalasUpdate


def get_salas(db: Session):
    return db.query(models.Salas).all()


def get_sala(db: Session, id: int):
    return db.query(models.Salas).filter(models.Salas.id == id).first()


def get_sala_by_clinica_id(db: Session, clinica_id: int):
    return db.query(models.Salas).filter(models.Salas.clinica == clinica_id).all()


def create_sala(db: Session, sala: SalasCreate):
    db_sala = models.Salas(**sala.model_dump())
    db.add(db_sala)
    db.commit()
    db.refresh(db_sala)
    return db_sala


def update_sala(db: Session, id: int, sala: SalasUpdate):
    db_sala = db.query(models.Salas).filter(models.Salas.id == id).first()
    if db_sala:
        for key, value in sala.model_dump().items():
            setattr(db_sala, key, value)
        db.commit()
        db.refresh(db_sala)
    return db_sala


def delete_sala(db: Session, id: int):
    db_sala = db.query(models.Salas).filter(models.Salas.id == id).first()
    if db_sala:
        db.delete(db_sala)
        db.commit()
    return db_sala
