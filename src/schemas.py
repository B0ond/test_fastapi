from pydantic import BaseModel
from datetime import datetime

class PatientBase(BaseModel):
    name: str
    age: int
    reason: str

class PatientCreate(PatientBase):
    pass

class DoctorBase(BaseModel):
    name: str
    specialization: str
    clinic_id: int

class DoctorCreate(DoctorBase):
    pass

class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    clinic_id: int
    datetime: datetime

class AppointmentCreate(AppointmentBase):
    pass