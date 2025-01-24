from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.___models import Patient, Doctor, Appointment
from src.schemas import PatientCreate, DoctorCreate, AppointmentCreate

async def get_patients(session: AsyncSession):
    result = await session.execute(select(Patient))
    return result.scalars().all()

async def create_patient(session: AsyncSession, patient: PatientCreate):
    new_patient = Patient(**patient.dict())
    session.add(new_patient)
    await session.commit()
    return new_patient

async def get_doctors(session: AsyncSession):
    result = await session.execute(select(Doctor))
    return result.scalars().all()

async def create_doctor(session: AsyncSession, doctor: DoctorCreate):
    new_doctor = Doctor(**doctor.dict())
    session.add(new_doctor)
    await session.commit()
    return new_doctor

async def create_appointment(session: AsyncSession, appointment: AppointmentCreate):
    new_appointment = Appointment(**appointment.dict())
    session.add(new_appointment)
    await session.commit()
    return new_appointment

async def get_appointments(session: AsyncSession):
    result = await session.execute(select(Appointment))
    return result.scalars().all()