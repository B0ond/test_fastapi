from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PatientSchema(BaseModel):
    id: int
    name: str
    doctor_id: Optional[int]  # Ссылка на доктора, если нужно
    appointment_time: Optional[datetime]  # Время записи пациента

    class Config:
        orm_mode = True  # Поддержка для SQLAlchemy

class DoctorSchema(BaseModel):
    id: int
    name: str
    patients: Optional[List[PatientSchema]] = []  # Список пациентов
    appointment_times: Optional[List[datetime]] = []  # Время записей

    class Config:
        orm_mode = True

class ClinicSchema(BaseModel):
    id: int
    name: str
    address: str
    doctors: Optional[List[DoctorSchema]] = []  # Список врачей
    patients: Optional[List[PatientSchema]] = []  # Список пациентов

    class Config:
        orm_mode = True

class AppointmentSchema(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    date: datetime  # Время записи
    doctor: Optional[DoctorSchema] = None  # Доктор
    patient: Optional[PatientSchema] = None  # Пациент

    class Config:
        orm_mode = True
