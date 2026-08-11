from sqlalchemy.orm import Session

from src.models import models
from src.schemas.agendamentos import AgendamentosCreate, AgendamentosUpdate


def get_agendamentos(db: Session):
    return db.query(models.Agendamentos).all()


def get_agendamento(db: Session, id: int):
    return db.query(models.Agendamentos).filter(models.Agendamentos.id == id).first()


def create_agendamento(db: Session, agendamento: AgendamentosCreate):
    db_agendamento = models.Agendamentos(**agendamento.model_dump())
    db.add(db_agendamento)
    db.commit()
    db.refresh(db_agendamento)
    return db_agendamento


def update_agendamento(db: Session, id: int, agendamento: AgendamentosUpdate):
    db_agendamento = (
        db.query(models.Agendamentos).filter(models.Agendamentos.id == id).first()
    )
    if db_agendamento:
        for key, value in agendamento.model_dump().items():
            setattr(db_agendamento, key, value)
        db.commit()
        db.refresh(db_agendamento)
    return db_agendamento


def delete_agendamento(db: Session, id: int):
    db_agendamento = (
        db.query(models.Agendamentos).filter(models.Agendamentos.id == id).first()
    )
    if db_agendamento:
        db.delete(db_agendamento)
        db.commit()
    return db_agendamento
