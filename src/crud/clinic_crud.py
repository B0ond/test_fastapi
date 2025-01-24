from sqlalchemy.orm import Session
from src.models.clinic import Clinic

def create_clinic(db: Session, name: str):
    db_clinic = Clinic(name=name)
    db.add(db_clinic)
    db.commit()
    db.refresh(db_clinic)
    return db_clinic

def get_clinic(db: Session, clinic_id: int):
    return db.query(Clinic).filter(Clinic.id == clinic_id).first()

