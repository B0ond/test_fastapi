from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PatientSchema(BaseModel):
    name: str
    doctor_id: Optional[int]  # Ссылка на доктора, если нужно
    appointment_time: Optional[datetime]  # Время записи пациента

    class Config:
        from_attributes = True  # Поддержка для SQLAlchemy

class DoctorSchema(BaseModel):
    name: str
    clinic_id: Optional[int] = None
    # patients: Optional[List[PatientSchema]] = []
    # appointment_times: Optional[List[datetime]] = []

    class Config:
        from_attributes = True

class ClinicSchema(BaseModel):
    name: str
    address: str
    # doctors: Optional[List[DoctorSchema]] = []
    # patients: Optional[List[PatientSchema]] = []

    class Config:
        from_attributes = True

class AppointmentSchema(BaseModel):
    doctor_id: int
    patient_id: int
    date: datetime  # Время записи
    doctor: Optional[DoctorSchema] = None
    patient: Optional[PatientSchema] = None

    class Config:
        from_attributes = True
