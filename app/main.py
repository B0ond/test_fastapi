from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import async_get_db, engine
from schemas import DoctorSchema, PatientSchema, ClinicSchema, AppointmentSchema
from models import Doctor, Patient, Base, Clinic, Appointment
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаляет все таблицы (что бы не мусорить)
        await conn.run_sync(Base.metadata.create_all)  # Создает все таблицы

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()  # Выполняется при старте приложения
    yield
    await engine.dispose()  # Выполняется при завершении работы приложения

app = FastAPI(
    title="MISA Prototype",
    description="This is an ASGI MISA prototype for a test assignment",
    docs_url="/",
    lifespan=lifespan
)

@app.get("/doctors/{doctor_id}", response_model=DoctorSchema, tags=["doctors"])
async def read_doctor(doctor_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Doctor).filter(Doctor.id == doctor_id))
        doctor = result.scalars().first()
        if doctor is None:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return doctor
    except Exception as e:
        logger.error(f"Error reading doctor with id={doctor_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Doctor with id={doctor_id} not found")


@app.get("/doctors/name/{doctor_name}", response_model=list[DoctorSchema], tags=["doctors"])
async def read_doctor_by_name(doctor_name: str, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Doctor).filter(Doctor.name == doctor_name))
        doctors = result.scalars().all()
        if not doctors:
            raise HTTPException(status_code=404, detail="Doctor name not found")
        return doctors
    except Exception as e:
        logger.error(f"Error reading doctor by name={doctor_name}: {e}")
        raise HTTPException(status_code=404, detail=f"Doctor with name={doctor_name} not found")


@app.post("/doctors/", response_model=DoctorSchema, tags=["doctors"])
async def create_doctor(doctor: DoctorSchema, db: AsyncSession = Depends(async_get_db)):
    try:
        if doctor.clinic_id is not None:
            result = await db.execute(select(Clinic).filter(Clinic.id == doctor.clinic_id))
            clinic = result.scalars().first()
            if clinic is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Clinic with id={doctor.clinic_id} not found"
                )
        db_doctor = Doctor(name=doctor.name, clinic_id=doctor.clinic_id)
        db.add(db_doctor)
        await db.commit()
        await db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        logger.error(f"Error creating doctor: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/doctors/{doctor_id}", response_model=DoctorSchema, tags=["doctors"])
async def update_doctor(doctor_id: int, doctor: DoctorSchema, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Doctor).filter(Doctor.id == doctor_id))
        db_doctor = result.scalars().first()
        if db_doctor is None:
            raise HTTPException(status_code=404, detail="Doctor not found")
        db_doctor.name = doctor.name
        db_doctor.clinic_id = doctor.clinic_id
        await db.commit()
        await db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        logger.error(f"Error updating doctor with id={doctor_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/doctors/{doctor_id}", response_model=dict, tags=["doctors"])
async def delete_doctor(doctor_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Doctor).filter(Doctor.id == doctor_id))
        db_doctor = result.scalars().first()
        if db_doctor is None:
            raise HTTPException(status_code=404, detail="Doctor not found")

        await db.delete(db_doctor)
        await db.commit()

        logger.info(f"Doctor with id={doctor_id} has been deleted.")
        return {"detail": f"Doctor with id={doctor_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting doctor with id={doctor_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.get("/patients/{patient_id}", response_model=PatientSchema, tags=["patients"])
async def read_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Patient).filter(Patient.id == patient_id))
        patient = result.scalars().first()
        if patient is None:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient
    except Exception as e:
        logger.error(f"Error reading patient with id={patient_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Patient with id={patient_id} not found")


@app.get("/patients/name/{patient_name}", response_model=list[PatientSchema], tags=["patients"])
async def read_patient_by_name(patient_name: str, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Patient).filter(Patient.name == patient_name))
        patients = result.scalars().all()
        if not patients:
            raise HTTPException(status_code=404, detail="Patient name not found")
        return patients
    except Exception as e:
        logger.error(f"Error reading patient by name={patient_name}: {e}")
        raise HTTPException(status_code=404, detail=f"Patient with name={patient_name} not found")


@app.post("/patients/", response_model=PatientSchema, tags=["patients"])
async def create_patient(patient: PatientSchema, db: AsyncSession = Depends(async_get_db)):
    try:
        if patient.doctor_id is not None:
            result = await db.execute(select(Doctor).filter(Doctor.id == patient.doctor_id))
            doctor = result.scalars().first()
            if doctor is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Doctor with id={patient.doctor_id} not found"
                )

            if patient.clinic_id is not None and doctor.clinic_id != patient.clinic_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Doctor with id={patient.doctor_id} is not associated with clinic id={patient.clinic_id}"
                )

        db_patient = Patient(
            name=patient.name,
            doctor_id=patient.doctor_id,
            clinic_id=patient.clinic_id if patient.clinic_id else (doctor.clinic_id if patient.doctor_id else None)
        )
        db.add(db_patient)
        await db.commit()
        await db.refresh(db_patient)
        return db_patient
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/patients/{patient_id}", response_model=PatientSchema, tags=["patients"])
async def update_patient(patient_id: int, patient: PatientSchema, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Patient).filter(Patient.id == patient_id))
        db_patient = result.scalars().first()
        if db_patient is None:
            raise HTTPException(status_code=404, detail="Patient not found")

        if patient.doctor_id is not None and patient.doctor_id != db_patient.doctor_id:
            result = await db.execute(select(Doctor).filter(Doctor.id == patient.doctor_id))
            doctor = result.scalars().first()
            if doctor is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Doctor with id={patient.doctor_id} not found"
                )

        if patient.clinic_id is not None and patient.clinic_id != db_patient.clinic_id:
            result = await db.execute(select(Clinic).filter(Clinic.id == patient.clinic_id))
            clinic = result.scalars().first()
            if clinic is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Clinic with id={patient.clinic_id} not found"
                )

        db_patient.name = patient.name
        db_patient.doctor_id = patient.doctor_id
        db_patient.clinic_id = patient.clinic_id
        await db.commit()
        await db.refresh(db_patient)
        return db_patient
    except Exception as e:
        logger.error(f"Error updating patient with id={patient_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/patients/{patient_id}", response_model=dict, tags=["patients"])
async def delete_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Patient).filter(Patient.id == patient_id))
        db_patient = result.scalars().first()
        if db_patient is None:
            raise HTTPException(status_code=404, detail="Patient not found")

        await db.delete(db_patient)
        await db.commit()

        logger.info(f"Patient with id={patient_id} has been deleted.")
        return {"detail": f"Patient with id={patient_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting patient with id={patient_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.get("/clinics/{clinic_id}", response_model=ClinicSchema, tags=["clinics"])
async def read_clinic(clinic_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Clinic).filter(Clinic.id == clinic_id))
        clinic = result.scalars().first()
        if clinic is None:
            raise HTTPException(status_code=404, detail="Clinic not found")
        return clinic
    except Exception as e:
        logger.error(f"Error reading clinic with id={clinic_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Clinic  with id={clinic_id} not found")


@app.get("/clinics/name/{clinic_name}", response_model=ClinicSchema, tags=["clinics"])
async def read_clinic_by_name(clinic_name: str, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Clinic).filter(Clinic.name == clinic_name))
        clinic = result.scalars().first()
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic name not found")
        return clinic
    except Exception as e:
        logger.error(f"Error reading clinic by name={clinic_name}: {e}")
        raise HTTPException(status_code=404, detail=f"Clinic  with name={clinic_name} not found")


@app.post("/clinics/", response_model=ClinicSchema, tags=["clinics"])
async def create_clinic(clinic: ClinicSchema, db: AsyncSession = Depends(async_get_db)):
    try:
        db_clinic = Clinic(name=clinic.name, address=clinic.address)
        db.add(db_clinic)
        await db.commit()
        await db.refresh(db_clinic)
        return db_clinic
    except Exception as e:
        logger.error(f"Error creating clinic: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/clinics/{clinic_id}", response_model=ClinicSchema, tags=["clinics"])
async def update_clinic(clinic_id: int, clinic: ClinicSchema, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Clinic).filter(Clinic.id == clinic_id))
        db_clinic = result.scalars().first()
        if db_clinic is None:
            raise HTTPException(status_code=404, detail="Clinic not found")
        db_clinic.name = clinic.name
        db_clinic.address = clinic.address
        await db.commit()
        await db.refresh(db_clinic)
        return db_clinic
    except Exception as e:
        logger.error(f"Error updating clinic with id={clinic_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/clinics/{clinic_id}", response_model=dict, tags=["clinics"])
async def delete_clinic(clinic_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Clinic).filter(Clinic.id == clinic_id))
        db_clinic = result.scalars().first()
        if db_clinic is None:
            raise HTTPException(status_code=404, detail="Clinic not found")

        await db.delete(db_clinic)
        await db.commit()

        logger.info(f"Clinic with id={clinic_id} has been deleted.")
        return {"detail": f"Clinic with id={clinic_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting clinic with id={clinic_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/appointments/{appointment_id}", response_model=AppointmentSchema, tags=["appointments"])
async def read_appointment(appointment_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Appointment).filter(Appointment.id == appointment_id))
        appointment = result.scalars().first()
        if appointment is None:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment
    except Exception as e:
        logger.error(f"Error reading appointment with id={appointment_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Appointment with id={appointment_id} not found")


@app.post("/appointments/", response_model=AppointmentSchema, tags=["appointments"])
async def create_appointment(appointment: AppointmentSchema, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Doctor).filter(Doctor.id == appointment.doctor_id))
        doctor = result.scalars().first()
        if doctor is None:
            raise HTTPException(
                status_code=404,
                detail=f"Doctor with id={appointment.doctor_id} not found"
            )

        result = await db.execute(select(Patient).filter(Patient.id == appointment.patient_id))
        patient = result.scalars().first()
        if patient is None:
            raise HTTPException(
                status_code=404,
                detail=f"Patient with id={appointment.patient_id} not found"
            )

        if appointment.date.tzinfo is not None:
            appointment_date_naive = appointment.date.replace(tzinfo=None)
        else:
            appointment_date_naive = appointment.date

        db_appointment = Appointment(
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            date=appointment_date_naive
        )
        db.add(db_appointment)
        await db.commit()
        await db.refresh(db_appointment)
        return db_appointment
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.put("/appointments/{appointment_id}", response_model=AppointmentSchema, tags=["appointments"])
async def update_appointment(
    appointment_id: int, 
    appointment: AppointmentSchema, 
    db: AsyncSession = Depends(async_get_db)
):
    try:
        result = await db.execute(select(Appointment).filter(Appointment.id == appointment_id))
        db_appointment = result.scalars().first()
        if db_appointment is None:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with id={appointment_id} not found"
            )

        if appointment.doctor_id != db_appointment.doctor_id:
            result = await db.execute(select(Doctor).filter(Doctor.id == appointment.doctor_id))
            doctor = result.scalars().first()
            if doctor is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Doctor with id={appointment.doctor_id} not found"
                )

        if appointment.patient_id != db_appointment.patient_id:
            result = await db.execute(select(Patient).filter(Patient.id == appointment.patient_id))
            patient = result.scalars().first()
            if patient is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Patient with id={appointment.patient_id} not found"
                )

        if appointment.date.tzinfo is not None:
            appointment_date_naive = appointment.date.replace(tzinfo=None)
        else:
            appointment_date_naive = appointment.date

        db_appointment.doctor_id = appointment.doctor_id
        db_appointment.patient_id = appointment.patient_id
        db_appointment.date = appointment_date_naive

        await db.commit()
        await db.refresh(db_appointment)
        return db_appointment
    except Exception as e:
        logger.error(f"Error updating appointment with id={appointment_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.delete("/appointments/{appointment_id}", response_model=dict, tags=["appointments"])
async def delete_appointment(appointment_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Appointment).filter(Appointment.id == appointment_id))
        db_appointment = result.scalars().first()
        if db_appointment is None:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with id={appointment_id} not found"
            )

        await db.delete(db_appointment)
        await db.commit()

        logger.info(f"Appointment with id={appointment_id} has been deleted.")
        return {"detail": f"Appointment with id={appointment_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting appointment with id={appointment_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
