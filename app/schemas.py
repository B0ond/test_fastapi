from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class PatientSchema(BaseModel):
    name: str
    doctor_id: Optional[int]
    clinic_id: Optional[int] = None

    class Config:
        from_attributes = True


class DoctorSchema(BaseModel):
    name: str
    clinic_id: Optional[int] = None

    class Config:
        from_attributes = True


class ClinicSchema(BaseModel):
    name: str
    address: str

    class Config:
        from_attributes = True


class AppointmentSchema(BaseModel):
    doctor_id: int
    patient_id: int
    date: datetime

    class Config:
        from_attributes = True
