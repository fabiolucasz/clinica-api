from sqlalchemy.orm import Session
from src.models import models
from src.schemas.estados import EstadoCreate, EstadoUpdate

def get_estados(db: Session):
    try:
        return db.query(models.Estados).all()
    except Exception as e:
        print(e)
        return {"message": "Erro ao buscar estados", "error": str(e)}


def get_estado(db: Session, id: int):
    try:
        return db.query(models.Estados).filter(models.Estados.id == id).first()
    except Exception as e:
        print(e)
        return {"message": "Erro ao buscar estado", "error": str(e)}

def create_estado(db: Session, estado: EstadoCreate):
    try:
        db_estado = models.Estados(**estado.model_dump())
        db.add(db_estado)
        db.commit()
        db.refresh(db_estado)
        return db_estado
    except Exception as e:
        print(e)
        return {"message": "Erro ao criar estado", "error": str(e)}

def update_estado(db: Session, id: int, estado: EstadoUpdate):
    try:
        db.query(models.Estados).filter(models.Estados.id == id).update(estado.model_dump())
        db.commit()
        return db.query(models.Estados).filter(models.Estados.id == id).first()
    except Exception as e:
        print(e)
        return {"message": "Erro ao atualizar estado", "error": str(e)}

def delete_estado(db: Session, id: int):
    db.query(models.Estados).filter(models.Estados.id == id).delete()
    db.commit()
    return {"message": "Estado deletado com sucesso"}



