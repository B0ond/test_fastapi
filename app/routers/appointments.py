import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import async_get_db
from ..schemas import AppointmentSchema
from ..models import Appointment, Doctor, Patient

router = APIRouter(prefix="/appointemts", tags=["appointemts 📲"])
logger = logging.getLogger(__name__)


async def get_appointment_by_id(db: AsyncSession, appointment_id: int):
    """Получить запись на прием по ID."""
    appointment = await db.get(Appointment, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

async def create_new_appointment(db: AsyncSession, appointment_data):
    """Создать новую запись на прием."""
    doctor = await db.get(Doctor, appointment_data.doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=404,
            detail=f"Doctor with id={appointment_data.doctor_id} not found",
        )

    patient = await db.get(Patient, appointment_data.patient_id)
    if not patient:
        raise HTTPException(
            status_code=404,
            detail=f"Patient with id={appointment_data.patient_id} not found",
        )

    appointment_date_naive = (
        appointment_data.date.replace(tzinfo=None)
        if appointment_data.date.tzinfo is not None
        else appointment_data.date
    )

    db_appointment = Appointment(
        doctor_id=appointment_data.doctor_id,
        patient_id=appointment_data.patient_id,
        date=appointment_date_naive,
    )
    db.add(db_appointment)
    await db.commit()
    await db.refresh(db_appointment)
    return db_appointment

async def update_existing_appointment(db: AsyncSession, appointment_id: int, appointment_data):
    """Обновить существующую запись на прием."""
    db_appointment = await db.get(Appointment, appointment_id)
    if not db_appointment:
        raise HTTPException(
            status_code=404,
            detail=f"Appointment with id={appointment_id} not found",
        )

    if appointment_data.doctor_id != db_appointment.doctor_id:
        doctor = await db.get(Doctor, appointment_data.doctor_id)
        if not doctor:
            raise HTTPException(
                status_code=404,
                detail=f"Doctor with id={appointment_data.doctor_id} not found",
            )

    if appointment_data.patient_id != db_appointment.patient_id:
        patient = await db.get(Patient, appointment_data.patient_id)
        if not patient:
            raise HTTPException(
                status_code=404,
                detail=f"Patient with id={appointment_data.patient_id} not found",
            )

    appointment_date_naive = (
        appointment_data.date.replace(tzinfo=None)
        if appointment_data.date.tzinfo is not None
        else appointment_data.date
    )

    db_appointment.doctor_id = appointment_data.doctor_id
    db_appointment.patient_id = appointment_data.patient_id
    db_appointment.date = appointment_date_naive

    await db.commit()
    await db.refresh(db_appointment)
    return db_appointment

async def delete_appointment_by_id(db: AsyncSession, appointment_id: int):
    """Удалить запись на прием."""
    db_appointment = await db.get(Appointment, appointment_id)
    if not db_appointment:
        raise HTTPException(
            status_code=404,
            detail=f"Appointment with id={appointment_id} not found",
        )

    await db.delete(db_appointment)
    await db.commit()

    logger.info("Appointment with id=%s has been deleted.", appointment_id)
    return {"detail": f"Appointment with id={appointment_id} deleted successfully"}

@router.get("/appointments/", response_model=list[AppointmentSchema]
)
async def get_all_appointments(db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Appointment))
    appointments = result.scalars().all()
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentSchema)
async def read_appointment_by_id(appointment_id: int, db: AsyncSession = Depends(async_get_db)):
    """Получить запись на прием по ID."""
    return await get_appointment_by_id(db, appointment_id)

@router.post("/", response_model=AppointmentSchema)
async def create_appointment(appointment: AppointmentSchema, db: AsyncSession = Depends(async_get_db)):
    """Создать новую запись на прием."""
    return await create_new_appointment(db, appointment)

@router.put("/{appointment_id}", response_model=AppointmentSchema)
async def update_appointment(appointment_id: int, appointment: AppointmentSchema, db: AsyncSession = Depends(async_get_db)):
    """Обновить существующую запись на прием."""
    return await update_existing_appointment(db, appointment_id, appointment)

@router.delete("/{appointment_id}", response_model=dict)
async def delete_appointment(appointment_id: int, db: AsyncSession = Depends(async_get_db)):
    """Удалить запись на прием."""
    return await delete_appointment_by_id(db, appointment_id)
