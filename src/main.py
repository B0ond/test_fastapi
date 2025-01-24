"""for work"""

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, Base, get_session
from src.models.___models import Patient, Doctor, Clinic, Appointment
from schemas import PatientCreate, DoctorCreate, AppointmentCreate
from crud import (get_patients, create_patient, get_doctors, create_doctor,
                      create_appointment, get_appointments)

async def startup_lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(lifespan=startup_lifespan)

@app.get("/patients/")
async def list_patients(session: AsyncSession = Depends(get_session)):
    return await get_patients(session)

@app.post("/patients/")
async def add_patient(patient: PatientCreate, session: AsyncSession = Depends(get_session)):
    return await create_patient(session, patient)

@app.get("/doctors/")
async def list_doctors(session: AsyncSession = Depends(get_session)):
    return await get_doctors(session)

@app.post("/doctors/")
async def add_doctor(doctor: DoctorCreate, session: AsyncSession = Depends(get_session)):
    return await create_doctor(session, doctor)

@app.post("/appointments/")
async def add_appointment(appointment: AppointmentCreate, session: AsyncSession = Depends(get_session)):
    return await create_appointment(session, appointment)

@app.get("/appointments/")
async def list_appointments(session: AsyncSession = Depends(get_session)):
    return await get_appointments(session)
