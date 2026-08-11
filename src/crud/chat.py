from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.models.models import Lead
from src.schemas.chat import LeadCreate


def create_or_update_lead(db: Session, lead_data: LeadCreate) -> Lead:
    existing_lead = db.query(Lead).filter(Lead.whatsapp == lead_data.whatsapp).first()

    if existing_lead:
        existing_lead.name = lead_data.name
        existing_lead.birth_date = lead_data.birth_date
        existing_lead.desired_specialty = lead_data.desired_specialty
        existing_lead.insurance = lead_data.insurance
        existing_lead.status = lead_data.status
        existing_lead.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(existing_lead)
        return existing_lead
    else:
        db_lead = Lead(
            name=lead_data.name,
            whatsapp=lead_data.whatsapp,
            birth_date=lead_data.birth_date,
            desired_specialty=lead_data.desired_specialty,
            insurance=lead_data.insurance,
            status=lead_data.status,
        )
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        return db_lead


def get_lead_by_whatsapp(db: Session, whatsapp: str) -> Lead | None:
    return db.query(Lead).filter(Lead.whatsapp == whatsapp).first()


def get_all_leads(db: Session, skip: int = 0, limit: int = 100) -> list[Lead]:
    return db.query(Lead).offset(skip).limit(limit).all()
