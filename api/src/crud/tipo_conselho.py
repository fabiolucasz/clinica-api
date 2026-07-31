from src.deps.user import SessionDep
from src.models import models
from src.schemas.tipo_conselho import TiposConselhoCreate, TiposConselhoUpdate


def get_tipo_conselho(db: SessionDep):
    return db.query(models.Tipo_conselho).all()


def get_tipo_conselho_by_id(db: SessionDep, id: int):
    return db.query(models.Tipo_conselho).filter(models.Tipo_conselho.id == id).first()


def create_tipo_conselho(db: SessionDep, tipo_conselho: TiposConselhoCreate):
    db_tipo_conselho = models.Tipo_conselho(**tipo_conselho.model_dump())
    db.add(db_tipo_conselho)
    db.commit()
    db.refresh(db_tipo_conselho)
    return db_tipo_conselho


def update_tipo_conselho(db: SessionDep, id: int, tipo_conselho: TiposConselhoUpdate):
    db.query(models.Tipo_conselho).filter(models.Tipo_conselho.id == id).update(
        tipo_conselho.model_dump()
    )
    db.commit()
    return db.query(models.Tipo_conselho).filter(models.Tipo_conselho.id == id).first()


def delete_tipo_conselho(db: SessionDep, id: int):
    db.query(models.Tipo_conselho).filter(models.Tipo_conselho.id == id).delete()
    db.commit()
    return {"message": "Tipo de conselho deletado com sucesso"}
