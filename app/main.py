from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import async_get_db, engine
from schemas import DoctorSchema, PatientSchema, ClinicSchema, AppointmentSchema
from models import Doctor, Patient, Base, Clinic, Appointment

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаляет все таблицы (опционально)
        await conn.run_sync(Base.metadata.create_all)  # Создает все таблицы

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()  # Выполняется при старте приложения
    yield
    await engine.dispose()  # Выполняется при завершении работы приложения

app = FastAPI(
    title="MISA Prototype API",
    description="This is an ASGI MISA prototype for a test assignment",
    docs_url="/",
    lifespan=lifespan
)

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

@app.post("/doctors/", response_model=DoctorSchema)
async def create_doctor(doctor: DoctorSchema, db: AsyncSession = Depends(async_get_db)):
    db_doctor = Doctor(name=doctor.name, clinic_id=doctor.clinic_id)
    db.add(db_doctor)
    await db.commit()
    await db.refresh(db_doctor)
    return db_doctor

@app.put("/doctors/{doctor_id}", response_model=DoctorSchema)
async def update_doctor(doctor_id: int, doctor: DoctorSchema, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Doctor).filter(Doctor.id == doctor_id))
    db_doctor = result.scalars().first()
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db_doctor.name = doctor.name
    await db.commit()
    await db.refresh(db_doctor)
    return db_doctor


@app.delete("/doctors/{doctor_id}", response_model=DoctorSchema)
async def delete_doctor(doctor_id: int, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Doctor).filter(Doctor.id == doctor_id))
    db_doctor = result.scalars().first()
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(db_doctor)
    await db.commit()
    return db_doctor
    

@app.get("/patients/{patient_id}", response_model=PatientSchema)
async def read_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    patient = result.scalars().first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.get("/patients/name/{patient_name}", response_model=list[PatientSchema])
async def read_patient_by_name(patient_name: str, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Patient).filter(Patient.name == patient_name))
    patients = result.scalars().all()
    if not patients:
        raise HTTPException(status_code=404, detail="Patient name not found")
    return patients

@app.post("/patients/", response_model=PatientSchema)
async def create_patient(patient: PatientSchema, db: AsyncSession = Depends(async_get_db)):
    db_patient = Patient(name=patient.name, doctor_id=patient.doctor_id)
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    return db_patient

@app.put("/patients/{patient_id}", response_model=PatientSchema)
async def update_patient(patient_id: int, patient: PatientSchema, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    db_patient = result.scalars().first()
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    db_patient.name = patient.name
    db_patient.doctor_id = patient.doctor_id
    await db.commit()
    await db.refresh(db_patient)
    return db_patient


@app.delete("/patients/{patient_id}", response_model=PatientSchema)
async def delete_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    db_patient = result.scalars().first()
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(db_patient)
    await db.commit()
    return db_patient
    

@app.get("/clinics/{clinic_id}", response_model=ClinicSchema)
async def read_clinic(clinic_id: int, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Clinic).filter(Clinic.id == clinic_id))
    clinic = result.scalars().first()
    if clinic is None:
        raise HTTPException(status_code=404 ,detail="Clinic not found")
    return clinic

@app.get("/clinics/name/{clinic_name}", response_model=ClinicSchema)
async def read_clinic_by_name(clinic_name: str, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Clinic).filter(Clinic.name == clinic_name))
    clinics = result.scalars().first()
    if not clinics:
        raise HTTPException(status_code=404, detail="Clinic name not found")
    return clinics

@app.post("/clinics/", response_model=ClinicSchema)
async def create_clinic(clinic: ClinicSchema, db: AsyncSession = Depends(async_get_db)):
    db_clinic = Clinic(name=clinic.name, address=clinic.address)
    db.add(db_clinic)
    await db.commit()
    await db.refresh(db_clinic)
    return db_clinic

@app.put("/clinics/{clinic_id}", response_model=ClinicSchema)
async def update_clinic(clinic_id: int, clinic: ClinicSchema, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Clinic).filter(Clinic.id == clinic_id))
    db_clinic = result.scalars().first()
    if db_clinic is None:
        raise HTTPException(status_code=404, detail="Clinic not found")
    db_clinic.name = clinic.name
    db_clinic.address = clinic.address
    await db.commit()
    await db.refresh(db_clinic)
    return db_clinic

@app.delete("/clinics/{clinic_id}", response_model=ClinicSchema)
async def delete_clinic(clinic_id: int, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Clinic).filter(Clinic.id == clinic_id))
    db_clinic = result.scalars().first()
    if db_clinic is None:
        raise HTTPException(status_code=404, detail="Clinic not found")
    db.delete(db_clinic)
    await db.commit()
    return db_clinic
