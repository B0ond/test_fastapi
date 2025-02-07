from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Patient, Doctor, Appointment


async def get_all_patient(db: AsyncSession):
    """Получить список всех Записей к врачу."""
    result = await db.execute(select(Appointment))
    return result.scalars().all()


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


async def update_existing_appointment(
    db: AsyncSession, appointment_id: int, appointment_data
):
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
    return {"detail": f"Appointment with id={appointment_id} deleted successfully"}
