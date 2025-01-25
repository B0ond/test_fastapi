from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
# from sqlalchemy.orm import Session
from database import async_get_db
from schemas import DoctorSchema, PatientSchema, ClinicSchema, AppointmentSchema
from models import Doctor, Patient, Clinic, Appointment
import asyncpg

app = FastAPI(
    title="MISA prototipe API",
    description="This is a asgi MISA prototype for a test assignment",
    docs_url="/"
)

# шаблон
# @app.get("/doctors{doctors_id}", response_model=DoctorSchema)
# async def read_doctor(doctors_id: int, db: Sessions = Depends(get_db)):
#     doctor = db.query(Doctor).filter(Doctor.id == doctors_id).first()
#     if doctor is None:
#         raise HTTPException(status_code=404, detail="Doctor not found")
#     return doctor

@app.get("/doctors/{doctor_id}", response_model=DoctorSchema)
async def read_doctor(doctor_id: int, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Doctor).filter(Doctor.id == doctor_id))
    doctor = result.scalars().first()
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@app.get("/doctors/name/{doctor_name}", response_model=list[DoctorSchema])
async def read_doctor_by_name(doctor_name: str, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Doctor).filter(Doctor.name == doctor_name))
    doctors = result.scalars().all()
    if not doctors:
        raise HTTPException(status_code=404, detail="Doctor name not found")
    return doctors


@app.post("/doctors/{doctor_id}", response_model=DoctorSchema)
async def create_doctor(doctor: DoctorSchema, db: AsyncSession = Depends(async_get_db)):
    db_doctor = Doctor(name=doctor.name)
    db.add(db_doctor)
    await db.commit()
    await db.refresh(db_doctor)
    return db_doctor

@app.put("/doctors/{doctor_id}", response_model=DoctorSchema)
async def update_doctor(doctor_id: int, doctor: DoctorSchema, db: AsyncSession=
                        Depends(async_get_db)):
    result = await db.execute(select(Doctor).filter(Doctor.id == doctor_id))
    db_doctor = result.scalars().first()
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db_doctor.name=doctor.name
    await db.commit()
    await db.refresh(db_doctor)
    return db_doctor



@app.get("/patients/{patient_id}", response_model=PatientSchema)
async def read_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    patient = result.scalars().first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.get("/patietns/name/{patient_name}", response_model=list[PatientSchema])
async def read_patient_by_name(patient_name: str, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Patient).filter(Patient.name == patient_name))
    patient = result.scalars().first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient name not found")
    return patient

@app.post("/patients/{patients_id}", response_model=PatientSchema)
async def create_patient(patient: PatientSchema, db: AsyncSession = Depends(async_get_db)):
    db_patient = Patient(name=patient.name)
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    return db_patient

















# @app.get("/clinics/{clinic_id}", response_model=ClinicSchema)
# async def read_clinic(clinic_id: int, db: Session = Depends(async_get_db)):
#     clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
#     if clinic is None:
#         raise HTTPException(status_code=404, detail="Clinic not found")
#     return clinic

# @app.get("/appointments/{appointment_id}", response_model=AppointmentSchema)
# async def read_appointment(appointment_id: int, db: Session = Depends(async_get_db)):
#     appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
#     if appointment is None:
#         raise HTTPException(status_code=404, detail="Appointment not found")
#     return appointment
