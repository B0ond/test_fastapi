from sqlalchemy.orm import Session
from src.models.doctor import Doctor

def create_doctor(db: Session, name: str, specialization: str, clinic_id: int):
    db_doctor = Doctor(name=name, specialization=specialization, clinic_id=clinic_id)
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def get_doctor(db: Session, doctor_id: int):
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()

