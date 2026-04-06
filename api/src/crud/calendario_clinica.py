from sqlalchemy.orm import Session
from src.models import models
from src.schemas.calendario_clinica import CalendarioClinicaCreate, CalendarioClinicaUpdate

def get_calendario_clinica(db: Session):
    results = db.query(models.CalendarioClinica, models.Calendario.data_br)\
        .join(models.Calendario, models.CalendarioClinica.data_feriado == models.Calendario.id)\
        .all()
    
    return [
        {
            "id": calendario_clinica.id,
            "clinica_id": calendario_clinica.clinica_id,
            "data_feriado": calendario_clinica.data_feriado,
            "data_br": data_br,
            "nome_feriado": calendario_clinica.nome_feriado,
            "aberta": calendario_clinica.aberta
        }
        for calendario_clinica, data_br in results
    ]

def get_calendario_clinica_by_clinica(db: Session, clinica_id: int):
    results = db.query(models.CalendarioClinica, models.Calendario.data_br)\
        .join(models.Calendario, models.CalendarioClinica.data_feriado == models.Calendario.id)\
        .filter(models.CalendarioClinica.clinica_id == clinica_id)\
        .all()
    
    return [
        {
            "id": calendario_clinica.id,
            "clinica_id": calendario_clinica.clinica_id,
            "data_feriado": calendario_clinica.data_feriado,
            "data_br": data_br,
            "nome_feriado": calendario_clinica.nome_feriado,
            "aberta": calendario_clinica.aberta
        }
        for calendario_clinica, data_br in results
    ]

def get_calendario_clinica_by_data(db: Session, data: str):
    results = db.query(models.CalendarioClinica, models.Calendario.data_br)\
        .join(models.Calendario, models.CalendarioClinica.data_feriado == models.Calendario.id)\
        .filter(models.Calendario.data_br == data)\
        .all()
    
    return [
        {
            "id": calendario_clinica.id,
            "clinica_id": calendario_clinica.clinica_id,
            "data_feriado": calendario_clinica.data_feriado,
            "data_br": data_br,
            "nome_feriado": calendario_clinica.nome_feriado,
            "aberta": calendario_clinica.aberta
        }
        for calendario_clinica, data_br in results
    ]

def create_calendario_clinica(db: Session, calendario_clinica: CalendarioClinicaCreate):
    db_calendario_clinica = models.CalendarioClinica(**calendario_clinica.model_dump())
    db.add(db_calendario_clinica)
    db.commit()
    db.refresh(db_calendario_clinica)
    return db_calendario_clinica

def update_calendario_clinica(db: Session, id: int, calendario_clinica: CalendarioClinicaUpdate):
    db_calendario_clinica = db.query(models.CalendarioClinica).filter(models.CalendarioClinica.id == id).first()
    if db_calendario_clinica:
        for key, value in calendario_clinica.model_dump().items():
            setattr(db_calendario_clinica, key, value)
        db.commit()
        db.refresh(db_calendario_clinica)
        return db_calendario_clinica
    return None

def delete_calendario_clinica(db: Session, id: int):
    db_calendario_clinica = db.query(models.CalendarioClinica).filter(models.CalendarioClinica.id == id).first()
    if db_calendario_clinica:
        db.delete(db_calendario_clinica)
        db.commit()
        return True
    return False
