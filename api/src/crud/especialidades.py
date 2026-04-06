
from src.deps.user import SessionDep
from src.schemas.especialidades import EspecialidadesCreate, EspecialidadesUpdate
from src.models import models

def get_especialidades(db: SessionDep):
    return db.query(models.Especialidades).all()

def get_especialidade(db: SessionDep, id: int):
    return db.query(models.Especialidades).filter(models.Especialidades.id == id).first()

def create_especialidade(db: SessionDep, especialidade: EspecialidadesCreate):
    db_especialidade = models.Especialidades(**especialidade.model_dump())
    db.add(db_especialidade)
    db.commit()
    db.refresh(db_especialidade)
    return db_especialidade

def update_especialidade(db: SessionDep, id: int, especialidade: EspecialidadesUpdate):
    db.query(models.Especialidades).filter(models.Especialidades.id == id).update(especialidade.model_dump())
    db.commit()
    return db.query(models.Especialidades).filter(models.Especialidades.id == id).first()

def delete_especialidade(db: SessionDep, id: int):
    db.query(models.Especialidades).filter(models.Especialidades.id == id).delete()
    db.commit()
    return {"message": "Especialidade deletada com sucesso"}
